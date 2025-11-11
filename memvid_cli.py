#!/usr/bin/env python3
"""
ChatVid CLI - Memvid Dataset Management Tool

A complete CLI tool for managing document datasets with embeddings and interactive chat.

Architecture (v1.3.0+):
    - Modular plugin system for document processors (chatvid/processors/)
    - Type-safe configuration management (chatvid/config.py)
    - Legacy functions kept for backward compatibility
    - Auto-registration and dependency checking

For new format support: Create processor in chatvid/processors/
For configuration changes: Update chatvid/config.py dataclasses
"""

from __future__ import annotations

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

# Import modular components (v1.3.0+)
from chatvid.processors import ProcessorRegistry
from chatvid.config import Config

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


# ==============================================================================
# Legacy Configuration Helpers (v1.0-1.2)
# ==============================================================================
# These functions are kept for backward compatibility.
# New code should use chatvid.config.Config.from_env() instead.
# ==============================================================================


def get_env_int(key: str, default: int, min_val: int, max_val: int) -> int:
    """Get integer from environment with validation

    DEPRECATED: Use chatvid.config.Config.from_env() instead.
    Kept for backward compatibility only.
    """
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
    """Get float from environment with validation

    DEPRECATED: Use chatvid.config.Config.from_env() instead.
    Kept for backward compatibility only.
    """
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
    """Get string from environment with default

    DEPRECATED: Use chatvid.config.Config.from_env() instead.
    Kept for backward compatibility only.
    """
    value = os.getenv(key)
    if value is None or value.strip() == "":
        return default
    return value.strip()


# ============================================================================
# Interactive Menu Helper Functions
# ============================================================================

