FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
ENV UV_LINK_MODE=copy

# Copy project files
COPY pyproject.toml .python-version README.md ./

# Install dependencies WITHOUT building the local package
RUN uv pip install --system \
    python-dotenv \
    lightrag-hku \
    raganything

# Copy application code
COPY main.py .env.example ./

VOLUME ["/app/rag_storage", "/app/output", "/app/data"]

ENTRYPOINT ["python", "main.py"]
CMD ["--help"]

