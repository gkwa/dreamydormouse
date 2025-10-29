# DreamyDormouse 🐭

A RAG (Retrieval-Augmented Generation) system for querying large collections of Markdown files using RAG-Anything.

[![Docker Build](https://github.com/yourusername/dreamydormouse/actions/workflows/docker-build.yml/badge.svg)](https://github.com/yourusername/dreamydormouse/actions/workflows/docker-build.yml)

## Features

- 📚 Process directories with 20,000+ Markdown files
- 🔍 Natural language querying across your entire knowledge base
- 🚀 Recursive directory scanning
- ⚡ Concurrent file processing
- 🧠 Knowledge graph + vector embeddings for intelligent retrieval
- 💬 Multiple query modes (hybrid, local, global)
- 🐳 Docker support for easy deployment

## Quick Start with Docker

### Prerequisites

- Docker and Docker Compose installed
- OpenAI API key

### Setup

1. **Clone and configure**

   ```bash
   # Copy environment template
   cp .env.example .env

   # Edit .env and add your OpenAI API key
   nano .env
   ```

2. **Place your Markdown files**

   ```bash
   # Create a data directory and add your markdown files
   mkdir -p data
   # Copy your markdown files to ./data/
   ```

3. **Build the container**

   ```bash
   docker compose build
   ```

### Usage

#### Process Markdown Files

```bash
# Process all markdown files in ./data directory
docker compose run --rm dreamydormouse process /app/data

# With custom settings
docker compose run --rm dreamydormouse process /app/data \
  --max-workers 8 \
  --recursive
```

#### Query Your Documents

```bash
# Basic query
docker compose run --rm dreamydormouse query \
  "What are the main topics discussed in the documents?"

# Using different query modes
docker compose run --rm dreamydormouse query \
  "Explain the concept of X" --mode hybrid
```

#### Show System Info

```bash
docker compose run --rm dreamydormouse info
```

## GitHub Actions

This project includes automated Docker builds via GitHub Actions:

- **`docker-build.yml`**: Runs on every push/PR to test the build
- **`docker-publish.yml`**: Publishes images to GitHub Container Registry on releases

To use the published image:

```bash
docker pull ghcr.io/yourusername/dreamydormouse:latest
docker run --rm ghcr.io/yourusername/dreamydormouse:latest --help
```

## Development

### Local Testing

```bash
# Build
docker compose build

# Run tests
docker compose run --rm dreamydormouse info

# Get shell access
docker compose run --rm --entrypoint /bin/bash dreamydormouse
```

### CI/CD

The project uses GitHub Actions for continuous integration:

1. Every push triggers a build and test
2. Docker images are cached for faster builds
3. Release tags automatically publish to GitHub Container Registry

## Query Modes

- **hybrid** (default): Combines local and global search for best results
- **local**: Focuses on specific relevant chunks
- **global**: Provides broader context and summaries
- **naive**: Simple semantic search without knowledge graph
- **mix**: Adaptive combination of modes

## Environment Variables

All environment variables can be set in `.env`:

- `OPENAI_API_KEY` - Your OpenAI API key (required)
- `OPENAI_BASE_URL` - Custom API endpoint (optional)
- `OPENAI_MODEL` - LLM model to use (default: gpt-4o-mini)
- `EMBEDDING_MODEL` - Embedding model (default: text-embedding-3-large)
- `EMBEDDING_DIM` - Embedding dimension (default: 3072)

## License

MIT

## Credits

Built on top of [RAG-Anything](https://github.com/HKUDS/RAG-Anything) and [LightRAG](https://github.com/HKUDS/LightRAG).

````

**Commands to clean up:**

```bash
# Remove debug script
rm debug-docker.sh

# Remove debug Dockerfile if it exists
rm -f Dockerfile.debug

# Clean up Docker build cache (optional)
docker builder prune -f

# Full cleanup (removes all unused Docker resources)
docker system prune -af
````

**To use GitHub Actions:**

1. Push the changes:

```bash
git add .github/workflows/
git add Dockerfile README.md
git rm debug-docker.sh
git commit -m "Add GitHub Actions for Docker build and publish"
git push origin master
```

2. The build will trigger automatically on push

3. To publish to GitHub Container Registry:
   - Go to Settings → Actions → General
   - Enable "Read and write permissions" for workflows
   - Create a release tag: `git tag v0.1.0 && git push --tags`

The image will be available at: `ghcr.io/yourusername/dreamydormouse:latest`