def clear_screen():
    """Clear terminal screen (cross-platform)"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_menu_header(title: str):
    """Print formatted menu header"""
    print()
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)
    print()


def pause_for_user(message: str = "Press Enter to continue..."):
    """Pause and wait for user to press Enter"""
    print()
    input(f"ℹ️  {message}")


def get_menu_choice(max_choice: int, allow_zero: bool = True, prompt: str = "Enter choice") -> int:
    """Get and validate numeric menu choice from user"""
    min_choice = 0 if allow_zero else 1

    while True:
        try:
            choice_str = input(f"\n{prompt} ({min_choice}-{max_choice}): ").strip()

            if not choice_str:
                print_warning("Please enter a number")
                continue

            choice = int(choice_str)

            if choice < min_choice or choice > max_choice:
                print_warning(f"Please enter a number between {min_choice} and {max_choice}")
                continue

            return choice

        except ValueError:
            print_warning("Please enter a valid number")
        except KeyboardInterrupt:
            print()
            print_warning("Operation cancelled")
            return 0 if allow_zero else -1


def confirm_action(prompt: str, require_name: str = None) -> bool:
    """
    Ask user to confirm an action

    Args:
        prompt: Question to ask user
        require_name: If provided, user must type this exact string to confirm

    Returns:
        True if confirmed, False otherwise
    """
    print()
    if require_name:
        print_warning(prompt)
        response = input(f"Type '{require_name}' to confirm: ").strip()
        return response == require_name
    else:
        response = input(f"{prompt} (y/n): ").strip().lower()
        return response in ['y', 'yes']


def print_dataset_list(datasets: list, with_numbers: bool = True, show_status: bool = True) -> dict:
    """
    Print formatted list of datasets

    Args:
        datasets: List of Dataset objects
        with_numbers: Show numbers for selection
        show_status: Show status indicators

    Returns:
        Dictionary mapping choice numbers to Dataset objects
    """
    if not datasets:
        print_info("No datasets found")
        print_info("Use 'Create New Dataset' to get started")
        return {}

    print()
    dataset_map = {}

    for i, dataset in enumerate(datasets, 1):
        # Get dataset info
        doc_count = len(list(dataset.documents_dir.glob("*.*"))) if dataset.documents_dir.exists() else 0
        has_embeddings = dataset.has_embeddings()

        # Build status line
        prefix = f"{i}. " if with_numbers else "  "
        status = ""

        if show_status:
            if has_embeddings:
                status = f"[✓ Built, {doc_count} docs]"
            elif doc_count > 0:
                status = f"[⚠️  Not built, {doc_count} docs]"
            else:
                status = "[📁 Empty]"

        print(f"{prefix}{dataset.name:<30} {status}")

        if with_numbers:
            dataset_map[i] = dataset

    print()
    return dataset_map


def select_dataset(purpose: str = "work with", allow_cancel: bool = True) -> 'Dataset':
    """
    Interactive dataset selection menu

    Args:
        purpose: Description of what the dataset will be used for
        allow_cancel: If True, user can cancel selection

    Returns:
        Selected Dataset object, or None if cancelled
    """
    # Get all dataset directories
    dataset_dirs = [d for d in DATASETS_DIR.iterdir() if d.is_dir()]

    if not dataset_dirs:
        print_warning(f"No datasets found to {purpose}")
        print_info("Create a new dataset first")
        return None

    # Create Dataset objects
    datasets = [Dataset(d.name) for d in sorted(dataset_dirs)]

    if len(datasets) == 1:
        # Auto-select if only one dataset
        dataset = datasets[0]
        print_info(f"Using dataset: {dataset.name}")
        return dataset

    # Multiple datasets - show selection menu
    print_menu_header(f"Select Dataset to {purpose.title()}")
    dataset_map = print_dataset_list(datasets, with_numbers=True, show_status=True)

    if allow_cancel:
        print("0. Cancel")

    choice = get_menu_choice(len(datasets), allow_zero=allow_cancel)

    if choice == 0 and allow_cancel:
        return None

    return dataset_map.get(choice)


# ==============================================================================
# Legacy Document Processing Functions (v1.0-1.2)
# ==============================================================================
# These functions are kept for backward compatibility.
# New code should use chatvid.processors.ProcessorRegistry instead.
# ==============================================================================


def read_text_file(file_path: Path) -> str:
    """Read plain text file

    DEPRECATED: Use chatvid.processors.TextProcessor instead.
    Kept for backward compatibility only.
    """
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def read_pdf_file(file_path: Path) -> str:
    """Extract text from PDF file

    DEPRECATED: Use chatvid.processors.PDFProcessor instead.
    Kept for backward compatibility only.
    """
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
    """Extract text from DOCX file

    DEPRECATED: Use chatvid.processors.DOCXProcessor instead.
    Kept for backward compatibility only.
    """
    try:
        import docx
        doc = docx.Document(file_path)
        text = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text.append(paragraph.text)
        return "\n\n".join(text)
    except ImportError:
        print_warning(f"Skipping {file_path.name} - python-docx not installed")
        return ""
    except Exception as e:
        print_error(f"Error reading DOCX {file_path.name}: {e}")
        return ""


def read_html_file(file_path: Path) -> str:
    """Extract text from HTML file

    DEPRECATED: Use chatvid.processors.HTMLProcessor instead.
    Kept for backward compatibility only.
    """
    try:
        from bs4 import BeautifulSoup

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            html_content = f.read()

        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html_content, "lxml")

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Get text and clean up whitespace
        text = soup.get_text()

        # Break into lines and remove leading/trailing whitespace
        lines = (line.strip() for line in text.splitlines())

        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))

        # Remove blank lines
        text = "\n".join(chunk for chunk in chunks if chunk)

        return text
    except ImportError:
        print_warning(f"Skipping {file_path.name} - beautifulsoup4 not installed")
        return ""
    except Exception as e:
        print_error(f"Error reading HTML {file_path.name}: {e}")
        return ""


def process_file(file_path: Path, enable_metadata: bool = True) -> Optional[str]:
    """Process a file and extract text based on extension using ProcessorRegistry

    Args:
        file_path: Path to the file to process
        enable_metadata: Whether to enrich text with metadata prefix (Phase 1 feature)

    Returns:
        Extracted text, optionally with metadata prefix
    """
    processor = ProcessorRegistry.get_processor(file_path)
    if processor:
        # Phase 1: Use metadata enrichment if processor supports it
        if enable_metadata and hasattr(processor, 'extract_with_metadata'):
            return processor.extract_with_metadata(file_path, enable_enrichment=True)
        else:
            return processor.extract_text(file_path)
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
        """Get all document files in the documents directory using ProcessorRegistry"""
        files = []
        extensions = ProcessorRegistry.get_supported_extensions()
        for ext in extensions:
            pattern = f"*{ext}"
            files.extend(self.documents_dir.glob(pattern))
        return sorted(files)

    def has_embeddings(self) -> bool:
        """Check if embeddings have been built"""
        return self.video_file.exists() and self.index_file.exists()


# ============================================================================
# Command Functions
# ============================================================================

def cmd_help(args):
    """Display comprehensive help and documentation"""
    clear_screen()
    print_header("ChatVid Help & Documentation")

    print("=" * 70)
    print("COMMAND REFERENCE")
    print("=" * 70)
    print()

    commands = [
        ("setup", "Configure API key (OpenAI or OpenRouter)",
         "./cli.sh setup"),
        ("create <name>", "Create a new dataset",
         "./cli.sh create my-project"),
        ("build <name>", "Process documents and build embeddings",
         "./cli.sh build my-project"),
        ("chat <name>", "Start interactive chat with dataset",
         "./cli.sh chat my-project"),
        ("append <name>", "Add new/modified documents to existing dataset",
         "./cli.sh append my-project"),
        ("rebuild <name>", "Rebuild dataset from scratch",
         "./cli.sh rebuild my-project"),
        ("list", "Show all datasets with status",
         "./cli.sh list"),
        ("info <name>", "Show detailed dataset information",
         "./cli.sh info my-project"),
        ("delete <name>", "Delete a dataset (requires confirmation)",
         "./cli.sh delete my-project"),
        ("help", "Show this help documentation",
         "./cli.sh help"),
    ]

    for cmd, desc, example in commands:
        print(f"  {cmd:<20} {desc}")
        print(f"  {'':20} Example: {example}")
        print()

    print("=" * 70)
    print("CONFIGURATION REFERENCE")
    print("=" * 70)
    print()
    print("Edit .env file to configure these settings:")
    print()

    config_vars = [
        ("OPENAI_API_KEY", "Your API key (sk-... or sk-or-v1-...)", "Required"),
        ("OPENAI_API_BASE", "API endpoint URL (for OpenRouter)", "Optional"),
        ("LLM_MODEL", "Model name", "gpt-4o-mini-2024-07-18"),
        ("CHUNK_SIZE", "Text chunk size (100-1000)", "300"),
        ("CHUNK_OVERLAP", "Chunk overlap (20-200)", "50"),
        ("LLM_TEMPERATURE", "Response creativity (0.0-2.0)", "0.7"),
        ("LLM_MAX_TOKENS", "Max response length (100-4000)", "1000"),
        ("CONTEXT_CHUNKS", "Retrieved chunks per query (1-20)", "10"),
        ("MAX_HISTORY", "Conversation history depth (1-50)", "10"),
    ]

    print(f"  {'Variable':<20} {'Description':<40} {'Default'}")
    print(f"  {'-'*20} {'-'*40} {'-'*15}")
    for var, desc, default in config_vars:
        print(f"  {var:<20} {desc:<40} {default}")
    print()

    print("=" * 70)
    print("WORKFLOW TUTORIALS")
    print("=" * 70)
    print()

    print("1. FIRST-TIME SETUP")
    print("   " + "-" * 66)
    print("   Step 1: Configure API")
    print("           ./cli.sh setup")
    print("           Choose provider (OpenAI or OpenRouter)")
    print("           Enter your API key")
    print()
    print("   Step 2: Create dataset")
    print("           ./cli.sh create my-docs")
    print()
    print("   Step 3: Add documents")
    print("           cp your-files.pdf datasets/my-docs/documents/")
    print()
    print("   Step 4: Build embeddings")
    print("           ./cli.sh build my-docs")
    print()
    print("   Step 5: Start chatting")
    print("           ./cli.sh chat my-docs")
    print()

    print("2. DAILY USAGE")
    print("   " + "-" * 66)
    print("   Add new documents:")
    print("           cp new-file.pdf datasets/my-docs/documents/")
    print("           ./cli.sh append my-docs")
    print()
    print("   Chat with dataset:")
    print("           ./cli.sh chat my-docs")
    print("           Type your questions, use 'exit' to quit")
    print()

    print("3. SWITCHING PROVIDERS")
    print("   " + "-" * 66)
    print("   OpenAI → OpenRouter:")
    print("           Edit .env file:")
    print("           - Uncomment: OPENAI_API_BASE=https://openrouter.ai/api/v1")
    print("           - Update: OPENAI_API_KEY=sk-or-v1-your-key")
    print("           - Change: LLM_MODEL=openai/gpt-4o")
    print()
    print("   OpenRouter → OpenAI:")
    print("           Edit .env file:")
    print("           - Comment out: # OPENAI_API_BASE=https://openrouter.ai/api/v1")
    print("           - Update: OPENAI_API_KEY=sk-your-key")
    print("           - Change: LLM_MODEL=gpt-4o-mini-2024-07-18")
    print()

    print("4. CONFIGURATION PRESETS")
    print("   " + "-" * 66)
    print("   Technical Documents:")
    print("           CHUNK_SIZE=400, CHUNK_OVERLAP=80")
    print("           LLM_TEMPERATURE=0.3, LLM_MODEL=gpt-4o")
    print()
    print("   Creative Content:")
    print("           CHUNK_SIZE=300, CHUNK_OVERLAP=50")
    print("           LLM_TEMPERATURE=1.0, LLM_MODEL=gpt-4o")
    print()
    print("   Cost Optimization:")
    print("           LLM_MODEL=gpt-4o-mini-2024-07-18")
    print("           CONTEXT_CHUNKS=7, LLM_MAX_TOKENS=500")
    print()

    print("=" * 70)
    print("TROUBLESHOOTING")
    print("=" * 70)
    print()

    issues = [
        ("401 Authentication Error",
         "- Check API key format (OpenAI: sk-..., OpenRouter: sk-or-v1-...)\n" +
         "         - Verify OPENAI_API_BASE matches your provider\n" +
         "         - Run: cat .env | grep OPENAI"),

        ("No documents found",
         "- Check files are in: datasets/<name>/documents/\n" +
         "         - Supported formats: PDF, TXT, MD, DOCX\n" +
         "         - Run: ls datasets/<name>/documents/"),

        ("Build command fails",
         "- Ensure documents contain readable text\n" +
         "         - Check CHUNK_SIZE and CHUNK_OVERLAP in .env\n" +
         "         - Try: ./cli.sh rebuild <name>"),

        ("Chat returns wrong info",
         "- Increase CONTEXT_CHUNKS in .env (try 15)\n" +
         "         - Rebuild dataset: ./cli.sh rebuild <name>\n" +
         "         - Check if documents were processed correctly"),

        ("Model not found",
         "- OpenAI format: gpt-4o-mini-2024-07-18\n" +
         "         - OpenRouter format: openai/gpt-4o\n" +
         "         - Match LLM_MODEL format to your provider"),
    ]

    for issue, solution in issues:
        print(f"  {issue}:")
        print(f"         {solution}")
        print()

    print("=" * 70)
    print("NEED MORE HELP?")
    print("=" * 70)
    print()
    print("  Documentation: Check README.md and PROVIDER_SETUP.md")
    print("  Interactive: Run './cli.sh' to use the interactive menu")
    print("  Command help: Run './cli.sh <command> --help' for specific help")
    print()

    pause_for_user()


def manage_files(dataset: Dataset):
    """Interactive file management menu for a dataset"""
    while True:
        clear_screen()
        print_menu_header(f"Manage Files: {dataset.name}")

        # Get all documents
        docs = dataset.get_documents()

        if not docs:
            print_warning("No documents in this dataset")
            print_info(f"Add files to: {dataset.documents_dir}")
            print()
            print("Options:")
            print("1. Open documents folder")
            print("0. Back to main menu")

            choice = get_menu_choice(1)
            if choice == 0:
                return
            elif choice == 1:
                import subprocess
                import platform
                folder = str(dataset.documents_dir)
                if platform.system() == "Darwin":  # macOS
                    subprocess.run(["open", folder])
                elif platform.system() == "Windows":
                    subprocess.run(["explorer", folder])
                else:  # Linux
                    subprocess.run(["xdg-open", folder])
                pause_for_user("Folder opened. Press Enter when done...")
            continue

        # Display files with numbers
        print("Documents:")
        file_map = {}
        for i, doc in enumerate(docs, 1):
            size_kb = doc.stat().st_size / 1024
            print(f"{i}. {doc.name:<40} ({size_kb:.1f} KB)")
            file_map[i] = doc

        print()
        print("Options:")
        print("a. View file details")
        print("b. Remove file from dataset")
        print("c. Open documents folder")
        print("0. Back to main menu")
        print()

        choice_str = input("Enter choice (number, a, b, c, or 0): ").strip().lower()

        if choice_str == "0":
            return
        elif choice_str == "a":
            # View file details
            file_num = get_menu_choice(len(docs), allow_zero=False, prompt="Enter file number to view")
            if file_num > 0 and file_num in file_map:
                doc = file_map[file_num]
                clear_screen()
                print_header(f"File Details: {doc.name}")
                print(f"Path: {doc}")
                print(f"Size: {doc.stat().st_size / 1024:.1f} KB")
                print(f"Type: {doc.suffix}")
                print(f"Modified: {datetime.fromtimestamp(doc.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")

                # Check if in metadata
                metadata = dataset.load_metadata()
                if str(doc) in metadata.get("files_processed", {}):
                    print(f"Status: ✓ Processed in embeddings")
                else:
                    print(f"Status: Not yet processed")

                pause_for_user()

        elif choice_str == "b":
            # Remove file
            file_num = get_menu_choice(len(docs), allow_zero=False, prompt="Enter file number to remove")
            if file_num > 0 and file_num in file_map:
                doc = file_map[file_num]
                if confirm_action(f"Remove {doc.name} from dataset?"):
                    try:
                        doc.unlink()
                        print_success(f"Removed: {doc.name}")
                        print_warning("Run 'rebuild' to update embeddings")
                        pause_for_user()
                    except Exception as e:
                        print_error(f"Failed to remove file: {e}")
                        pause_for_user()

        elif choice_str == "c":
            # Open folder
            import subprocess
            import platform
            folder = str(dataset.documents_dir)
            if platform.system() == "Darwin":  # macOS
                subprocess.run(["open", folder])
            elif platform.system() == "Windows":
                subprocess.run(["explorer", folder])
            else:  # Linux
                subprocess.run(["xdg-open", folder])
            pause_for_user("Folder opened. Press Enter when done...")


def interactive_menu():
    """Main interactive menu - entry point for menu mode"""
    while True:
        clear_screen()
        print_menu_header("ChatVid Interactive Menu")

        print("What would you like to do?")
        print()
        print(" 1. Setup / Configure API")
        print(" 2. Create New Dataset")
        print(" 3. Build Dataset (Process Documents)")
        print(" 4. Chat with Dataset")
        print(" 5. Append Documents to Dataset")
        print(" 6. Rebuild Dataset")
        print(" 7. List All Datasets")
        print(" 8. Dataset Info")
        print(" 9. Manage Dataset Files")
        print("10. Delete Dataset")
        print("11. Help & Documentation")
        print(" 0. Exit")

        choice = get_menu_choice(11)

        if choice == 0:
            print()
            print_success("Goodbye!")
            sys.exit(0)

        elif choice == 1:
            # Setup / Configure API
            clear_screen()
            class Args:
                pass
            cmd_setup(Args())
            pause_for_user()

        elif choice == 2:
            # Create New Dataset
            clear_screen()
            print_header("Create New Dataset")
            name = input("Enter dataset name (letters, numbers, hyphens, underscores): ").strip()

            if not name:
                print_warning("Dataset name cannot be empty")
                pause_for_user()
                continue

            if not name.replace("-", "").replace("_", "").isalnum():
                print_error("Dataset name can only contain letters, numbers, hyphens, and underscores")
                pause_for_user()
                continue

            class Args:
                pass
            args = Args()
            args.name = name
            cmd_create(args)
            pause_for_user()

        elif choice == 3:
            # Build Dataset
            dataset = select_dataset(purpose="build")
            if dataset:
                clear_screen()
                # Reload .env in case it was created/updated during setup
                load_dotenv(ENV_FILE)
                class Args:
                    pass
                args = Args()
                args.name = dataset.name
                args.rebuild = False
                cmd_build(args)
                pause_for_user()

        elif choice == 4:
            # Chat with Dataset
            dataset = select_dataset(purpose="chat with")
            if dataset:
                if not dataset.has_embeddings():
                    print_error(f"Dataset '{dataset.name}' has no embeddings")
                    print_info("Build the dataset first (option 3)")
                    pause_for_user()
                    continue

                clear_screen()
                # Reload .env in case it was created/updated during setup
                load_dotenv(ENV_FILE)
                class Args:
                    pass
                args = Args()
                args.name = dataset.name
                cmd_chat(args)
                # Chat has its own exit message, just return to menu
                pause_for_user()

        elif choice == 5:
            # Append Documents
            dataset = select_dataset(purpose="append to")
            if dataset:
                clear_screen()
                # Reload .env in case it was created/updated during setup
                load_dotenv(ENV_FILE)
                class Args:
                    pass
                args = Args()
                args.name = dataset.name
                cmd_append(args)
                pause_for_user()

        elif choice == 6:
            # Rebuild Dataset
            dataset = select_dataset(purpose="rebuild")
            if dataset:
                clear_screen()
                # Reload .env in case it was created/updated during setup
                load_dotenv(ENV_FILE)
                class Args:
                    pass
                args = Args()
                args.name = dataset.name
                cmd_rebuild(args)
                pause_for_user()

        elif choice == 7:
            # List All Datasets
            clear_screen()
            class Args:
                pass
            cmd_list(Args())
            pause_for_user()

        elif choice == 8:
            # Dataset Info
            dataset = select_dataset(purpose="view info for")
            if dataset:
                clear_screen()
                class Args:
                    pass
                args = Args()
                args.name = dataset.name
                cmd_info(args)
                pause_for_user()

        elif choice == 9:
            # Manage Files
            dataset = select_dataset(purpose="manage files for")
            if dataset:
                manage_files(dataset)

        elif choice == 10:
            # Delete Dataset
            dataset = select_dataset(purpose="delete", allow_cancel=True)
            if dataset:
                clear_screen()
                class Args:
                    pass
                args = Args()
                args.name = dataset.name
                cmd_delete(args)
                pause_for_user()

        elif choice == 11:
            # Help
            clear_screen()
            class Args:
                pass
            cmd_help(Args())


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

    # Use the template with proper placeholders for setup
    # (Always use this template, not .env.example, since we need {api_config} and {llm_model} placeholders)
    config_template = """# ChatVid Configuration

