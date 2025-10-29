"""DreamyDormouse - Lightweight RAG for Markdown files"""
import os
import sys
import argparse
import pathlib
from dotenv import load_dotenv
import chromadb
import openai
import tiktoken

load_dotenv()


def chunk_text(text, max_tokens=500):
    """Simple chunking by tokens"""
    enc = tiktoken.get_encoding("cl100k_base")
    words = text.split()
    chunks = []
    current = []
    current_tokens = 0
    
    for word in words:
        word_tokens = len(enc.encode(word))
        if current_tokens + word_tokens > max_tokens and current:
            chunks.append(" ".join(current))
            current = [word]
            current_tokens = word_tokens
        else:
            current.append(word)
            current_tokens += word_tokens
    
    if current:
        chunks.append(" ".join(current))
    return chunks or [text]


def process_documents(args):
    """Process markdown files"""
    directory = pathlib.Path(args.directory)
    if not directory.exists():
        print(f"Error: {directory} does not exist")
        return 1
    
    client = chromadb.PersistentClient(path=args.working_dir)
    collection = client.get_or_create_collection("docs")
    openai_client = openai.Client(api_key=args.api_key)
    
    files = list(directory.rglob("*.md"))
    print(f"Processing {len(files)} markdown files...")
    
    for i, path in enumerate(files, 1):
        print(f"[{i}/{len(files)}] {path.name}")
        text = path.read_text(encoding='utf-8')
        
        for j, chunk in enumerate(chunk_text(text, args.max_tokens)):
            # Get embedding
            resp = openai_client.embeddings.create(
                model=args.embedding_model,
                input=chunk
            )
            embedding = resp.data[0].embedding
            
            # Store
            collection.add(
                ids=[f"{path.name}-{j}"],
                documents=[chunk],
                embeddings=[embedding],
                metadatas=[{"source": str(path), "chunk": j}]
            )
    
    print(f"✅ Processed {len(files)} files")
    return 0


def query_documents(args):
    """Query documents"""
    if not pathlib.Path(args.working_dir).exists():
        print(f"Error: {args.working_dir} does not exist. Process documents first.")
        return 1
    
    client = chromadb.PersistentClient(path=args.working_dir)
    collection = client.get_or_create_collection("docs")
    openai_client = openai.Client(api_key=args.api_key)
    
    # Get question embedding
    resp = openai_client.embeddings.create(
        model=args.embedding_model,
        input=args.question
    )
    q_embedding = resp.data[0].embedding
    
    # Search
    results = collection.query(
        query_embeddings=[q_embedding],
        n_results=5
    )
    
    if not results['documents'][0]:
        print("No relevant documents found")
        return 1
    
    # Build context
    context = "\n\n---\n\n".join(results['documents'][0])
    
    # Ask OpenAI
    resp = openai_client.chat.completions.create(
        model=args.model,
        messages=[
            {"role": "system", "content": "Answer based on the provided context."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {args.question}"}
        ]
    )
    
    print("\n" + "=" * 80)
    print("ANSWER:")
    print("=" * 80)
    print(resp.choices[0].message.content)
    print("=" * 80 + "\n")
    return 0


def show_info(args):
    """Show system info"""
    print("\n" + "=" * 80)
    print("DREAMYDORMOUSE - Lightweight RAG System")
    print("=" * 80)
    print(f"\nWorking Directory: {args.working_dir}")
    
    if pathlib.Path(args.working_dir).exists():
        print("Status: ✅ Initialized")
        files = list(pathlib.Path(args.working_dir).rglob("*"))
        print(f"Files: {sum(1 for f in files if f.is_file())}")
    else:
        print("Status: ❌ Not initialized")
        print("\nRun: python main.py process <directory>")
    
    print("\nConfiguration:")
    print(f"  Model: {args.model}")
    print(f"  Embedding Model: {args.embedding_model}")
    print(f"  API Key: {'✅ Set' if args.api_key else '❌ Not set'}")
    print("=" * 80 + "\n")
    return 0


def main():
    parser = argparse.ArgumentParser(description="DreamyDormouse - RAG for Markdown")
    parser.add_argument("--api-key", default=os.getenv("OPENAI_API_KEY"))
    parser.add_argument("--working-dir", "-w", default="./rag_storage")
    parser.add_argument("--model", default=os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
    parser.add_argument("--embedding-model", default=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"))
    
    subparsers = parser.add_subparsers(dest="command")
    
    # Process command
    process_parser = subparsers.add_parser("process")
    process_parser.add_argument("directory")
    process_parser.add_argument("--max-tokens", type=int, default=500)
    
    # Query command
    query_parser = subparsers.add_parser("query")
    query_parser.add_argument("question")
    
    # Info command
    subparsers.add_parser("info")
    
    args = parser.parse_args()
    
    if not args.api_key:
        print("Error: OPENAI_API_KEY required")
        return 1
    
    if args.command == "process":
        return process_documents(args)
    elif args.command == "query":
        return query_documents(args)
    elif args.command == "info":
        return show_info(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())

