# DreamyDormouse 🐭

A RAG (Retrieval-Augmented Generation) system for querying large collections of Markdown files.

## ⚠️ Important: Image Size Issues

The current build includes heavy ML dependencies (PyTorch, CUDA libraries) totaling **5+ GB**. This causes:
- Very slow builds (30-45 minutes)
- GitHub Actions timeouts
- Large image downloads

**Solutions:**

1. **Wait for current build** (it's probably still running, not failed)
2. **Use local build** instead of GitHub Actions
3. **Optimize dependencies** (see below)

## Quick Start (Local Build Recommended)
```bash
# Build locally (faster with better feedback)
docker compose build

# Or use docker directly
docker build -t dreamydormouse .

# Check image size
docker images dreamydormouse
```

## Reducing Image Size

The dependencies include unnecessary heavy packages. To fix:
```bash
# Check what's being installed
./check-deps.sh

# Option 1: Use slim Dockerfile
docker build -f Dockerfile.slim -t dreamydormouse:slim .

# Option 2: Modify pyproject.toml to exclude heavy deps
# Remove or make optional: torch, nvidia-*, opencv-python
```

## Why Is the Build So Large?

The `lightrag-hku` and `raganything` packages pull in:
- PyTorch (858 MB)
- NVIDIA CUDA libraries (3.5+ GB total)
- OpenCV, scipy, scikit-image, etc.

**Most of these aren't needed for basic RAG operations!**

## Development Workflow
```bash
# Local development (skip GitHub Actions for now)
git add .
git commit -m "Update"
git push

# Build locally instead
docker compose build
docker compose run --rm dreamydormouse info
```

## GitHub Actions Timeout

If GitHub Actions times out:

1. **Add timeout** (already done in updated workflow)
2. **Build locally** and push image manually
3. **Optimize dependencies** to reduce size

## Checking Build Progress
```bash
# If build seems stuck, check Docker
docker ps -a

# Check build logs
docker logs <container-id>

# Monitor system resources
docker stats
```

## Manual Image Push (Alternative to GitHub Actions)
```bash
# Build locally
docker build -t ghcr.io/yourusername/dreamydormouse:latest .

# Login to GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u yourusername --password-stdin

# Push
docker push ghcr.io/yourusername/dreamydormouse:latest
```
