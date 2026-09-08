"""Authentication primitives: password hashing and JWT (stdlib only).

Kept dependency-free (no passlib / python-jose) so the container does not need
to be rebuilt. Password hashing uses PBKDF2-HMAC-SHA256; tokens use HS256 JWT.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time
from typing import Any

from app.core.config import get_settings

_PBKDF2_ITERATIONS = 240_000
_PBKDF2_ALGO = "pbkdf2_sha256"

# HMAC digest backing each supported JWT "alg". Only these are ever accepted,
# so a token cannot downgrade itself to "none" or to a weaker primitive.
_JWT_DIGESTS = {
    "HS256": hashlib.sha256,
    "HS384": hashlib.sha384,
    "HS512": hashlib.sha512,
}

# Reject oversized tokens before doing any parsing work.
_MAX_TOKEN_LENGTH = 8192


# --- Password hashing --------------------------------------------------------

def hash_password(password: str) -> str:
    """Return a self-describing PBKDF2 hash: ``pbkdf2_sha256$iters$salt$hash``."""
    salt = secrets.token_bytes(16)
    derived = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, _PBKDF2_ITERATIONS
    )
    return (
        f"{_PBKDF2_ALGO}${_PBKDF2_ITERATIONS}"
        f"${base64.b64encode(salt).decode()}${base64.b64encode(derived).decode()}"
    )


def verify_password(password: str, stored: str) -> bool:
    """Constant-time verification of a password against a stored PBKDF2 hash."""
    try:
        algo, iters_s, salt_b64, hash_b64 = stored.split("$")
        if algo != _PBKDF2_ALGO:
            return False
        iterations = int(iters_s)
        salt = base64.b64decode(salt_b64)
        expected = base64.b64decode(hash_b64)
    except (ValueError, TypeError):
        return False

    derived = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, iterations
    )
    return hmac.compare_digest(derived, expected)


# --- JWT (HMAC) --------------------------------------------------------------

def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def _sign(algorithm: str, signing_input: bytes) -> bytes:
    """HMAC ``signing_input`` with the configured secret for ``algorithm``."""
    digest = _JWT_DIGESTS.get(algorithm)
    if digest is None:
        raise ValueError(f"Unsupported JWT algorithm: {algorithm!r}")
    secret = get_settings().jwt_secret.get_secret_value().encode("utf-8")
    return hmac.new(secret, signing_input, digest).digest()


def create_access_token(
    subject: str,
    *,
    extra_claims: dict[str, Any] | None = None,
    expires_minutes: int | None = None,
) -> str:
    """Create a signed JWT for ``subject`` (typically the user id)."""
    settings = get_settings()
    ttl = expires_minutes or settings.access_token_expire_minutes
    now = int(time.time())
    header = {"alg": settings.jwt_algorithm, "typ": "JWT"}
    payload: dict[str, Any] = dict(extra_claims or {})
    # Registered claims are written last so a caller-supplied claim can never
    # rewrite the subject or extend the lifetime of the token.
    payload.update({"sub": subject, "iat": now, "exp": now + ttl * 60})

    segments = [
        _b64url_encode(json.dumps(header, separators=(",", ":")).encode()),
        _b64url_encode(json.dumps(payload, separators=(",", ":")).encode()),
    ]
    signing_input = ".".join(segments).encode("ascii")
    segments.append(_b64url_encode(_sign(settings.jwt_algorithm, signing_input)))
    return ".".join(segments)


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Validate header, signature and expiry; return the payload or ``None``.

    The header ``alg`` is pinned to the configured algorithm before the
    signature is checked, so an attacker cannot swap in ``none`` or a weaker
    algorithm and have the claims trusted.
    """
    settings = get_settings()
    # A JWT is ASCII by construction. Checking up front keeps a header with
    # stray high bytes from raising out of the ascii encode further down, which
    # would surface as a 500 instead of a plain rejection.
    if not token or len(token) > _MAX_TOKEN_LENGTH or not token.isascii():
        return None

    try:
        header_b64, payload_b64, signature_b64 = token.split(".")
    except ValueError:
        return None

    try:
        header = json.loads(_b64url_decode(header_b64))
    except (ValueError, TypeError):
        return None
    if not isinstance(header, dict) or header.get("alg") != settings.jwt_algorithm:
        return None

    signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
    expected_sig = _sign(settings.jwt_algorithm, signing_input)
    try:
        provided_sig = _b64url_decode(signature_b64)
    except (ValueError, TypeError):
        return None
    if not hmac.compare_digest(expected_sig, provided_sig):
        return None

    try:
        payload = json.loads(_b64url_decode(payload_b64))
    except (ValueError, TypeError):
        return None
    if not isinstance(payload, dict):
        return None

    try:
        expires_at = int(payload["exp"])
    except (KeyError, TypeError, ValueError):
        return None
    if expires_at < int(time.time()):
        return None
    return payload
