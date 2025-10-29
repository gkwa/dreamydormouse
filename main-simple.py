"""
DreamyDormouse - Simple RAG system for querying Markdown files
Lightweight version without heavy ML dependencies
"""

import argparse
import os
import pathlib
from typing import List

import chromadb
import openai
import tiktoken
from dotenv import load_dotenv

load_dotenv()


def chunk_markdown(text: str, max_tokens: int = 500) -> List[str]:
    """Simple markdown chunking"""
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = []
    current_tokens = 0
    
    encoding = tiktoken.get_encoding("cl100k_base")
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
            
        para_tokens = len(encoding.encode(para))
        
        if current_tokens + para_tokens > max_tokens and current_chunk:
            chunks.append('\n\n'.join(current_chunk))
            current_chunk = [para]
            current_tokens = para_tokens
        else:
            current_chunk.append(para)
            current_tokens += para_tokens
    
    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))
    
    return chunks or [text]


def get_embedding(text: str, api_key: str, model: str = "text-embedding-3-small") -> List[float]:
    """Get embedding from OpenAI API"""
    client = openai.Client(api_key=api_key)
    response = client.embeddings.create(model=model, input=text)
    return response.data[0].embedding


def process_directory(directory: str, db_path: str, api_key: str):
    """Process all markdown files in directory"""
    client = chromadb.PersistentClient(path=db_path)
    collection = client.get_or_create_collection("docs")
    
    markdown_files = list(pathlib.Path(directory).rglob("*.md"))
    print(f"Found {len(markdown_files)} markdown files")
    
    for i, file_path in enumerate(markdown_files, 1):
        print(f"[{i}/{len(markdown_files)}] Processing {file_path.name}...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        chunks = chunk_markdown(text)
        
        for j, chunk in enumerate(chunks):
            embedding = get_embedding(chunk, api_key)
            doc_id = f"{file_path.name}-{j}"
            
            collection.add(
                ids=[doc_id],
                documents=[chunk],
                embeddings=[embedding],
                metadatas=[{"source": str(file_path), "chunk": j}]
            )
    
    print(f"✅ Indexed {len(markdown_files)} files")


def query_documents(question: str, db_path: str, api_key: str, model: str = "gpt-4o-mini"):
    """Query the indexed documents"""
    client = chromadb.PersistentClient(path=db_path)
    collection = client.get_or_create_collection("docs")
    
    # Get embedding for question
    question_embedding = get_embedding(question, api_key)
    
    # Search for relevant chunks
    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=5
    )
    
    if not results['documents'][0]:
        print("No relevant documents found")
        return
    
    # Build context from results
    context = "\n\n---\n\n".join(results['documents'][0])
    
    # Query OpenAI with context
    openai_client = openai.Client(api_key=api_key)
    response = openai_client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided context."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
        ]
    )
    
    answer = response.choices[0].message.content
    
    print("\n" + "=" * 80)
    print("ANSWER:")
    print("=" * 80)
    print(answer)
    print("=" * 80 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Simple RAG for Markdown files")
    parser.add_argument("--api-key", default=os.getenv("OPENAI_API_KEY"))
    
    subparsers = parser.add_subparsers(dest="command")
    
    # Process command
    process_parser = subparsers.add_parser("process")
    process_parser.add_argument("directory")
    process_parser.add_argument("--db-path", default="./chroma_db")
    
    # Query command  
    query_parser = subparsers.add_parser("query")
    query_parser.add_argument("question")
    query_parser.add_argument("--db-path", default="./chroma_db")
    query_parser.add_argument("--model", default="gpt-4o-mini")
    
    args = parser.parse_args()
    
    if not args.api_key:
        print("Error: OPENAI_API_KEY required")
        return 1
    
    if args.command == "process":
        process_directory(args.directory, args.db_path, args.api_key)
    elif args.command == "query":
        query_documents(args.question, args.db_path, args.api_key, args.model)
    else:
        parser.print_help()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

