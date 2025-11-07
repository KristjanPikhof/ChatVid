#!/usr/bin/env python3
"""
ChatVid CLI - Memvid Dataset Management Tool

A complete CLI tool for managing document datasets with embeddings and interactive chat.
"""

import os
import sys
import json
import argparse
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# Suppress tokenizer warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"

try:
    from memvid import MemvidEncoder, MemvidRetriever, MemvidChat
    import PyPDF2
    from dotenv import load_dotenv
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("Run: ./cli.sh setup")
    sys.exit(1)

# Try to import python-docx (optional)
try:
    import docx

    DOCX_SUPPORT = True
except ImportError:
    DOCX_SUPPORT = False

# Project directories
SCRIPT_DIR = Path(__file__).parent
DATASETS_DIR = SCRIPT_DIR / "datasets"
ENV_FILE = SCRIPT_DIR / ".env"

# Ensure datasets directory exists
DATASETS_DIR.mkdir(exist_ok=True)

# Load environment variables
load_dotenv(ENV_FILE)


class Colors:
    """Terminal colors"""

    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    CYAN = "\033[0;36m"
    NC = "\033[0m"  # No Color


def print_info(msg):
    print(f"{Colors.BLUE}ℹ{Colors.NC} {msg}")


def print_success(msg):
    print(f"{Colors.GREEN}✓{Colors.NC} {msg}")


def print_error(msg):
    print(f"{Colors.RED}✗{Colors.NC} {msg}")


def print_warning(msg):
    print(f"{Colors.YELLOW}⚠{Colors.NC} {msg}")


def print_header(msg):
    print(f"\n{Colors.CYAN}{'=' * 70}{Colors.NC}")
    print(f"{Colors.CYAN}{msg.center(70)}{Colors.NC}")
    print(f"{Colors.CYAN}{'=' * 70}{Colors.NC}\n")


def get_file_hash(file_path: Path) -> str:
    """Calculate MD5 hash of file"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def get_env_int(key: str, default: int, min_val: int, max_val: int) -> int:
    """Get integer from environment with validation"""
    value = os.getenv(key)
    if value is None:
        return default

    try:
        int_value = int(value)
        if int_value < min_val or int_value > max_val:
            print_warning(f"{key}={int_value} out of range [{min_val}-{max_val}], using default: {default}")
            return default
        return int_value
    except ValueError:
        print_warning(f"{key}={value} is not a valid integer, using default: {default}")
        return default


def get_env_float(key: str, default: float, min_val: float, max_val: float) -> float:
    """Get float from environment with validation"""
    value = os.getenv(key)
    if value is None:
        return default

    try:
        float_value = float(value)
        if float_value < min_val or float_value > max_val:
            print_warning(f"{key}={float_value} out of range [{min_val}-{max_val}], using default: {default}")
            return default
        return float_value
    except ValueError:
        print_warning(f"{key}={value} is not a valid number, using default: {default}")
        return default


def get_env_str(key: str, default: str) -> str:
    """Get string from environment with default"""
    value = os.getenv(key)
    if value is None or value.strip() == "":
        return default
    return value.strip()


def read_text_file(file_path: Path) -> str:
    """Read plain text file"""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def read_pdf_file(file_path: Path) -> str:
    """Extract text from PDF file"""
    text = []
    try:
        with open(file_path, "rb") as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text.append(page_text)
        return "\n\n".join(text)
    except Exception as e:
        print_error(f"Error reading PDF {file_path.name}: {e}")
        return ""


def read_docx_file(file_path: Path) -> str:
    """Extract text from DOCX file"""
    if not DOCX_SUPPORT:
        print_warning(f"Skipping {file_path.name} - python-docx not installed")
        return ""

    try:
        doc = docx.Document(file_path)
        text = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text.append(paragraph.text)
        return "\n\n".join(text)
    except Exception as e:
        print_error(f"Error reading DOCX {file_path.name}: {e}")
        return ""


def process_file(file_path: Path) -> Optional[str]:
    """Process a file and extract text based on extension"""
    ext = file_path.suffix.lower()

    if ext in [".txt", ".md", ".markdown"]:
        return read_text_file(file_path)
    elif ext == ".pdf":
        return read_pdf_file(file_path)
    elif ext in [".docx", ".doc"]:
        return read_docx_file(file_path)
    else:
        print_warning(f"Skipping unsupported file type: {file_path.name}")
        return None


class Dataset:
    """Represents a dataset with its metadata"""

    def __init__(self, name: str):
        self.name = name
        self.path = DATASETS_DIR / name
        self.documents_dir = self.path / "documents"
        self.metadata_file = self.path / "metadata.json"
        self.video_file = self.path / "knowledge.mp4"
        self.index_file = self.path / "knowledge_index.json"
        self.faiss_file = self.path / "knowledge_index.faiss"

    def exists(self) -> bool:
        """Check if dataset exists"""
        return self.path.exists() and self.path.is_dir()

    def create(self):
        """Create dataset directory structure"""
        self.path.mkdir(exist_ok=True)
        self.documents_dir.mkdir(exist_ok=True)

        # Create initial metadata
        metadata = {
            "name": self.name,
            "created": datetime.now().isoformat(),
            "last_build": None,
            "files_processed": {},
            "total_chunks": 0,
        }
        self.save_metadata(metadata)

    def load_metadata(self) -> Dict:
        """Load dataset metadata"""
        if self.metadata_file.exists():
            with open(self.metadata_file, "r") as f:
                return json.load(f)
        return {}

    def save_metadata(self, metadata: Dict):
        """Save dataset metadata"""
        with open(self.metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)

    def get_documents(self) -> List[Path]:
        """Get all document files in the documents directory"""
        files = []
        for ext in ["*.txt", "*.md", "*.pdf", "*.docx", "*.doc"]:
            files.extend(self.documents_dir.glob(ext))
        return sorted(files)

    def has_embeddings(self) -> bool:
        """Check if embeddings have been built"""
        return self.video_file.exists() and self.index_file.exists()


def cmd_setup(args):
    """Setup API key"""
    print_header("ChatVid Setup")

    # Check if .env already exists
    if ENV_FILE.exists():
        print_info(f"Configuration file found at: {ENV_FILE}")
        load_dotenv(ENV_FILE)
        if os.getenv("OPENAI_API_KEY"):
            print_success("API key is already configured!")
            print("\nTo update, edit the .env file or delete it and run setup again.")
            return

    print("Choose your LLM provider:")
    print("1) OpenAI (https://platform.openai.com/api-keys)")
    print("2) OpenRouter (https://openrouter.ai/keys)")
    print()

    choice = input("Enter choice (1 or 2): ").strip()

    # Configuration template - {llm_model} will be replaced based on provider
    config_template = """# ChatVid Configuration

