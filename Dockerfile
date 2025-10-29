FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN echo "Installing system dependencies..." && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/* && \
    echo "System dependencies installed"

# Install uv by copying from official Astral image
RUN echo "Installing uv..."
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
RUN echo "uv installed" && uv --version

# Suppress UV hardlink warnings in Docker
ENV UV_LINK_MODE=copy

# Copy ALL project files needed for build (including README.md!)
RUN echo "Copying project files..."
COPY pyproject.toml .python-version README.md ./

# Install Python dependencies
RUN echo "Installing Python dependencies (this may take a few minutes)..." && \
    uv sync && \
    echo "Dependencies installed"

# Copy application code
COPY main.py .env.example ./
RUN echo "Application code copied"

# Create volume mount points
VOLUME ["/app/rag_storage", "/app/output", "/app/data"]

# Make the virtual environment the default Python environment
ENV PATH="/app/.venv/bin:$PATH"

# Set entrypoint
ENTRYPOINT ["uv", "run", "python", "main.py"]
CMD ["--help"]

