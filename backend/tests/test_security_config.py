"""Regression tests for credential handling, CORS scope and JWT validation."""

import base64
import json
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from app.core.config import Settings
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)

_STRONG_SECRET = "z" * 48


def _settings(**overrides: object) -> Settings:
    """Build Settings from explicit values only, ignoring .env and the process env."""
    base: dict[str, object] = {
        "postgres_password": "unit-test-password",
        "jwt_secret": _STRONG_SECRET,
    }
    base.update(overrides)
    return Settings(_env_file=None, **base)  # type: ignore[arg-type]


# --- Credentials must come from the environment ------------------------------

def test_postgres_password_has_no_built_in_default() -> None:
    """An empty database password is rejected instead of falling back to a literal."""
    with pytest.raises(ValidationError, match="POSTGRES_PASSWORD"):
        _settings(postgres_password="")


@pytest.mark.parametrize(
    "secret",
    [
        "",
        "change-me",
        "change-me-in-production-please-use-a-long-random-secret",
        "short",
    ],
)
def test_production_rejects_missing_or_placeholder_jwt_secret(secret: str) -> None:
    """Outside development a weak signing key aborts startup."""
    with pytest.raises(ValidationError, match="JWT_SECRET"):
        _settings(app_env="production", jwt_secret=secret)


def test_development_generates_ephemeral_jwt_secret() -> None:
    """Development stays usable without a configured secret, but never a shared one."""
    first = _settings(app_env="development", jwt_secret="")
    second = _settings(app_env="development", jwt_secret="")

    generated = first.jwt_secret.get_secret_value()
    assert len(generated) >= 32
    assert generated != second.jwt_secret.get_secret_value()


def test_database_url_percent_encodes_credentials() -> None:
    """A password containing URL syntax cannot redirect the connection."""
    settings = _settings(
        postgres_user="user@corp",
        postgres_password="p@ss/w:rd#1",
        postgres_host="db.internal",
        postgres_db="legallink",
    )

    assert settings.database_url == (
        "postgresql+asyncpg://user%40corp:p%40ss%2Fw%3Ard%231@db.internal:5432/legallink"
    )
    assert "p@ss/w:rd#1" not in settings.database_url


def test_database_url_is_not_serialised_with_the_model() -> None:
    """model_dump() must not expose the password through a computed field."""
    dumped = _settings().model_dump()

    assert "database_url" not in dumped
    assert "unit-test-password" not in json.dumps(dumped, default=str)


# --- CORS --------------------------------------------------------------------

def test_cors_never_returns_a_wildcard() -> None:
    """Credentialed CORS requires exact origins; "*" would reflect any origin."""
    assert "*" not in _settings(app_env="development").cors_allow_origin_list
    assert _settings(app_env="production").cors_allow_origin_list == []


def test_cors_uses_the_configured_allowlist() -> None:
    settings = _settings(
        app_env="production",
        cors_allow_origins="https://app.example.com, https://admin.example.com",
    )

    assert settings.cors_allow_origin_list == [
        "https://app.example.com",
        "https://admin.example.com",
    ]


# --- JWT ---------------------------------------------------------------------

def _b64url(payload: dict) -> str:
    raw = json.dumps(payload, separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def test_token_round_trip() -> None:
    settings = _settings()
    with patch("app.core.security.get_settings", return_value=settings):
        token = create_access_token("user-1", extra_claims={"role": "admin"})
        payload = decode_access_token(token)

    assert payload is not None
    assert payload["sub"] == "user-1"
    assert payload["role"] == "admin"


def test_extra_claims_cannot_override_registered_claims() -> None:
    """A caller-supplied claim must not rewrite the subject or the expiry."""
    settings = _settings()
    with patch("app.core.security.get_settings", return_value=settings):
        token = create_access_token(
            "user-1", extra_claims={"sub": "attacker", "exp": 9999999999}
        )
        payload = decode_access_token(token)

    assert payload is not None
    assert payload["sub"] == "user-1"
    assert payload["exp"] < 9999999999


def test_alg_none_header_is_rejected() -> None:
    """An unsigned token must not be accepted even if the rest is well-formed."""
    settings = _settings()
    forged = f"{_b64url({'alg': 'none', 'typ': 'JWT'})}.{_b64url({'sub': 'attacker', 'exp': 9999999999})}."

    with patch("app.core.security.get_settings", return_value=settings):
        assert decode_access_token(forged) is None


def test_algorithm_downgrade_is_rejected() -> None:
    """The header alg is pinned to the configured algorithm before verification."""
    signing_settings = _settings(jwt_algorithm="HS512")
    verifying_settings = _settings(jwt_algorithm="HS256")

    with patch("app.core.security.get_settings", return_value=signing_settings):
        token = create_access_token("user-1")

    with patch("app.core.security.get_settings", return_value=verifying_settings):
        assert decode_access_token(token) is None


def test_token_signed_with_another_secret_is_rejected() -> None:
    with patch("app.core.security.get_settings", return_value=_settings(jwt_secret="a" * 48)):
        token = create_access_token("user-1")

    with patch("app.core.security.get_settings", return_value=_settings(jwt_secret="b" * 48)):
        assert decode_access_token(token) is None


def test_tampered_payload_is_rejected() -> None:
    settings = _settings()
    with patch("app.core.security.get_settings", return_value=settings):
        token = create_access_token("user-1")
        header_b64, _, signature_b64 = token.split(".")
        forged = ".".join(
            [header_b64, _b64url({"sub": "attacker", "exp": 9999999999}), signature_b64]
        )

        assert decode_access_token(forged) is None


@pytest.mark.parametrize(
    "token",
    ["", "not-a-token", "a.b", "a.b.c.d", "x" * 9000, "éé.éé.éé", "a.\udcff.c"],
)
def test_malformed_tokens_are_rejected(token: str) -> None:
    """Garbage input is rejected rather than raising out of the decoder."""
    with patch("app.core.security.get_settings", return_value=_settings()):
        assert decode_access_token(token) is None


def test_expired_token_is_rejected() -> None:
    settings = _settings()
    with patch("app.core.security.get_settings", return_value=settings):
        token = create_access_token("user-1", expires_minutes=-1)
        assert decode_access_token(token) is None


# --- Password hashing --------------------------------------------------------

def test_password_hash_is_salted_and_verifiable() -> None:
    first = hash_password("correct horse battery staple")
    second = hash_password("correct horse battery staple")

    assert first != second, "each hash must use a fresh salt"
    assert "correct horse battery staple" not in first
    assert verify_password("correct horse battery staple", first)
    assert not verify_password("wrong password", first)


@pytest.mark.parametrize("stored", ["", "not-a-hash", "bcrypt$1$salt$hash", "a$b$c"])
def test_verify_password_rejects_unusable_hashes(stored: str) -> None:
    assert not verify_password("anything", stored)
