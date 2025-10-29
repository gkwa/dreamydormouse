# DreamyDormouse 🐭

A RAG system for querying Markdown files.

## ⚠️ Important: Recommended Approach

**For old macOS laptops, skip Docker!** Just use Python directly:
```bash
# Install (takes 1-2 minutes)
pip install python-dotenv lightrag-hku raganything

# Use
export OPENAI_API_KEY="your-key"
python main.py process ./your-markdown-files
python main.py query "What are the main topics?"
```

## Why Skip Docker?

- **Docker build:** 30-45 minutes, 5GB download
- **Local install:** 2 minutes, works immediately
- **Both do the exact same thing** on your laptop

## Docker (If You Really Want It)
```bash
# Build (will take a LONG time and download 5GB)
docker compose build

# Use
docker compose run --rm dreamydormouse process /app/data
docker compose run --rm dreamydormouse query "your question"
```

## What Gets Installed

The dependencies include heavy ML packages:
- PyTorch (858 MB)
- NVIDIA CUDA libraries (3.5+ GB)
- Various ML tools

**These are NOT used** when you run on macOS (or any laptop). They're optional dependencies that get installed anyway. All the actual AI work happens via OpenAI's API.

## System Requirements

- Python 3.12+
- OpenAI API key
- Internet connection
- 1GB RAM
- **No GPU needed** - everything runs via API calls

## Quick Test
```bash
# Create test documents
mkdir test-docs
echo "# AI\nAI is cool" > test-docs/ai.md
echo "# Python\nPython is great" > test-docs/py.md

# Process
python main.py process ./test-docs

# Query
python main.py query "Tell me about AI"
```
