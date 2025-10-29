# DreamyDormouse - Lightweight Version

**This version works on ANY laptop** - no GPU required!

## What's Different?

- ❌ Removed: 5GB of NVIDIA CUDA libraries
- ❌ Removed: PyTorch, TensorFlow, heavy ML packages
- ✅ Kept: Simple text processing + OpenAI API calls
- ✅ Result: ~100MB image instead of 5GB

## Installation (macOS)

### Option 1: Local Python (No Docker)

```bash
# Install dependencies
pip install python-dotenv openai chromadb tiktoken pydantic

# Set API key
export OPENAI_API_KEY="your-key-here"

# Process documents
python main-simple.py process ./my_markdown_files

# Query
python main-simple.py query "What are the main topics?"
```

### Option 2: Docker

```bash
# Build (takes 2 minutes, not 30!)
docker compose -f docker-compose.simple.yml build

# Process
docker compose -f docker-compose.simple.yml run --rm dreamydormouse \
  process /app/data

# Query
docker compose -f docker-compose.simple.yml run --rm dreamydormouse \
  query "Your question here"
```

## Why This Works on Old macOS

- **No GPU needed** - all AI happens on OpenAI's servers
- **Minimal CPU usage** - just text processing
- **Low memory** - ChromaDB is efficient
- **Fast** - no heavy model loading

## Comparison

**Original (lightrag-hku + raganything):**
- Size: 5+ GB
- Build time: 30-45 minutes
- Requires: Modern hardware
- Use case: Local ML model hosting

**Simple version:**
- Size: ~100 MB
- Build time: 2-3 minutes
- Requires: Any laptop with internet
- Use case: API-based RAG (what you actually need!)

## Test It

```bash
# Create test data
mkdir -p data
echo "# AI Overview\nArtificial Intelligence is transforming technology." > data/ai.md
echo "# Python Basics\nPython is a versatile programming language." > data/python.md

# Process
python main-simple.py process ./data --db-path ./my_db

# Query
python main-simple.py query "Tell me about AI" --db-path ./my_db
```

## System Requirements

- macOS 10.13+ (or any OS really)
- Python 3.12+
- 1GB RAM
- Internet connection (for OpenAI API)
- OpenAI API key

**That's it!** No GPU, no CUDA, no heavyweight ML libraries.
```

**What should you do now?**

1. **Use the simple version** - it does everything you need
2. **Test locally first** - no Docker needed on your Mac:
   ```bash
   pip install python-dotenv openai chromadb tiktoken pydantic
   python main-simple.py process ./your-docs
   ```
3. **Forget about the heavy version** - you don't need it

The original `lightrag-hku` package is designed for people who want to run ML models locally. You just want to query documents using OpenAI's API - much simpler!