# ============================================================================
# API Configuration (Required)
# ============================================================================

{api_config}

# ============================================================================
# Chunking Configuration (Build Phase)
# ============================================================================

CHUNKING_STRATEGY=semantic
CHUNK_SIZE=500
CHUNK_OVERLAP=50
MIN_CHUNK_SIZE=300
MAX_CHUNK_SIZE=700
OVERLAP_SENTENCES=1
SENTENCE_BACKEND=nltk

# ============================================================================
# Document Processing Configuration (Build Phase)
# ============================================================================

MAX_SPREADSHEET_ROWS=10000
ENABLE_METADATA_ENRICHMENT=true

# ============================================================================
# Adaptive Retrieval Configuration (Chat Phase)
# ============================================================================

ENABLE_ADAPTIVE_TOP_K=true
MIN_TOP_K=5
MAX_TOP_K=25
DEBUG_ADAPTIVE=false

# ============================================================================
# LLM Configuration (Chat Phase)
# ============================================================================

LLM_MODEL={llm_model}
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=1000
CONTEXT_CHUNKS=10
MAX_HISTORY=10
"""

    if choice == "1":
        api_key = input("Enter your OpenAI API key (sk-...): ").strip()
        api_config = f"""# For OpenAI:
# Uncomment the line below to use OpenRouter or other custom endpoint:
# OPENAI_API_BASE=https://openrouter.ai/api/v1
OPENAI_API_KEY={api_key}"""
        llm_model = "gpt-4o-mini-2024-07-18"
        with open(ENV_FILE, "w") as f:
            f.write(config_template.format(api_config=api_config, llm_model=llm_model))
        print_success("OpenAI API key saved to .env")
        model_display = llm_model

    elif choice == "2":
        api_key = input("Enter your OpenRouter API key (sk-or-...): ").strip()
        api_config = f"""# For OpenRouter:
