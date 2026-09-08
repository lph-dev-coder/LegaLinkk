# syntax=docker/dockerfile:1

# Pin Bookworm: current python:3.12-slim (Trixie/glibc 2.41) segfaults on
# `import paddle` with official paddlepaddle CPU wheels.
FROM python:3.12-slim-bookworm AS base

# Unprivileged runtime identity. A fixed high UID/GID keeps host bind-mount
# ownership predictable and never collides with a real host account.
ARG APP_UID=10001
ARG APP_GID=10001
ARG APP_USER=appuser
ARG APP_HOME=/home/appuser

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # Must be able to read poetry.lock's format (lock-version 2.1). Poetry 1.8
    # only warns and then guesses, which risks installing something other than
    # the pinned, patched versions.
    POETRY_VERSION=2.2.1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1 \
    FLAGS_use_mkldnn=0 \
    FLAGS_enable_pir_api=0 \
    FLAGS_enable_pir_in_executor=0 \
    OMP_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    HOME=${APP_HOME} \
    XDG_CACHE_HOME=${APP_HOME}/.cache \
    HF_HOME=${APP_HOME}/.cache/huggingface

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        build-essential \
        libpq-dev \
        libgl1 \
        libglib2.0-0 \
        libgomp1 \
        libsm6 \
        libxext6 \
        libxrender1 \
        # WeasyPrint runtime libraries (HTML → PDF rendering)
        libpango-1.0-0 \
        libpangocairo-1.0-0 \
        libcairo2 \
        libgdk-pixbuf-2.0-0 \
        libffi8 \
        libfontconfig1 \
        shared-mime-info \
        fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir "poetry==${POETRY_VERSION}"

RUN groupadd --gid "${APP_GID}" "${APP_USER}" \
    && useradd --uid "${APP_UID}" --gid "${APP_GID}" --create-home \
        --home-dir "${APP_HOME}" --shell /usr/sbin/nologin "${APP_USER}"

# Install locked dependencies first for better layer caching.
COPY pyproject.toml poetry.lock* ./
RUN poetry install --no-root --only main

# Left root-owned: the application code is read-only to the runtime user, so a
# compromised worker cannot rewrite the code it is about to execute.
COPY . .
RUN poetry install --only main

# The only paths the app writes to at runtime: uploads, generated PDFs, and the
# embedding/reranker model caches.
RUN mkdir -p /app/storage/documents /app/storage/generated \
        "${APP_HOME}/.cache/fastembed" "${APP_HOME}/.cache/huggingface" \
    && chown -R "${APP_UID}:${APP_GID}" /app/storage "${APP_HOME}"

USER ${APP_UID}:${APP_GID}

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
