"""
DreamyDormouse - RAG system for querying Markdown files

This tool processes a directory of Markdown files and allows you to query them
using natural language questions.
"""

import argparse
import asyncio
import os
import pathlib
import sys
import traceback

import dotenv
import lightrag
import lightrag.kg.shared_storage
import lightrag.llm.openai
import lightrag.utils
import raganything

# Load environment variables
dotenv.load_dotenv()


def setup_argparse():
    """Setup command line argument parser"""
    parser = argparse.ArgumentParser(
        description="DreamyDormouse - RAG system for querying Markdown files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process a directory of markdown files
  python main.py process ./my_notes

  # Process with custom working directory
  python main.py process ./my_notes --working-dir ./my_rag_storage

  # Query processed content
  python main.py query "What are the main topics discussed?"

  # Query with specific working directory
  python main.py query "Explain the concept" --working-dir ./my_rag_storage

  # Query with different modes
  python main.py query "Search query" --mode hybrid
  python main.py query "Search query" --mode local
  python main.py query "Search query" --mode global
        """,
    )

    parser.add_argument(
        "--api-key",
        default=os.getenv("OPENAI_API_KEY"),
        help="OpenAI API key (default: OPENAI_API_KEY env var)",
    )

    parser.add_argument(
        "--base-url",
        default=os.getenv("OPENAI_BASE_URL"),
        help="OpenAI API base URL (default: OPENAI_BASE_URL env var)",
    )

    parser.add_argument(
        "--working-dir",
        "-w",
        default="./rag_storage",
        help="Working directory for RAG storage (default: ./rag_storage)",
    )

    parser.add_argument(
        "--model",
        default=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        help="LLM model to use (default: gpt-4o-mini)",
    )

    parser.add_argument(
        "--embedding-model",
        default=os.getenv("EMBEDDING_MODEL", "text-embedding-3-large"),
        help="Embedding model to use (default: text-embedding-3-large)",
    )

    parser.add_argument(
        "--embedding-dim",
        type=int,
        default=int(os.getenv("EMBEDDING_DIM", "3072")),
        help="Embedding dimension (default: 3072)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Process command
    process_parser = subparsers.add_parser(
        "process", help="Process a directory of Markdown files"
    )
    process_parser.add_argument(
        "directory", type=str, help="Directory containing Markdown files"
    )
    process_parser.add_argument(
        "--recursive",
        "-r",
        action="store_true",
        default=True,
        help="Process subdirectories recursively (default: True)",
    )
    process_parser.add_argument(
        "--max-workers",
        type=int,
        default=4,
        help="Maximum number of concurrent file processors (default: 4)",
    )
    process_parser.add_argument(
        "--output-dir",
        "-o",
        default="./output",
        help="Output directory for parsed documents (default: ./output)",
    )

    # Query command
    query_parser = subparsers.add_parser(
        "query", help="Query the processed Markdown files"
    )
    query_parser.add_argument("question", type=str, help="Question to ask")
    query_parser.add_argument(
        "--mode",
        choices=["local", "global", "hybrid", "naive", "mix"],
        default="hybrid",
        help="Query mode (default: hybrid)",
    )
    query_parser.add_argument(
        "--stream",
        action="store_true",
        help="Enable streaming response",
    )

    # Info command
    subparsers.add_parser("info", help="Show information about the RAG system")

    return parser


async def process_directory(args):
    """Process a directory of Markdown files"""
    directory = pathlib.Path(args.directory)

    if not directory.exists():
        lightrag.utils.logger.error(f"Directory does not exist: {directory}")
        return 1

    if not directory.is_dir():
        lightrag.utils.logger.error(f"Path is not a directory: {directory}")
        return 1

    lightrag.utils.logger.info(f"Processing Markdown files in: {directory}")
    lightrag.utils.logger.info(f"Working directory: {args.working_dir}")
    lightrag.utils.logger.info(f"Recursive: {args.recursive}")
    lightrag.utils.logger.info(f"Max workers: {args.max_workers}")

    # Validate API key
    if not args.api_key:
        lightrag.utils.logger.error(
            "OpenAI API key is required. Set OPENAI_API_KEY "
            "environment variable or use --api-key"
        )
        return 1

    # Create RAG configuration optimized for Markdown files
    config = raganything.RAGAnythingConfig(
        working_dir=args.working_dir,
        parser="mineru",  # Will be used but with minimal overhead for text
        parse_method="txt",  # Use text mode for Markdown
        enable_image_processing=False,  # Disable multimodal features we don't need
        enable_table_processing=False,
        enable_equation_processing=False,
        max_concurrent_files=args.max_workers,
        recursive_folder_processing=args.recursive,
        supported_file_extensions=[".md", ".markdown"],
    )

    # Define LLM model function
    def llm_model_func(prompt, system_prompt=None, history_messages=None, **kwargs):
        if history_messages is None:
            history_messages = []
        return lightrag.llm.openai.openai_complete_if_cache(
            args.model,
            prompt,
            system_prompt=system_prompt,
            history_messages=history_messages,
            api_key=args.api_key,
            base_url=args.base_url,
            **kwargs,
        )

    # Define embedding function
    embedding_func = lightrag.utils.EmbeddingFunc(
        embedding_dim=args.embedding_dim,
        max_token_size=8192,
        func=lambda texts: lightrag.llm.openai.openai_embed(
            texts,
            model=args.embedding_model,
            api_key=args.api_key,
            base_url=args.base_url,
        ),
    )

    # Initialize RAGAnything
    rag = raganything.RAGAnything(
        config=config,
        llm_model_func=llm_model_func,
        embedding_func=embedding_func,
    )

    try:
        # Process the entire directory
        await rag.process_folder_complete(
            folder_path=str(directory),
            output_dir=args.output_dir,
            file_extensions=[".md", ".markdown"],
            recursive=args.recursive,
            max_workers=args.max_workers,
        )

        lightrag.utils.logger.info("✅ Processing complete!")
        lightrag.utils.logger.info("You can now query your Markdown files using:")
        lightrag.utils.logger.info('  python main.py query "your question here"')
    except Exception as e:
        lightrag.utils.logger.error(f"Error during processing: {e}")
        lightrag.utils.logger.error(traceback.format_exc())
        return 1
    finally:
        # Clean up resources
        await rag.finalize_storages()

    return 0


async def query_documents(args):
    """Query the processed documents"""
    lightrag.utils.logger.info(f"Query: {args.question}")
    lightrag.utils.logger.info(f"Mode: {args.mode}")
    lightrag.utils.logger.info(f"Working directory: {args.working_dir}")

    # Check if working directory exists
    if not pathlib.Path(args.working_dir).exists():
        lightrag.utils.logger.error(
            f"Working directory does not exist: {args.working_dir}. "
            "Have you processed documents yet?"
        )
        lightrag.utils.logger.info(
            "Run: python main.py process <directory> "
            "to process your Markdown files first"
        )
        return 1

    # Validate API key
    if not args.api_key:
        lightrag.utils.logger.error(
            "OpenAI API key is required. Set OPENAI_API_KEY "
            "environment variable or use --api-key"
        )
        return 1

    # Define LLM model function
    def llm_model_func(prompt, system_prompt=None, history_messages=None, **kwargs):
        if history_messages is None:
            history_messages = []
        return lightrag.llm.openai.openai_complete_if_cache(
            args.model,
            prompt,
            system_prompt=system_prompt,
            history_messages=history_messages,
            api_key=args.api_key,
            base_url=args.base_url,
            **kwargs,
        )

    # Define embedding function
    embedding_func = lightrag.utils.EmbeddingFunc(
        embedding_dim=args.embedding_dim,
        max_token_size=8192,
        func=lambda texts: lightrag.llm.openai.openai_embed(
            texts,
            model=args.embedding_model,
            api_key=args.api_key,
            base_url=args.base_url,
        ),
    )

    # Load existing LightRAG instance
    lightrag_instance = lightrag.LightRAG(
        working_dir=args.working_dir,
        llm_model_func=llm_model_func,
        embedding_func=embedding_func,
    )

    try:
        # Initialize storage (loads existing data)
        await lightrag_instance.initialize_storages()
        await lightrag.kg.shared_storage.initialize_pipeline_status()

        # Create RAGAnything instance with existing LightRAG
        rag = raganything.RAGAnything(
            lightrag=lightrag_instance,
        )

        # Execute query
        lightrag.utils.logger.info("Executing query...")
        result = await rag.aquery(args.question, mode=args.mode, stream=args.stream)

        # Display result
        print("\n" + "=" * 80)  # noqa: T201
        print("ANSWER:")  # noqa: T201
        print("=" * 80)  # noqa: T201
        print(result)  # noqa: T201
        print("=" * 80 + "\n")  # noqa: T201
    except Exception as e:
        lightrag.utils.logger.error(f"Error during query: {e}")
        lightrag.utils.logger.error(traceback.format_exc())
        return 1
    finally:
        # Clean up resources
        if lightrag_instance:
            await lightrag_instance.finalize_storages()

    return 0


def show_info(args):
    """Show information about the RAG system"""
    print("\n" + "=" * 80)  # noqa: T201
    print("DREAMYDORMOUSE - RAG System Information")  # noqa: T201
    print("=" * 80)  # noqa: T201

    print(f"\nWorking Directory: {args.working_dir}")  # noqa: T201

    if pathlib.Path(args.working_dir).exists():
        print("Status: ✅ Initialized")  # noqa: T201

        # Count files in working directory
        files = list(pathlib.Path(args.working_dir).rglob("*"))
        file_count = sum(1 for f in files if f.is_file())
        dir_count = sum(1 for f in files if f.is_dir())

        print(f"Files: {file_count}")  # noqa: T201
        print(f"Directories: {dir_count}")  # noqa: T201
    else:
        print("Status: ❌ Not initialized")  # noqa: T201
        print(  # noqa: T201
            "\nRun 'python main.py process <directory>' to process your Markdown files"
        )

    print("\nConfiguration:")  # noqa: T201
    print(f"  Model: {args.model}")  # noqa: T201
    print(f"  Embedding Model: {args.embedding_model}")  # noqa: T201
    print(f"  Embedding Dimension: {args.embedding_dim}")  # noqa: T201
    print(f"  API Key: {'✅ Set' if args.api_key else '❌ Not set'}")  # noqa: T201
    if args.base_url:
        print(f"  Base URL: {args.base_url}")  # noqa: T201

    print("=" * 80 + "\n")  # noqa: T201
    return 0


async def async_main():
    """Async main function"""
    parser = setup_argparse()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    if args.command == "process":
        return await process_directory(args)
    if args.command == "query":
        return await query_documents(args)
    if args.command == "info":
        return show_info(args)

    parser.print_help()
    return 1


def main():
    """Main entry point"""
    try:
        exit_code = asyncio.run(async_main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        lightrag.utils.logger.info("\nInterrupted by user")
        sys.exit(130)
    except Exception as e:
        lightrag.utils.logger.error(f"Unexpected error: {e}")
        lightrag.utils.logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