OPENAI_API_BASE=https://openrouter.ai/api/v1
OPENAI_API_KEY={api_key}
# To switch back to OpenAI, comment out OPENAI_API_BASE above"""
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

        # Get supported extensions dynamically from ProcessorRegistry
        try:
            from chatvid.processors import ProcessorRegistry
            supported_exts = sorted(ProcessorRegistry.get_supported_extensions())
            if supported_exts:
                exts_display = ", ".join(supported_exts)
                print_info(f"Supported formats: {exts_display}")
            else:
                print_info("Add document files to the documents/ folder")
        except:
            print_info("Add document files to the documents/ folder")

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

    # Phase 2: Initialize citation store for page number tracking (v1.7.0)
    from chatvid.citation_store import CitationStore
    citation_store = CitationStore(dataset.path)
    citation_store.clear()  # Start fresh for each build

    # Get chunking configuration
    try:
        config = Config.from_env()
        chunk_size = config.chunking.chunk_size
        chunk_overlap = config.chunking.chunk_overlap
        chunking_strategy = config.chunking.chunking_strategy
        min_chunk_size = config.chunking.min_chunk_size
        max_chunk_size = config.chunking.max_chunk_size
        overlap_sentences = config.chunking.overlap_sentences
    except Exception as e:
        print_warning(f"Config error: {e}, using fallback")
        chunk_size = get_env_int("CHUNK_SIZE", 300, 100, 1000)
        chunk_overlap = get_env_int("CHUNK_OVERLAP", 50, 20, 200)
        chunking_strategy = get_env_str("CHUNKING_STRATEGY", "semantic")
        min_chunk_size = get_env_int("MIN_CHUNK_SIZE", 300, 100, 1000)
        max_chunk_size = get_env_int("MAX_CHUNK_SIZE", 700, 300, 2000)
        overlap_sentences = get_env_int("OVERLAP_SENTENCES", 1, 0, 5)

    # Phase 1: Metadata enrichment configuration
    enable_metadata = os.getenv("ENABLE_METADATA_ENRICHMENT", "true").lower() == "true"

    # Phase 2: Initialize chunker based on strategy
    if chunking_strategy == "semantic":
        from chatvid.chunking import SemanticChunker
        try:
            # Use regex backend for speed (NLTK is slow on large documents)
            # Users can set SENTENCE_BACKEND env var to "nltk" or "spacy" if needed
            sentence_backend = os.getenv("SENTENCE_BACKEND", "regex")

            chunker = SemanticChunker(
                min_chunk_size=min_chunk_size,
                max_chunk_size=max_chunk_size,
                target_chunk_size=chunk_size,
                overlap_sentences=overlap_sentences,
                backend=sentence_backend  # Default: regex (fast)
            )

            # Try to detect which backend will be used
            try:
                _, backend_used = chunker._get_tokenizer()
                print_info(f"Chunking strategy: semantic (backend: {backend_used}, size range: {min_chunk_size}-{max_chunk_size})")
            except:
                print_info(f"Chunking strategy: semantic (size range: {min_chunk_size}-{max_chunk_size})")

        except RuntimeError as e:
            print_warning(f"Semantic chunking unavailable: {e}")
            print_info("Falling back to fixed chunking")
            chunking_strategy = "fixed"
            chunker = None
    else:
        chunker = None
        print_info(f"Chunking strategy: fixed (size: {chunk_size}, overlap: {chunk_overlap})")

    print_info(f"Processing {len(docs)} documents...")
    if enable_metadata:
        print_info(f"Metadata enrichment: enabled")
    print()

    files_processed = {}
    all_chunks = []  # Collect chunk text for encoder
    all_chunk_metadata = []  # Collect citation metadata parallel to chunks

    # Import processors for page-aware processing
    from chatvid.processors import ProcessorRegistry

    for i, doc_path in enumerate(docs, 1):
        print(f"[{i}/{len(docs)}] Processing: {doc_path.name}")

        # Get processor to check if page-aware processing is available
        processor = ProcessorRegistry.get_processor(doc_path)

        # Phase 2: PDF page-aware processing
        if processor and hasattr(processor, 'extract_text_with_pages') and chunking_strategy == "semantic" and chunker:
            # PDF with page tracking
            import sys
            print(f"  Extracting text with page tracking...", file=sys.stderr, flush=True)

            pages = processor.extract_text_with_pages(doc_path)

            if not pages:
                print_warning(f"  Skipped (no text extracted)")
                continue

            total_chars = sum(len(text) for _, text in pages)
            print(f"  Extracted {total_chars} characters from {len(pages)} pages", file=sys.stderr, flush=True)

            # Get document metadata
            doc_metadata = processor.get_metadata(doc_path)

            # Build metadata prefix (if enabled)
            if enable_metadata:
                prefix_parts = [f"[Document: {doc_path.name}"]
                if 'pages' in doc_metadata:
                    prefix_parts.append(f"Pages: {doc_metadata['pages']}")
                if 'author' in doc_metadata:
                    prefix_parts.append(f"Author: {doc_metadata['author']}")
                metadata_prefix = " | ".join(prefix_parts) + "]\n\n"
            else:
                metadata_prefix = ""

            # Use PageAwareSemanticChunker
            from chatvid.chunking import PageAwareSemanticChunker
            page_chunker = PageAwareSemanticChunker(
                min_chunk_size=min_chunk_size,
                max_chunk_size=max_chunk_size,
                target_chunk_size=chunk_size,
                overlap_sentences=overlap_sentences,
                backend=sentence_backend if 'sentence_backend' in locals() else "regex"
            )

            print(f"  Semantic chunking with page tracking...", file=sys.stderr, flush=True)
            try:
                page_aware_chunks = page_chunker.chunk_text_with_pages(pages)

                # Add source attribution and metadata to each chunk
                for chunk in page_aware_chunks:
                    chunk_text = f"[Source: {doc_path.name}]\n{metadata_prefix}{chunk.text}"
                    all_chunks.append(chunk_text)

                    # Store citation metadata
                    all_chunk_metadata.append({
                        'document': doc_path.name,
                        'page_start': chunk.page_start,
                        'page_end': chunk.page_end,
                        'doc_metadata': doc_metadata
                    })

                print_success(f"  Added ({total_chars} characters, {len(page_aware_chunks)} chunks with page numbers)")
            except Exception as e:
                print_warning(f"  Page-aware chunking failed: {e}, using standard approach")
                # Fallback to standard processing
                text = process_file(doc_path, enable_metadata=enable_metadata)
                file_hash = get_file_hash(doc_path)
                prefixed_text = f"[Source: {doc_path.name}]\n\n{text}"
                chunks = chunker.chunk_text(prefixed_text)
                all_chunks.extend(chunks)
                # Add metadata without page numbers
                for _ in chunks:
                    all_chunk_metadata.append({
                        'document': doc_path.name,
                        'page_start': None,
                        'page_end': None,
                        'doc_metadata': doc_metadata
                    })
                print_success(f"  Added ({len(text)} characters, {len(chunks)} chunks)")

            file_hash = get_file_hash(doc_path)
            files_processed[doc_path.name] = file_hash

        else:
            # Standard processing for non-PDF files or non-semantic chunking
            import sys
            print(f"  Extracting text...", file=sys.stderr, flush=True)
            text = process_file(doc_path, enable_metadata=enable_metadata)

            if not text or len(text.strip()) < 10:
                print_warning(f"  Skipped (no text extracted)")
                continue

            print(f"  Extracted {len(text)} characters", file=sys.stderr, flush=True)

            # Add source attribution
            file_hash = get_file_hash(doc_path)
            prefixed_text = f"[Source: {doc_path.name}]\n\n{text}"

            # Get metadata for citation store (no page numbers)
            doc_metadata = processor.get_metadata(doc_path) if processor else {}

            # Chunk text based on strategy
            if chunking_strategy == "semantic" and chunker:
                # Use semantic chunker
                try:
                    print(f"  Semantic chunking...", file=sys.stderr, flush=True)
                    chunks = chunker.chunk_text(prefixed_text)
                    all_chunks.extend(chunks)
                    # Add metadata without page numbers
                    for _ in chunks:
                        all_chunk_metadata.append({
                            'document': doc_path.name,
                            'page_start': None,
                            'page_end': None,
                            'doc_metadata': doc_metadata
                        })
                    print_success(f"  Added ({len(text)} characters, {len(chunks)} chunks)")
                except Exception as e:
                    print_warning(f"  Semantic chunking failed: {e}, using fixed")
                    encoder.add_text(prefixed_text, chunk_size=chunk_size, overlap=chunk_overlap)
                    # Note: For fixed chunking added directly, we can't track individual chunks easily
                    print_success(f"  Added ({len(text)} characters)")
            else:
                # Use fixed chunking (via MemvidEncoder)
                encoder.add_text(prefixed_text, chunk_size=chunk_size, overlap=chunk_overlap)
                # Note: For fixed chunking added directly, we can't track individual chunks easily
                print_success(f"  Added ({len(text)} characters)")

            files_processed[doc_path.name] = file_hash

    # If we used semantic chunking, add all chunks to encoder at once
    if chunking_strategy == "semantic" and all_chunks:
        print()
        print_info(f"Adding {len(all_chunks)} semantic chunks to encoder...")
        for idx, chunk in enumerate(all_chunks):
            # Add each chunk as a separate text with size=len(chunk) to prevent re-chunking
            encoder.add_text(chunk, chunk_size=len(chunk) + 1, overlap=0)

            # Save citation metadata if available
            if idx < len(all_chunk_metadata):
                metadata = all_chunk_metadata[idx]
                citation_store.add_citation(
                    chunk_id=idx,
                    document=metadata['document'],
                    page_start=metadata.get('page_start'),
                    page_end=metadata.get('page_end'),
                    doc_metadata=metadata.get('doc_metadata', {})
                )

    print()

    # Build video
    if encoder.chunks:
        print_info("Building embeddings (this may take a while)...")
        print()

        # Suppress memvid library warnings and debug output during video encoding
        import warnings
        import sys
        import io

        # Create a filter for stdout that removes debug lines
        class DebugFilter(io.TextIOBase):
            def __init__(self, original_stdout):
                self.original_stdout = original_stdout

            def write(self, text):
                # Filter out debug messages from memvid
                if not (text.startswith('🐛') or 'docker_mount=' in text):
                    self.original_stdout.write(text)
                return len(text)

            def flush(self):
                self.original_stdout.flush()

        old_stdout = sys.stdout
        sys.stdout = DebugFilter(old_stdout)

        try:
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=UserWarning, module="memvid")
                stats = encoder.build_video(
                    str(dataset.video_file), str(dataset.index_file), show_progress=True
                )
        finally:
            sys.stdout = old_stdout

        # Update metadata
        metadata["last_build"] = datetime.now().isoformat()
        metadata["files_processed"] = files_processed
        metadata["total_chunks"] = stats["total_chunks"]

        # Phase 2: Track chunking configuration for rebuild detection
        metadata["chunking_strategy"] = chunking_strategy
        metadata["chunking_config"] = {
            "strategy": chunking_strategy,
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap if chunking_strategy == "fixed" else None,
            "min_chunk_size": min_chunk_size if chunking_strategy == "semantic" else None,
            "max_chunk_size": max_chunk_size if chunking_strategy == "semantic" else None,
            "overlap_sentences": overlap_sentences if chunking_strategy == "semantic" else None,
        }

        dataset.save_metadata(metadata)

        # Phase 2: Save citation store with page tracking (v1.7.0)
        citation_store.set_chunking_config(metadata["chunking_config"])
        citation_store.save()

        # Get citation statistics
        citation_stats = citation_store.get_stats()

        print()
        print_success("Build complete!")
        print()
        print_info(f"Total chunks: {stats['total_chunks']}")
        print_info(f"Files processed: {len(files_processed)}")

        # Show citation tracking info
        if citation_stats['has_page_tracking']:
            print_info(f"Page tracking: {citation_stats['chunks_with_pages']}/{citation_stats['total_chunks']} chunks with page numbers")
        else:
            print_info(f"Page tracking: disabled (use semantic chunking + PDF files)")

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


