# DreamyDormouse 🐭

Lightweight RAG system for Markdown files. **Works on old macOS!**

[![Docker Build](https://github.com/yourusername/dreamydormouse/actions/workflows/docker-build.yml/badge.svg)](https://github.com/yourusername/dreamydormouse/actions/workflows/docker-build.yml)

## Why This Version?

Original version required macOS 13+ (for `onnxruntime`). This version works on **any macOS** via Docker.

**Stats:**
- ✅ Build time: ~3 minutes
- ✅ Image size: ~550MB  
- ✅ Works on old macOS 12 x86_64
- ✅ No GPU required

## Quick Start
```bash
# 1. Clone and setup
git clone https://github.com/yourusername/dreamydormouse.git
cd dreamydormouse
cp .env.example .env
# Edit .env and add OPENAI_API_KEY

# 2. Build (first time takes ~3 minutes)
docker compose build

# 3. Add your markdown files to ./data/

# 4. Process
docker compose run --rm dreamydormouse process /app/data

# 5. Query
docker compose run --rm dreamydormouse query "What are the main topics?"
```

## Commands
```bash
# Process markdown files
docker compose run --rm dreamydormouse process /app/data

# Process with custom settings
docker compose run --rm dreamydormouse process /app/data \
  --working-dir /app/custom_storage \
  --max-tokens 1000

# Query documents
docker compose run --rm dreamydormouse query "your question here"

# Query with custom working dir
docker compose run --rm dreamydormouse query "your question" \
  --working-dir /app/custom_storage

# Show system info
docker compose run --rm dreamydormouse info

# Show help
docker compose run --rm dreamydormouse --help
```

## Use Pre-built Image from GitHub
```bash
# Pull from GitHub Container Registry
docker pull ghcr.io/yourusername/dreamydormouse:latest

# Use it
docker run --rm \
  -v $(pwd)/data:/app/data:ro \
  -v $(pwd)/rag_storage:/app/rag_storage \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  ghcr.io/yourusername/dreamydormouse:latest process /app/data
```

## Docker Compose Configuration

The `docker-compose.yml` mounts:
- `./data` → `/app/data` (read-only) - your markdown files
- `./rag_storage` → `/app/rag_storage` - persistent vector database

Environment variables:
- `OPENAI_API_KEY` - Required
- `OPENAI_MODEL` - Optional (default: gpt-4o-mini)
- `EMBEDDING_MODEL` - Optional (default: text-embedding-3-small)

## What This Does

1. **Process:** Reads markdown files, chunks them, gets embeddings from OpenAI, stores in ChromaDB
2. **Query:** Takes your question, finds relevant chunks, sends to OpenAI with context, returns answer
3. **Info:** Shows system status and configuration

## Technical Details

**Dependencies:**
- `openai` - API client
- `chromadb` - Vector database
- `tiktoken` - Token counting
- `python-dotenv` - Environment variables

**What's NOT included:**
- ❌ PyTorch (858 MB saved)
- ❌ NVIDIA CUDA libraries (3.5 GB saved)
- ❌ Computer vision libraries
- ❌ Local ML models

**Why?** All AI processing happens via OpenAI's API. No local GPU needed!

## Troubleshooting

### macOS 12 compatibility issues
This version was specifically designed for older macOS. If you still have issues, try:
```bash
docker system prune -af
docker compose build --no-cache
```

### Slow build
First build downloads ~550MB. Subsequent builds are cached and fast.

### Out of memory
ChromaDB needs ~1GB RAM. Close other apps if needed.

## System Requirements

- Docker Desktop
- 2GB free disk space
- Internet connection
- OpenAI API key

## Development
```bash
# Run tests locally
docker compose build
docker compose run --rm dreamydormouse info

# Get shell in container
docker compose run --rm --entrypoint /bin/bash dreamydormouse

# Check Python packages
docker compose run --rm --entrypoint pip dreamydormouse list
```

## License

MIT
