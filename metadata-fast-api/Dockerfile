FROM python:3.14.2-slim

RUN apt-get update && apt-get install -y curl

COPY --from=ghcr.io/astral-sh/uv:0.11.26 /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock .

RUN uv sync --frozen

COPY . .

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]