# ============================================================================
# Citation & Source Tracking System
# ============================================================================

def extract_citations_from_chunks(chunks_data: List[Dict], citation_store=None) -> List[Dict]:
    """
    Extract citation information from retrieved chunks.

    Phase 2 (v1.7.0): Enhanced with page number support from citation store.

    Args:
        chunks_data: List of chunk dicts from search_with_metadata()
        citation_store: Optional CitationStore for page number lookup

    Returns:
        List of citation dicts with document info, scores, and page numbers
    """
    import re

    citations = []
    seen_docs = {}  # Track unique documents: doc_name -> first appearance index

    for chunk in chunks_data:
        text = chunk.get('text', '')
        score = chunk.get('score', 0.0)
        chunk_id = chunk.get('chunk_id', chunk.get('id', None))

        # Extract [Source: filename.pdf] from chunk text
        match = re.search(r'\[Source:\s*([^\]]+)\]', text)
        if match:
            doc_name = match.group(1).strip()

            # Only add first occurrence of each document
            if doc_name not in seen_docs:
                citation_num = len(citations) + 1
                seen_docs[doc_name] = citation_num

                # Extract a relevant excerpt (first ~150 chars after source tag)
                excerpt_start = match.end()
                excerpt_text = text[excerpt_start:excerpt_start + 150].strip()
                if len(text[excerpt_start:]) > 150:
                    excerpt_text += "..."

                # Get page numbers from citation store if available
                page_start = None
                page_end = None
                if citation_store and chunk_id is not None:
                    citation_meta = citation_store.get_citation(chunk_id)
                    if citation_meta:
                        page_start = citation_meta.get('page_start')
                        page_end = citation_meta.get('page_end')

                citations.append({
                    'number': citation_num,
                    'document': doc_name,
                    'chunk_id': chunk_id,
                    'score': score,
                    'excerpt': excerpt_text,
                    'page_start': page_start,
                    'page_end': page_end
                })

    return citations


