"""Application configuration loaded from environment variables."""

import logging
import secrets
from functools import lru_cache
from pathlib import Path
from typing import Literal
from urllib.parse import quote

from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

# Environment names that enable developer conveniences (ephemeral JWT secret,
# permissive CORS). Anything else is treated as production and fails closed.
_DEVELOPMENT_ENVIRONMENTS = {"development", "dev", "local"}

# An HS256 key shorter than the HMAC block size is brute-forceable offline once
# a single token leaks, so refuse anything below 32 characters.
_MIN_JWT_SECRET_LENGTH = 32

# Values that have shipped as documentation placeholders and must never be
# accepted as a real secret, even if they are long enough.
_REJECTED_SECRETS = frozenset(
    {
        "change-me",
        "changeme",
        "change-me-in-production",
        "change-me-in-production-please-use-a-long-random-secret",
        "secret",
        "changethis",
        "please-change-me",
    }
)


class Settings(BaseSettings):
    """Central application settings.

    Values are loaded from environment variables and an optional ``.env`` file.
    Field names map to uppercase env vars (e.g. ``app_name`` → ``APP_NAME``).
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "LegalLink"
    app_env: str = "development"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    log_level: str = "INFO"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # CORS: comma-separated exact origins (scheme + host + port), e.g.
    # "https://app.example.com,https://admin.example.com". Credentialed
    # requests are only enabled when an explicit allowlist is configured,
    # because "*" plus cookies is both spec-invalid and origin-reflecting.
    cors_allow_origins: str = ""

    # Database. The password has no default on purpose: a fallback baked into
    # source is a hard-coded credential (CWE-798) and silently becomes the
    # production password whenever POSTGRES_PASSWORD is forgotten.
    postgres_user: str = "legallink"
    postgres_password: SecretStr = SecretStr("")
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "legallink"

    # Document storage
    storage_path: str = "storage/documents"
    generated_storage_path: str = "storage/generated"
    brand_logo_path: str = "../frontend/public/logo.png"
    max_upload_size_mb: int = 25
    allowed_mime_types: str = "application/pdf"

    # OCR / extraction pipeline (tuned for low-RAM hosts)
    ocr_enabled: bool = True
    ocr_lang: str = "en"  # PaddleOCR: en | french | arabic | ...
    ocr_min_chars_per_page: int = 30
    # Lower scale = less RAM / faster CPU OCR on scanned A4 pages.
    ocr_render_scale: float = 1.0
    # Cap longest pixmap side (px) before OCR to avoid huge bitmaps.
    ocr_max_image_side: int = 1280
    # Angle classifier doubles model memory; disable on low-RAM machines.
    ocr_use_angle_cls: bool = False
    # First OCR run may download Paddle models; keep a generous timeout.
    ocr_timeout_seconds: int = 1800

    # Chunking (RAG preprocessing)
    chunk_size: int = 900
    chunk_overlap: int = 175

    # Semantic indexing (pgvector + embeddings)
    embedding_model: str = "BAAI/bge-m3"
    embedding_fallback_model: str = "intfloat/multilingual-e5-large"
    embedding_dimension: int = 1024
    embedding_batch_size: int = 2
    embedding_cache_dir: str = "~/.cache/fastembed"
    auto_index_on_process: bool = True

    # Semantic retrieval (pgvector cosine Top-K)
    retrieval_top_k: int = 5
    # Candidate pool size before CrossEncoder reranking
    retrieval_candidate_k: int = 15

    # CrossEncoder reranking
    reranker_model: str = "BAAI/bge-reranker-v2-m3"
    reranker_fallback_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    reranker_final_k: int = 5
    reranker_cache_dir: str = "~/.cache/fastembed"

    # Library-wide ("all documents") retrieval coverage. When no single document
    # is selected, plain Top-K concentrates on whichever document has the most
    # matching chunks. To span the whole library we widen the candidate pool and
    # cap how many chunks any single document may contribute to the final context.
    multi_doc_candidate_k: int = 40  # candidate pool when scanning all documents
    multi_doc_final_k: int = 8  # chunks kept for the LLM in all-documents mode
    multi_doc_per_document_cap: int = 2  # max chunks from one doc before diversifying

    # LLM / RAG generation (OpenAI-compatible: openai | nvidia_nim | groq | openrouter)
    llm_provider: str = "openai"
    # Generic key used as a fallback for every provider. Provider-specific keys
    # below take precedence, so switching provider only requires setting its key.
    llm_api_key: str = ""
    llm_model: str = ""
    llm_base_url: str = ""
    llm_temperature: float = 0.1
    llm_max_tokens: int = 1024
    # Specialist analyses are intentionally more exhaustive than normal chat.
    agent_max_tokens: int = 8192
    # The multi-agent synthesis cross-references the three specialist analyses,
    # so it needs the most room of any single completion to avoid truncation.
    synthesis_max_tokens: int = 12000
    # Extra completion rounds allowed to finish a synthesis that hit the token
    # limit (continuation). 0 disables continuation (only flag truncation).
    synthesis_max_continuations: int = 2
    # Clause-by-clause two-contract comparison. The combined prompt splits this
    # character budget equally between version A and version B.
    comparison_context_chars: int = 180000
    comparison_max_tokens: int = 12000
    # Completion budget for the document-generation mode (full HTML reports:
    # per-article analysis + recommendations + risk-score note). Much larger than
    # a chat reply so long reports are not truncated mid-section.
    document_max_tokens: int = 16000
    # Extra completion rounds allowed to finish a report that hit the token limit
    # (continuation). 0 disables continuation (only detect + flag truncation).
    document_max_continuations: int = 3
    llm_timeout_seconds: float = 300.0

    # Provider-specific API keys (optional). When set, they take precedence over
    # ``llm_api_key`` for the matching ``llm_provider``. This makes provider
    # onboarding config-only: e.g. tomorrow set OPENROUTER_API_KEY and
    # LLM_PROVIDER=openrouter — no code changes required.
    openai_api_key: str = ""
    groq_api_key: str = ""
    nvidia_api_key: str = ""
    openrouter_api_key: str = ""
    # OpenRouter attribution headers (optional, recommended by OpenRouter).
    openrouter_referer: str = ""
    openrouter_title: str = "LegalLink"

    # LLM reliability: bounded exponential-backoff retries for *transient*
    # failures only (timeouts, 429 rate limits, 5xx). Permanent errors
    # (auth/4xx/missing key) are never retried.
    llm_max_retries: int = 2
    llm_retry_base_delay_seconds: float = 1.0

    rag_max_context_chars: int = 12000
    # Full-document analysis mode (see GeneratorService.generate_document): when a
    # report is requested for a single document we send the WHOLE contract (all
    # chunks ordered by chunk_index) instead of a Top-K similarity slice, so no
    # article is silently dropped. This is the per-LLM-call context budget (chars);
    # a large window (Claude/OpenRouter handle ~200K tokens) means realistic
    # contracts fit in one call. Documents larger than this are processed in
    # ordered batches (map) and then synthesised into the final report (reduce).
    full_document_context_chars: int = 200000
    # Soft size cap for agent default/global analyses that use full-document
    # retrieval. Above this character count we fall back to Top-K with an
    # elevated final_k, so a very large contract does not blow LLM cost/latency.
    agent_full_document_max_chars: int = 80000
    # final_k used when the full-document agent path falls back to Top-K.
    agent_full_document_fallback_final_k: int = 20
    rag_no_answer_message: str = (
        "I cannot answer this question based on the uploaded documents."
    )

    # Conversation memory (recent turns injected into the prompt)
    conversation_history_limit: int = 10

    # Background processing (Redis + Celery)
    redis_url: str = "redis://localhost:6379/0"
    # Celery broker / result backend default to REDIS_URL when left empty.
    celery_broker_url: str = ""
    celery_result_backend: str = ""
    # TTL (seconds) for ingestion progress entries stored in Redis.
    ingestion_progress_ttl_seconds: int = 60 * 60 * 24  # 24h
    # TTL for reconnectable chat/agent jobs and their streamed event history.
    chat_job_ttl_seconds: int = 60 * 60 * 24  # 24h

    # Authentication (JWT). JWT_SECRET must come from the environment. Outside
    # development a missing or placeholder value aborts startup; in development
    # a random per-process secret is generated so tokens are never signed with
    # a key an attacker can read in the repository.
    jwt_secret: SecretStr = SecretStr("")
    jwt_algorithm: Literal["HS256", "HS384", "HS512"] = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24h

    # Observability — Langfuse tracing (optional; disabled by default).
    # When disabled (or the SDK/keys are missing) the app runs normally and
    # every node simply executes without emitting traces.
    langfuse_enabled: bool = False
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "https://cloud.langfuse.com"
    # Optional grouping tags attached to every trace.
    langfuse_release: str = ""
    langfuse_environment: str = ""
    # Capture full text payloads (documents, chunks, answers) in traces instead
    # of compact size/preview summaries. Off by default for confidentiality.
    langfuse_capture_full_io: bool = False

    @model_validator(mode="after")
    def _expand_cache_paths(self) -> "Settings":
        """Resolve ``~`` in cache directories.

        The model caches used to be pinned to ``/root/.cache``, which is not
        writable now that the container runs as an unprivileged user. Consumers
        hand these straight to fastembed, which does not expand ``~`` itself.
        """
        self.embedding_cache_dir = str(Path(self.embedding_cache_dir).expanduser())
        self.reranker_cache_dir = str(Path(self.reranker_cache_dir).expanduser())
        return self

    @model_validator(mode="after")
    def _enforce_secret_hygiene(self) -> "Settings":
        """Reject missing/placeholder credentials before the app can serve traffic."""
        password = self.postgres_password.get_secret_value()
        if not password:
            raise ValueError(
                "POSTGRES_PASSWORD is not set. Configure it in the environment "
                "(see backend/.env.example) — there is no built-in default."
            )

        secret = self.jwt_secret.get_secret_value()
        if secret.strip().lower() in _REJECTED_SECRETS or len(secret) < _MIN_JWT_SECRET_LENGTH:
            if not self.is_development:
                raise ValueError(
                    "JWT_SECRET is missing, a known placeholder, or shorter than "
                    f"{_MIN_JWT_SECRET_LENGTH} characters. Generate one with "
                    "`python -c \"import secrets; print(secrets.token_urlsafe(48))\"` "
                    "and set JWT_SECRET in the environment."
                )
            self.jwt_secret = SecretStr(secrets.token_urlsafe(48))
            logger.warning(
                "JWT_SECRET is unset or too weak; generated an ephemeral development "
                "secret. Every restart invalidates all issued tokens — set JWT_SECRET "
                "in backend/.env to keep sessions stable."
            )

        return self

    @property
    def cors_allow_origin_list(self) -> list[str]:
        """Exact origins allowed by CORS, in priority order of configuration.

        An explicit allowlist always wins. With nothing configured, development
        falls back to the local Vite dev servers and production allows nothing.
        """
        configured = [item.strip() for item in self.cors_allow_origins.split(",") if item.strip()]
        if configured:
            return configured
        if self.is_development:
            return [
                "http://localhost:5173",
                "http://127.0.0.1:5173",
                "http://localhost:4173",
                "http://127.0.0.1:4173",
            ]
        return []

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024

    @property
    def allowed_mime_type_set(self) -> set[str]:
        return {item.strip() for item in self.allowed_mime_types.split(",") if item.strip()}

    def _database_url(self, driver: str) -> str:
        """Build a DSN with percent-encoded credentials.

        Encoding matters for correctness and safety: an unescaped ``@``, ``/``
        or ``#`` in a strong password would otherwise reshape the URL and point
        the client at a different host or database.
        """
        user = quote(self.postgres_user, safe="")
        password = quote(self.postgres_password.get_secret_value(), safe="")
        return (
            f"postgresql+{driver}://{user}:{password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # Plain properties rather than computed fields: a computed field is emitted
    # by model_dump()/model_dump_json(), which would print the password anywhere
    # settings get serialised for debugging.
    @property
    def database_url(self) -> str:
        """Async SQLAlchemy connection URL (asyncpg)."""
        return self._database_url("asyncpg")

    @property
    def database_url_sync(self) -> str:
        """Sync SQLAlchemy connection URL (psycopg2) used by Alembic."""
        return self._database_url("psycopg2")

    @property
    def is_development(self) -> bool:
        return self.app_env.lower() in _DEVELOPMENT_ENVIRONMENTS

    @property
    def effective_celery_broker_url(self) -> str:
        return self.celery_broker_url or self.redis_url

    @property
    def effective_celery_result_backend(self) -> str:
        return self.celery_result_backend or self.redis_url


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
