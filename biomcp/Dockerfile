FROM python:3.14.6-slim

COPY --from=ghcr.io/astral-sh/uv:0.11.32 /uv /usr/local/bin/uv

ENV UV_PROJECT_ENVIRONMENT=/usr/local \
    UV_LINK_MODE=copy

WORKDIR /app

COPY pyproject.toml uv.lock .

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

COPY . .

EXPOSE 9000

CMD ["python", "server.py"]