def format_inline_citations(citations: List[Dict]) -> str:
    """
    Format citations as inline numbered references with full source list.

    Phase 2 (v1.7.0): Includes page numbers when available.

    Args:
        citations: List of citation dicts

    Returns:
        Formatted string with numbered sources and page numbers
    """
    if not citations:
        return ""

    # Build the sources section
    sources_lines = ["\n\n📚 Sources:"]
    show_scores = os.getenv("SHOW_RELEVANCE_SCORES", "false").lower() == "true"

    for cite in citations:
        # Format: [1] document.pdf (pp. 12-13) [score: 0.89]
        source_text = f"[{cite['number']}] {cite['document']}"

        # Add page numbers if available
        page_start = cite.get('page_start')
        page_end = cite.get('page_end')

        if page_start is not None:
            if page_end is not None and page_end != page_start:
                # Multiple pages
                source_text += f" (pp. {page_start}-{page_end})"
            else:
                # Single page
                source_text += f" (p. {page_start})"

        # Add relevance score if enabled
        if show_scores and 'score' in cite:
            source_text += f" [score: {cite['score']:.2f}]"

        sources_lines.append(source_text)

    # Add hint about /source command if enabled
    if os.getenv("SHOW_SOURCE_HINTS", "true").lower() == "true":
        sources_lines.append(f"\n💡 Use '/source N' to see full context for source [N]")

    return "\n".join(sources_lines)