# ============================================================================
# API Configuration (Required)
# ============================================================================

{api_config}

# ============================================================================
# Chunking Configuration (Build Phase)
# ============================================================================

# Size of text chunks in characters (affects how documents are split)
# Range: 100-1000 | Default: 300
CHUNK_SIZE=300

# Overlap between consecutive chunks in characters (prevents information loss)
# Range: 20-200 | Default: 50
CHUNK_OVERLAP=50

# ============================================================================
# LLM Configuration (Chat Phase)
# ============================================================================

# Model to use for chat responses
# OpenAI: gpt-4o-mini-2024-07-18, gpt-4o, gpt-4-turbo, gpt-3.5-turbo
# OpenRouter: openai/gpt-4o, anthropic/claude-3-sonnet, google/gemini-pro-1.5, etc.
LLM_MODEL={llm_model}

# Temperature controls response creativity (0.0 = focused, 2.0 = creative)
# Range: 0.0-2.0 | Default: 0.7
LLM_TEMPERATURE=0.7

# Maximum tokens in response (controls response length)
# Range: 100-4000 | Default: 1000
LLM_MAX_TOKENS=1000

# Number of text chunks to retrieve for each query
# Range: 1-20 | Default: 10
CONTEXT_CHUNKS=10

# Number of conversation turns to remember (history depth)
# Range: 1-50 | Default: 10
MAX_HISTORY=10
"""

    if choice == "1":
        api_key = input("Enter your OpenAI API key (sk-...): ").strip()
        api_config = f"# For OpenAI:\nOPENAI_API_KEY={api_key}"
        llm_model = "gpt-4o-mini-2024-07-18"
        with open(ENV_FILE, "w") as f:
            f.write(config_template.format(api_config=api_config, llm_model=llm_model))
        print_success("OpenAI API key saved to .env")
        model_display = llm_model

    elif choice == "2":
        api_key = input("Enter your OpenRouter API key (sk-or-...): ").strip()
        api_config = f"# For OpenRouter:\nOPENAI_API_BASE=https://openrouter.ai/api/v1\nOPENAI_API_KEY={api_key}"
        llm_model = "openai/gpt-4o"
        with open(ENV_FILE, "w") as f:
            f.write(config_template.format(api_config=api_config, llm_model=llm_model))
        print_success("OpenRouter API key saved to .env")
        model_display = llm_model

    else:
        print_error("Invalid choice")
        return

    print()
    print_success("Setup complete! Configuration saved to .env")
    print()
    print_info("Default settings applied:")
    print_info("  - Chunk size: 300 characters")
    print_info("  - Chunk overlap: 50 characters")
    print_info(f"  - LLM model: {model_display}")
    print_info("  - Context chunks: 10")
    print()
    print_info("To customize settings, edit .env file")
    print_info("Next step: ./cli.sh create <dataset-name>")


def cmd_create(args):
    """Create a new dataset"""
    name = args.name

    # Validate name
    if not name.replace("-", "").replace("_", "").isalnum():
        print_error(
            "Dataset name can only contain letters, numbers, hyphens, and underscores"
        )
        return

    dataset = Dataset(name)

    if dataset.exists():
        print_error(f"Dataset '{name}' already exists!")
        return

    dataset.create()
    print_success(f"Dataset '{name}' created successfully!")
    print()
    print_info(f"Dataset location: {dataset.path}")
    print_info(f"Add your documents to: {dataset.documents_dir}")
    print()
    print_info("Next steps:")
    print(f"  1. Add files to {dataset.documents_dir}/")
    print(f"  2. Run: ./cli.sh build {name}")
    print(f"  3. Run: ./cli.sh chat {name}")


def cmd_list(args):
    """List all datasets"""
    datasets = [d for d in DATASETS_DIR.iterdir() if d.is_dir()]

    if not datasets:
        print_info("No datasets found. Create one with: ./cli.sh create <name>")
        return

    print_header("Available Datasets")

    for dataset_dir in sorted(datasets):
        dataset = Dataset(dataset_dir.name)
        metadata = dataset.load_metadata()

        print(f"\n📁 {Colors.CYAN}{dataset.name}{Colors.NC}")
        print(f"   Created: {metadata.get('created', 'Unknown')[:19]}")

        if dataset.has_embeddings():
            last_build = metadata.get("last_build", "Unknown")
            if last_build != "Unknown":
                last_build = last_build[:19]
            print(f"   Last build: {last_build}")
            print(f"   Chunks: {metadata.get('total_chunks', 0)}")
            print(f"   Files: {len(metadata.get('files_processed', {}))}")
            print(f"   {Colors.GREEN}✓ Ready for chat{Colors.NC}")
        else:
            docs = dataset.get_documents()
            print(f"   Documents: {len(docs)}")
            print(f"   {Colors.YELLOW}⚠ Embeddings not built{Colors.NC}")

    print()


def cmd_info(args):
    """Show detailed dataset information"""
    dataset = Dataset(args.name)

    if not dataset.exists():
        print_error(f"Dataset '{args.name}' not found")
        return

    metadata = dataset.load_metadata()
    docs = dataset.get_documents()

    print_header(f"Dataset: {dataset.name}")

    print(f"Location: {dataset.path}")
    print(f"Created: {metadata.get('created', 'Unknown')}")
    print()

    print("📄 Documents:")
    if docs:
        for doc in docs:
            size_kb = doc.stat().st_size / 1024
            print(f"   - {doc.name} ({size_kb:.1f} KB)")
    else:
        print("   No documents found")
    print()

    if dataset.has_embeddings():
        print("🎯 Embeddings:")
        print(f"   Last build: {metadata.get('last_build', 'Unknown')[:19]}")
        print(f"   Total chunks: {metadata.get('total_chunks', 0)}")
        print(f"   Files processed: {len(metadata.get('files_processed', {}))}")

        video_size = dataset.video_file.stat().st_size / (1024 * 1024)
        print(f"   Video size: {video_size:.2f} MB")
        print(f"   Status: {Colors.GREEN}Ready for chat{Colors.NC}")
    else:
        print("⚠️  Embeddings not built")
        print(f"   Run: ./cli.sh build {dataset.name}")

    print()


def cmd_build(args):
    """Build embeddings from documents"""
    dataset = Dataset(args.name)

    if not dataset.exists():
        print_error(f"Dataset '{args.name}' not found")
        return

    docs = dataset.get_documents()

    if not docs:
        print_error(f"No documents found in {dataset.documents_dir}")
        print_info("Add PDF, TXT, MD, or DOCX files to the documents/ folder")
        return

    print_header(f"Building: {dataset.name}")

    # Check if this is rebuild or first build
    is_rebuild = args.rebuild if hasattr(args, "rebuild") else False
    metadata = dataset.load_metadata()

    if is_rebuild and dataset.has_embeddings():
        print_info("Removing existing embeddings...")
        for f in [dataset.video_file, dataset.index_file, dataset.faiss_file]:
            if f.exists():
                f.unlink()
        metadata["files_processed"] = {}

    # Initialize encoder
    encoder = MemvidEncoder()

    # Get chunking configuration from environment
    chunk_size = get_env_int("CHUNK_SIZE", 300, 100, 1000)
    chunk_overlap = get_env_int("CHUNK_OVERLAP", 50, 20, 200)

    print_info(f"Processing {len(docs)} documents...")
    print_info(f"Chunk settings: size={chunk_size}, overlap={chunk_overlap}")
    print()

    files_processed = {}
    for i, doc_path in enumerate(docs, 1):
        print(f"[{i}/{len(docs)}] Processing: {doc_path.name}")

        # Extract text
        text = process_file(doc_path)
        if not text or len(text.strip()) < 10:
            print_warning(f"  Skipped (no text extracted)")
            continue

        # Add to encoder with source attribution
        # Prepend source filename to help LLM distinguish between documents
        file_hash = get_file_hash(doc_path)
        prefixed_text = f"[Source: {doc_path.name}]\n\n{text}"
        encoder.add_text(prefixed_text, chunk_size=chunk_size, overlap=chunk_overlap)

        files_processed[doc_path.name] = file_hash
        print_success(f"  Added ({len(text)} characters)")

    print()

    # Build video
    if encoder.chunks:
        print_info("Building embeddings (this may take a while)...")
        stats = encoder.build_video(
            str(dataset.video_file), str(dataset.index_file), show_progress=True
        )

        # Update metadata
        metadata["last_build"] = datetime.now().isoformat()
        metadata["files_processed"] = files_processed
        metadata["total_chunks"] = stats["total_chunks"]
        dataset.save_metadata(metadata)

        print()
        print_success("Build complete!")
        print()
        print_info(f"Total chunks: {stats['total_chunks']}")
        print_info(f"Files processed: {len(files_processed)}")
        print()
        print_info(f"Ready to chat! Run: ./cli.sh chat {dataset.name}")
    else:
        print_error("No text extracted from documents")


def cmd_append(args):
    """Append new documents to existing dataset"""
    dataset = Dataset(args.name)

    if not dataset.exists():
        print_error(f"Dataset '{args.name}' not found")
        return

    if not dataset.has_embeddings():
        print_error("No existing embeddings found. Use 'build' instead.")
        return

    metadata = dataset.load_metadata()
    existing_files = metadata.get("files_processed", {})

    docs = dataset.get_documents()
    new_docs = []

    # Find new or modified documents
    for doc_path in docs:
        current_hash = get_file_hash(doc_path)
        if (
            doc_path.name not in existing_files
            or existing_files[doc_path.name] != current_hash
        ):
            new_docs.append(doc_path)

    if not new_docs:
        print_info("No new or modified documents found")
        return

    print_header(f"Appending to: {dataset.name}")
    print_info(f"Found {len(new_docs)} new/modified documents")
    print()

    # For simplicity, we'll rebuild with all files
    # (Memvid doesn't easily support true append to video)
    print_info("Note: Rebuilding embeddings with all documents...")
    args.rebuild = True
    cmd_build(args)


def cmd_rebuild(args):
    """Rebuild embeddings from scratch"""
    dataset = Dataset(args.name)

    if not dataset.exists():
        print_error(f"Dataset '{args.name}' not found")
        return

    if not dataset.has_embeddings():
        print_info("No existing embeddings found. Running initial build...")
        cmd_build(args)
        return

    print_warning(
        f"This will delete existing embeddings for '{args.name}' and rebuild from scratch."
    )
    confirm = input("Continue? (y/N): ").strip().lower()

    if confirm != "y":
        print_info("Cancelled")
        return

    args.rebuild = True
    cmd_build(args)


def cmd_chat(args):
    """Start interactive chat with dataset"""
    dataset = Dataset(args.name)

    if not dataset.exists():
        print_error(f"Dataset '{args.name}' not found")
        return

    if not dataset.has_embeddings():
        print_error(f"Embeddings not built for '{args.name}'")
        print_info(f"Run: ./cli.sh build {args.name}")
        return

    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print_error("API key not configured")
        print_info("Run: ./cli.sh setup")
        return

    print_header(f"Chat: {dataset.name}")

    # Initialize chat
    try:
        base_url = os.getenv("OPENAI_API_BASE")

        # Get LLM configuration from environment
        llm_model = get_env_str("LLM_MODEL", "gpt-4o-mini-2024-07-18")
        llm_temperature = get_env_float("LLM_TEMPERATURE", 0.7, 0.0, 2.0)
        llm_max_tokens = get_env_int("LLM_MAX_TOKENS", 1000, 100, 4000)
        context_chunks = get_env_int("CONTEXT_CHUNKS", 10, 1, 20)
        max_history = get_env_int("MAX_HISTORY", 10, 1, 50)

        # Load the existing config from index and update chat settings
        import json

        with open(dataset.index_file, "r") as f:
            index_data = json.load(f)

        # Use existing config and override chat settings
        chat_config = index_data.get("config", {})
        chat_config["chat"] = {
            "max_history": max_history,
            "context_chunks": context_chunks,
        }
        chat_config["llm"]["temperature"] = llm_temperature
        chat_config["llm"]["max_tokens"] = llm_max_tokens

        print_info(f"LLM settings: model={llm_model}, temp={llm_temperature}, max_tokens={llm_max_tokens}")
        print_info(f"Chat settings: context_chunks={context_chunks}, max_history={max_history}")
        print()

        chat = MemvidChat(
            video_file=str(dataset.video_file),
            index_file=str(dataset.index_file),
            llm_provider="openai",
            llm_model=llm_model,
            llm_api_key=api_key,
            config=chat_config,
        )

        # Override base_url if using OpenRouter
        if base_url and hasattr(chat.llm_client, "client"):
            chat.llm_client.client.base_url = base_url

        print_success("Chat initialized successfully!")
        print()
        print_info("Type your questions and press Enter.")
        print_info("Type 'quit' or 'exit' to end the session.")
        print(f"{Colors.CYAN}{'=' * 70}{Colors.NC}\n")

        # Start interactive chat
        chat.interactive_chat()

    except Exception as e:
        print_error(f"Failed to initialize chat: {e}")
        return

    print()
    print_success("Chat session ended")


def cmd_delete(args):
    """Delete a dataset"""
    dataset = Dataset(args.name)

    if not dataset.exists():
        print_error(f"Dataset '{args.name}' not found")
        return

    print_warning(
        f"This will permanently delete the dataset '{args.name}' and all its files."
    )
    confirm = input("Type the dataset name to confirm: ").strip()

    if confirm != args.name:
        print_info("Cancelled")
        return

    import shutil

    shutil.rmtree(dataset.path)
    print_success(f"Dataset '{args.name}' deleted")


def main():
    parser = argparse.ArgumentParser(
        description="ChatVid - Memvid Dataset Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ./cli.sh setup                    # First-time setup
  ./cli.sh create my-project        # Create new dataset
  ./cli.sh list                     # List all datasets
  ./cli.sh build my-project         # Build embeddings
  ./cli.sh chat my-project          # Start chatting
  ./cli.sh append my-project        # Add new documents
  ./cli.sh rebuild my-project       # Rebuild from scratch
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Setup command
    subparsers.add_parser("setup", help="Configure API key")

    # Create command
    parser_create = subparsers.add_parser("create", help="Create new dataset")
    parser_create.add_argument("name", help="Dataset name")

    # List command
    subparsers.add_parser("list", help="List all datasets")

    # Info command
    parser_info = subparsers.add_parser("info", help="Show dataset information")
    parser_info.add_argument("name", help="Dataset name")

    # Build command
    parser_build = subparsers.add_parser(
        "build", help="Build embeddings from documents"
    )
    parser_build.add_argument("name", help="Dataset name")

    # Append command
    parser_append = subparsers.add_parser(
        "append", help="Add new documents to existing dataset"
    )
    parser_append.add_argument("name", help="Dataset name")

    # Rebuild command
    parser_rebuild = subparsers.add_parser(
        "rebuild", help="Rebuild embeddings from scratch"
    )
    parser_rebuild.add_argument("name", help="Dataset name")

    # Chat command
    parser_chat = subparsers.add_parser("chat", help="Start interactive chat")
    parser_chat.add_argument("name", help="Dataset name")

    # Delete command
    parser_delete = subparsers.add_parser("delete", help="Delete a dataset")
    parser_delete.add_argument("name", help="Dataset name")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Route to appropriate command
    commands = {
        "setup": cmd_setup,
        "create": cmd_create,
        "list": cmd_list,
        "info": cmd_info,
        "build": cmd_build,
        "append": cmd_append,
        "rebuild": cmd_rebuild,
        "chat": cmd_chat,
        "delete": cmd_delete,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
