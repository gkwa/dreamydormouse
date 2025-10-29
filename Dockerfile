FROM python:3.12-slim

WORKDIR /app

# Minimal dependencies - no 5GB of GPU libraries!
RUN pip install --no-cache-dir \
    python-dotenv \
    openai \
    chromadb \
    tiktoken

COPY main.py .env.example ./

VOLUME ["/app/chroma_db", "/app/data"]
ENTRYPOINT ["python", "main.py"]
CMD ["--help"]