def format_inline_citation_markers(citations: List[Dict]) -> str:
    """
    Generate inline citation markers like [1][2][3] for appending to response.

    Args:
        citations: List of citation dicts

    Returns:
        String like " [1][2]" or empty string
    """
    if not citations:
        return ""

    markers = "".join([f"[{cite['number']}]" for cite in citations])
    return f" {markers}"


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

    # Get configuration
    try:
        config = Config.from_env()
        api_key = config.llm.api_key
        base_url = config.llm.base_url
        llm_model = config.llm.model
        llm_temperature = config.llm.temperature
        llm_max_tokens = config.llm.max_tokens
        context_chunks = config.llm.top_k
        max_history = config.chat.max_history

        # Phase 1: Adaptive retrieval configuration
        min_top_k = config.retrieval.min_top_k
        max_top_k = config.retrieval.max_top_k
        enable_adaptive = config.retrieval.enable_adaptive_top_k
    except Exception as e:
        print_warning(f"Config error: {e}, using fallback")
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_API_BASE")
        llm_model = get_env_str("LLM_MODEL", "gpt-4o-mini-2024-07-18")
        llm_temperature = get_env_float("LLM_TEMPERATURE", 0.7, 0.0, 2.0)
        llm_max_tokens = get_env_int("LLM_MAX_TOKENS", 1000, 100, 4000)
        context_chunks = get_env_int("CONTEXT_CHUNKS", 10, 1, 20)
        max_history = get_env_int("MAX_HISTORY", 10, 1, 50)

        # Phase 1: Adaptive retrieval fallback
        min_top_k = get_env_int("MIN_TOP_K", 5, 1, 50)
        max_top_k = get_env_int("MAX_TOP_K", 25, 5, 50)
        enable_adaptive = os.getenv("ENABLE_ADAPTIVE_TOP_K", "true").lower() == "true"

    # Check for API key
    if not api_key:
        print_error("API key not configured")
        print_info("Run: ./cli.sh setup")
        return

    print_header(f"Chat: {dataset.name}")

    # Initialize chat
    try:

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

        # Initialize chat
        chat = MemvidChat(
            video_file=str(dataset.video_file),
            index_file=str(dataset.index_file),
            llm_provider="openai",
            llm_model=llm_model,
            llm_api_key=api_key,
            config=chat_config,
        )

        # Override base_url if using OpenRouter or other custom endpoints
        # This needs to be done immediately after initialization
        if base_url:
            print_info(f"Using custom API endpoint: {base_url}")

            # The memvid library wraps the OpenAI client in a provider object
            # We need to recreate the OpenAI client within the provider with the correct base_url
            if hasattr(chat.llm_client, "provider") and hasattr(chat.llm_client.provider, "client"):
                import openai
                chat.llm_client.provider.client = openai.OpenAI(
                    api_key=api_key,
                    base_url=base_url
                )
                print_info("✓ OpenRouter endpoint configured")
            else:
                print_warning("⚠ Could not configure custom endpoint - using default")

        print_success("Chat initialized successfully!")
        print()

        # Phase 1: Initialize query complexity analyzer if adaptive retrieval is enabled
        if enable_adaptive:
            from chatvid.retrieval import QueryComplexityAnalyzer
            query_analyzer = QueryComplexityAnalyzer(min_top_k=min_top_k, max_top_k=max_top_k)
            print_info(f"Adaptive retrieval enabled (range: {min_top_k}-{max_top_k} chunks)")
        else:
            query_analyzer = None
            print_info(f"Using fixed retrieval: {context_chunks} chunks")

        print()
        print_info("Type your questions and press Enter.")
        print_info("Type 'quit' or 'exit' to end the session.")
        print_info("Commands: /source N (view full context), /sources (list all sources)")

        # Check if citations are enabled
        show_citations = os.getenv("SHOW_CITATIONS", "true").lower() == "true"

        if show_citations:
            print_info("Citations enabled - sources will be shown with responses.")

        print(f"{Colors.CYAN}{'=' * 70}{Colors.NC}\n")

        # Initialize retriever for citation extraction
        from memvid import MemvidRetriever
        retriever = MemvidRetriever(
            video_file=str(dataset.video_file),
            index_file=str(dataset.index_file)
        )

        # Phase 2: Load citation store for page number tracking (v1.7.0)
        from chatvid.citation_store import CitationStore
        citation_store = CitationStore(dataset.path)

        if citation_store.exists() and citation_store.has_page_numbers():
            print_info("Page number tracking enabled for citations.")
        elif citation_store.exists():
            print_info("Citation tracking enabled (no page numbers).")
        else:
            citation_store = None  # No citation store available

        # Track last query's citations for /source command
        last_citations = []
        last_chunks_data = []

        # Start interactive chat with adaptive retrieval
        if enable_adaptive and query_analyzer:
            # Custom chat loop with per-query adaptive retrieval and citation tracking
            conversation_history = []

            while True:
                try:
                    # Get user input
                    user_input = input(f"{Colors.CYAN}You: {Colors.NC}").strip()

                    if not user_input:
                        continue

                    if user_input.lower() in ['quit', 'exit', 'q']:
                        break

                    # Handle /source N command
                    if user_input.startswith('/source'):
                        parts = user_input.split()
                        if len(parts) == 2 and parts[1].isdigit():
                            source_num = int(parts[1])
                            if 1 <= source_num <= len(last_citations):
                                citation = last_citations[source_num - 1]
                                # Find the corresponding chunk
                                chunk_found = False
                                for chunk_data in last_chunks_data:
                                    chunk_text = chunk_data.get('text', '')
                                    if f"[Source: {citation['document']}]" in chunk_text:
                                        # Display full chunk context
                                        print(f"\n{Colors.YELLOW}Source [{source_num}]: {citation['document']}", end="")
                                        if citation.get('page_start'):
                                            if citation.get('page_end') and citation['page_end'] != citation['page_start']:
                                                print(f" (pp. {citation['page_start']}-{citation['page_end']})")
                                            else:
                                                print(f" (p. {citation['page_start']})")
                                        else:
                                            print()
                                        print(f"{Colors.CYAN}{'-' * 70}{Colors.NC}")
                                        # Remove source prefix for cleaner display
                                        clean_text = chunk_text.replace(f"[Source: {citation['document']}]\n", "")
                                        print(f"{clean_text}")
                                        print(f"{Colors.CYAN}{'-' * 70}{Colors.NC}\n")
                                        chunk_found = True
                                        break
                                if not chunk_found:
                                    print_warning(f"Could not find chunk for source [{source_num}]")
                            else:
                                print_warning(f"Invalid source number. Valid range: 1-{len(last_citations)}")
                        else:
                            print_warning("Usage: /source N (where N is the source number)")
                        continue

                    # Handle /sources command
                    if user_input.startswith('/sources'):
                        if last_citations:
                            print(f"\n{Colors.YELLOW}All sources from last query:{Colors.NC}")
                            for cite in last_citations:
                                source_text = f"[{cite['number']}] {cite['document']}"
                                if cite.get('page_start'):
                                    if cite.get('page_end') and cite['page_end'] != cite['page_start']:
                                        source_text += f" (pp. {cite['page_start']}-{cite['page_end']})"
                                    else:
                                        source_text += f" (p. {cite['page_start']})"
                                print(f"  {source_text}")
                            print()
                        else:
                            print_warning("No citations available. Ask a question first.")
                        continue

                    # Analyze query complexity and adjust retrieval
                    analysis = query_analyzer.analyze(user_input)
                    adaptive_top_k = analysis['top_k']

                    # Update chat config for this query
                    chat_config["chat"]["context_chunks"] = adaptive_top_k

                    # Show analysis in debug mode
                    if os.getenv("DEBUG_ADAPTIVE", "false").lower() == "true":
                        print(f"  [Analysis: {analysis['reasoning']}, retrieving {adaptive_top_k} chunks]")

                    # Retrieve chunks with metadata for citation extraction
                    if show_citations:
                        chunks_data = retriever.search_with_metadata(user_input, top_k=adaptive_top_k)
                        citations = extract_citations_from_chunks(chunks_data, citation_store)
                        # Store for /source command
                        last_citations = citations
                        last_chunks_data = chunks_data
                    else:
                        citations = []
                        last_citations = []
                        last_chunks_data = []

                    # Get response from chat
                    response = chat.chat(user_input)

                    # Format citations
                    citation_text = format_inline_citations(citations) if show_citations else ""

                    # Display response with citations
                    print(f"\n{Colors.GREEN}Assistant:{Colors.NC} {response}{citation_text}\n")

                    # Manage conversation history
                    conversation_history.append({"role": "user", "content": user_input})
                    conversation_history.append({"role": "assistant", "content": response})

                    # Trim history to max_history turns
                    if len(conversation_history) > max_history * 2:
                        conversation_history = conversation_history[-(max_history * 2):]

                except KeyboardInterrupt:
                    print("\n")
                    break
                except EOFError:
                    print("\n")
                    break
                except Exception as e:
                    print_error(f"Error processing query: {e}")
                    continue
        else:
            # Non-adaptive chat loop with citation support
            conversation_history = []

            while True:
                try:
                    # Get user input
                    user_input = input(f"{Colors.CYAN}You: {Colors.NC}").strip()

                    if not user_input:
                        continue

                    if user_input.lower() in ['quit', 'exit', 'q']:
                        break

                    # Handle /source N command
                    if user_input.startswith('/source'):
                        parts = user_input.split()
                        if len(parts) == 2 and parts[1].isdigit():
                            source_num = int(parts[1])
                            if 1 <= source_num <= len(last_citations):
                                citation = last_citations[source_num - 1]
                                # Find the corresponding chunk
                                chunk_found = False
                                for chunk_data in last_chunks_data:
                                    chunk_text = chunk_data.get('text', '')
                                    if f"[Source: {citation['document']}]" in chunk_text:
                                        # Display full chunk context
                                        print(f"\n{Colors.YELLOW}Source [{source_num}]: {citation['document']}", end="")
                                        if citation.get('page_start'):
                                            if citation.get('page_end') and citation['page_end'] != citation['page_start']:
                                                print(f" (pp. {citation['page_start']}-{citation['page_end']})")
                                            else:
                                                print(f" (p. {citation['page_start']})")
                                        else:
                                            print()
                                        print(f"{Colors.CYAN}{'-' * 70}{Colors.NC}")
                                        # Remove source prefix for cleaner display
                                        clean_text = chunk_text.replace(f"[Source: {citation['document']}]\n", "")
                                        print(f"{clean_text}")
                                        print(f"{Colors.CYAN}{'-' * 70}{Colors.NC}\n")
                                        chunk_found = True
                                        break
                                if not chunk_found:
                                    print_warning(f"Could not find chunk for source [{source_num}]")
                            else:
                                print_warning(f"Invalid source number. Valid range: 1-{len(last_citations)}")
                        else:
                            print_warning("Usage: /source N (where N is the source number)")
                        continue

                    # Handle /sources command
                    if user_input.startswith('/sources'):
                        if last_citations:
                            print(f"\n{Colors.YELLOW}All sources from last query:{Colors.NC}")
                            for cite in last_citations:
                                source_text = f"[{cite['number']}] {cite['document']}"
                                if cite.get('page_start'):
                                    if cite.get('page_end') and cite['page_end'] != cite['page_start']:
                                        source_text += f" (pp. {cite['page_start']}-{cite['page_end']})"
                                    else:
                                        source_text += f" (p. {cite['page_start']})"
                                print(f"  {source_text}")
                            print()
                        else:
                            print_warning("No citations available. Ask a question first.")
                        continue

                    # Retrieve chunks with metadata for citation extraction
                    if show_citations:
                        chunks_data = retriever.search_with_metadata(user_input, top_k=context_chunks)
                        citations = extract_citations_from_chunks(chunks_data, citation_store)
                        # Store for /source command
                        last_citations = citations
                        last_chunks_data = chunks_data
                    else:
                        citations = []
                        last_citations = []
                        last_chunks_data = []

                    # Get response from chat
                    response = chat.chat(user_input)

                    # Format citations
                    citation_text = format_inline_citations(citations) if show_citations else ""

                    # Display response with citations
                    print(f"\n{Colors.GREEN}Assistant:{Colors.NC} {response}{citation_text}\n")

                    # Manage conversation history
                    conversation_history.append({"role": "user", "content": user_input})
                    conversation_history.append({"role": "assistant", "content": response})

                    # Trim history to max_history turns
                    if len(conversation_history) > max_history * 2:
                        conversation_history = conversation_history[-(max_history * 2):]

                except KeyboardInterrupt:
                    print("\n")
                    break
                except EOFError:
                    print("\n")
                    break
                except Exception as e:
                    print_error(f"Error processing query: {e}")
                    continue

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
  ./cli.sh                          # Start interactive menu (default)
  ./cli.sh setup                    # First-time setup
  ./cli.sh create my-project        # Create new dataset
  ./cli.sh list                     # List all datasets
  ./cli.sh build my-project         # Build embeddings
  ./cli.sh chat my-project          # Start chatting
  ./cli.sh append my-project        # Add new documents
  ./cli.sh rebuild my-project       # Rebuild from scratch
  ./cli.sh help                     # Show comprehensive help
        """,
    )

    # Add global flags
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Start interactive menu mode"
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

    # Help command
    subparsers.add_parser("help", help="Show comprehensive help and documentation")

    args = parser.parse_args()

    # Check for interactive mode flag
    if args.interactive:
        interactive_menu()
        return

    # If no command provided, start interactive menu
    if not args.command:
        interactive_menu()
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
        "help": cmd_help,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
