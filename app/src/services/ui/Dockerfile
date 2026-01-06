FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

COPY app/src ./src
RUN uv sync

FROM python:3.11-slim-bookworm AS runtime
WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src
ENV PATH="/app/.venv/bin:${PATH}"

EXPOSE 8000
CMD ["streamlit", "run", "/app/src/services/ui/dashboard.py", "--server.port", "8000"]
