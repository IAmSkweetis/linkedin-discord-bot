# Build args
ARG PYTHON_VERSION=3.12.9


#### Base ####
FROM python:${PYTHON_VERSION}-slim AS base

SHELL ["/bin/bash", "-eo", "pipefail", "-c"]

RUN apt-get update -y \
    && apt-get upgrade -y \
    && apt-get install -y \
    --no-install-recommends \
    curl \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Setup our workdir and user
WORKDIR /app
RUN useradd -d '/app' --shell /bin/bash tucker \
    && chown -R tucker:tucker /app

USER tucker


#### Builder ####
FROM base AS builder

# python
ENV PYTHONFAULTHANDLER=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONHASHSEED=random
ENV PYTHONDONTWRITEBYTECODE=1

# pip:
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_DEFAULT_TIMEOUT=100
ENV PIP_ROOT_USER_ACTION=ignore
ENV PIP_CONSTRAINT='/var/cache/pip_constraint.txt'
# uv:
ENV UV_COMPILE_BYTECODE=1

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

# Copy our app and things
COPY --chown=tucker:tucker . /app/

# Install the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --compile-bytecode

#### Final ####
FROM base AS final

# ARGS
ARG PKG_NAME
ARG PKG_VERSION
ARG GIT_COMMIT_SHA
ARG GIT_REPO_URL
ARG DKR_BUILD_DATE

# Set our runtime environment variables
ENV PATH="/app/.venv/bin:$PATH"

# Copy the built app
COPY --from=builder --chown=tucker:tucker /app/ /app/

# Healthcheck
# TODO: Make this a real healthcheck
HEALTHCHECK --interval=5m --timeout=3s CMD python -c 'print("ok")' || exit 1

ENTRYPOINT ["li-bot"]
CMD []

# Metadata
LABEL org.opencontainers.image.created=${DKR_BUILD_DATE}
LABEL org.opencontainers.image.authors="Scott Wolfe"
LABEL org.opencontainers.image.url=${GIT_REPO_URL}
LABEL org.opencontainers.image.documentation=${GIT_REPO_URL}
LABEL org.opencontainers.image.source=${GIT_REPO_URL}
LABEL org.opencontainers.image.version=${PKG_VERSION}
LABEL org.opencontainers.image.revision=${GIT_COMMIT_SHA}
LABEL org.opencontainers.image.ref.name=${PKG_NAME}
LABEL org.opencontainers.image.title="LinkedIn Discord Bot"
LABEL org.opencontainers.image.description="LinkedIn Discord Bot"
