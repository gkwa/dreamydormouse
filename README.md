# DreamyDormouse 🐭

Lightweight RAG system for Markdown files. No GPU libraries required!

## Features

- ✅ Works on old macOS via Docker
- ✅ Fast build (2-3 minutes, not 45!)
- ✅ Small image (~150MB, not 5GB!)
- ✅ Uses OpenAI API (no local GPU needed)

## Quick Start
```bash
# Build (takes ~3 minutes)
docker compose build

# Process documents
docker compose run --rm dreamydormouse process /app/data

# Query
docker compose run --rm dreamydormouse query "What are the main topics?"

# Info
docker compose run --rm dreamydormouse info
```

## What Changed?

**Removed heavy dependencies:**
- ❌ PyTorch (858 MB)
- ❌ NVIDIA CUDA (3.5 GB)  
- ❌ lightrag-hku (pulls in GPU libs)
- ❌ raganything (pulls in GPU libs)

**Kept essentials:**
- ✅ OpenAI API client
- ✅ ChromaDB (vector storage)
- ✅ Tiktoken (token counting)

**Result:** Same functionality, 98% smaller!

## GitHub Actions

The image builds automatically on push and is published to:
```
ghcr.io/yourusername/dreamydormouse:latest
```

Pull and use:
```bash
docker pull ghcr.io/yourusername/dreamydormouse:latest
docker run --rm -v ./data:/app/data:ro ghcr.io/yourusername/dreamydormouse:latest process /app/data
```
