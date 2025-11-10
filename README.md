# ChatVid - Memvid Dataset Management CLI

A complete command-line tool for managing document datasets with AI-powered embeddings and interactive chat.

**Powered by [Memvid v1](https://github.com/Olow304/memvid)** - Turn millions of text chunks into a single, searchable video file. 🎬

## Features

<img width="425" height="422" alt="image" src="https://github.com/user-attachments/assets/bbb86ba9-9fb9-4383-9799-01ea1a6f3db3" />


- ✅ Self-contained virtual environment management
- ✅ Automatic dependency installation
- ✅ Multiple dataset support
- ✅ **11 file format support**: Documents (PDF, DOCX, RTF, TXT, MD), Spreadsheets (XLSX, XLS, CSV), Presentations (PPTX), E-books (EPUB), Web (HTML)
- ✅ Automatic embedding generation with source attribution
- ✅ Interactive AI chat with your documents
- ✅ Dataset versioning (append/rebuild)
- ✅ Simple, intuitive CLI with interactive menu mode
- ✅ Improved context retrieval (10 chunks, up from 5)
- ✅ Source file tracking to prevent data mixing
- ✅ Full environment variable configuration (chunk size, LLM model, temperature, etc.)
- ✅ **NEW**: Interactive menu system with numbered selection
- ✅ **NEW**: File management interface
- ✅ **NEW**: Comprehensive help system

## Recent Updates

#### [1.6.0] - 2025-11-10

**Major improvement to text chunking quality with sentence-boundary-aware splitting:**

##### Semantic Chunker (`chatvid/chunking.py`)
- **`SemanticChunker` class**: Respects sentence boundaries instead of arbitrary character splits
  - **Benefits**: +25% quality improvement over fixed chunking
  - Preserves complete sentences (no mid-sentence splits)
  - Better semantic coherence per chunk
  - Smart sentence-based overlap for continuity
  - Size range control: min_chunk_size (300) to max_chunk_size (700)

**Full version history:** See [CHANGELOG.md](CHANGELOG.md)

## Supported File Formats

ChatVid supports 11 file formats across 5 categories:

| Category | Formats | Extensions | Features |
|----------|---------|------------|----------|
| **Documents** | PDF, Word, RTF, Text, Markdown | `.pdf`, `.docx`, `.doc`, `.rtf`, `.txt`, `.md`, `.markdown` | Full text extraction, metadata |
| **Spreadsheets** | Excel, CSV | `.xlsx`, `.xls`, `.csv` | Multi-sheet support, markdown tables, configurable row limits |
| **Presentations** | PowerPoint | `.pptx` | Slides, speaker notes, tables |
| **E-books** | EPUB | `.epub` | EPUB2/EPUB3, chapter extraction, metadata |
| **Web Content** | HTML | `.html`, `.htm` | Clean text extraction, script/style removal |

### Format-Specific Notes

- **Spreadsheets**: Configurable row limit via `MAX_SPREADSHEET_ROWS` (default: 10,000) prevents memory issues
- **PowerPoint**: Only `.pptx` supported (not legacy `.ppt` format)
- **EPUB**: DRM-protected files not supported
- **All Formats**: Source attribution included automatically for accurate LLM responses

## System Requirements

### Python Version

ChatVid requires **Python 3.10, 3.11, 3.12, or 3.13**.

The CLI script automatically detects and validates your Python installation:
- **First run**: Detects suitable Python command (`python3` or `python`) and saves it
- **Subsequent runs**: Uses saved command for fast startup (~10ms overhead)
- **Auto-recovery**: Re-detects if saved command becomes invalid
- **Smart detection**: Prefers `python3` over `python` for better cross-platform compatibility

#### Manual Override

If you need to use a specific Python executable (e.g., for pyenv/asdf users):

```bash
export CHATVID_PYTHON_CMD=/path/to/python3.12
./cli.sh
```

#### Checking Your Python Version

```bash
python3 --version  # Should show 3.10.x, 3.11.x, 3.12.x, or 3.13.x
# OR
python --version   # If python3 is not available
```

#### Installing Python

If you don't have a compatible Python version:

- **macOS**: `brew install python@3.12`
- **Ubuntu/Debian**: `sudo apt install python3.12`
- **Windows**: `winget install Python.Python.3.12`
- **Any OS**: Download from [python.org](https://www.python.org/downloads/)
- **Version managers**: Use `pyenv`, `asdf`, or similar tools

## Quick Start

**New in v1.2.0**: Interactive menu mode! Simply run `./cli.sh` and follow the numbered menus - no commands to memorize!

### Interactive Mode (Recommended for Beginners)

```bash
cd ChatVid
./cli.sh
```

The interactive menu will guide you through:
1. **Setup** - Configure your API key
2. **Create Dataset** - Name your dataset
3. **Build** - Select dataset and process documents
4. **Chat** - Select dataset and start asking questions
5. **File Management** - View and manage files
6. **Help** - Comprehensive documentation

**Benefits**:
- No command memorization needed
- Numbered selection (just type 1, 2, 3, etc.)
- Visual dataset status indicators
- Guided workflows with validation
- Built-in help and troubleshooting

### Command-Line Mode (For Advanced Users)

#### 1. First-Time Setup

```bash
cd ChatVid
./cli.sh setup
```

This will:
- Create a virtual environment (`venv/`)
- Install all dependencies
- Prompt for your OpenAI or OpenRouter API key

#### 2. Create a Dataset

```bash
./cli.sh create my-project
```

This creates:
```
datasets/my-project/
├── documents/     # Add your files here
└── metadata.json  # Dataset tracking
```

#### 3. Add Your Documents

```bash
# Copy your files to the documents folder
cp ~/my-documents/*.pdf datasets/my-project/documents/
cp ~/my-documents/*.txt datasets/my-project/documents/
```

Supported formats:
- **PDF** (`.pdf`)
- **Text** (`.txt`)
- **Markdown** (`.md`)
- **Word** (`.docx`, `.doc`)
- **HTML** (`.html`, `.htm`)

#### 4. Build Embeddings

```bash
./cli.sh build my-project
```

This will:
- Extract text from all documents
- Add source attribution to prevent data mixing
- Generate semantic embeddings
- Create searchable knowledge base (`knowledge.mp4`)

#### 5. Start Chatting!

```bash
./cli.sh chat my-project
```

Ask questions about your documents and get AI-powered answers! The AI now correctly distinguishes between different source files.

## Complete Command Reference

### Interactive Menu Mode

#### `./cli.sh` (no arguments)
Start interactive menu with numbered selection

```bash
./cli.sh
```

**Menu Options**:
1. Setup / Configure API
2. Create New Dataset
3. Build Dataset (Process Documents)
4. Chat with Dataset
5. Append Documents to Dataset
6. Rebuild Dataset
7. List All Datasets
8. Dataset Info
9. Manage Dataset Files - **NEW!**
10. Delete Dataset
11. Help & Documentation - **NEW!**
0. Exit

**Features**:
- Dataset selection from numbered list
- File management (view, remove, open folder)
- Built-in help and tutorials
- Progress tracking and validation

---

### Setup & Configuration

#### `./cli.sh setup`
Configure your API key (first-time setup)

```bash
./cli.sh setup
```

Prompts for:
- **OpenAI** API key (https://platform.openai.com/api-keys)
- **OpenRouter** API key (https://openrouter.ai/keys)

Saves configuration to `.env` file.

#### `./cli.sh help`
Show comprehensive help documentation - **NEW!**

```bash
./cli.sh help
```

Displays:
- Command reference with examples
- Configuration variable guide
- Workflow tutorials
- Troubleshooting tips
- Configuration presets

---

### Dataset Management

#### `./cli.sh create <name>`
Create a new dataset

```bash
./cli.sh create research-papers
```

Creates folder structure at `datasets/research-papers/`

#### `./cli.sh list`
List all datasets with statistics

```bash
./cli.sh list
```

Shows:
- Dataset names
- Creation dates
- Build status
- Number of chunks and files

#### `./cli.sh info <name>`
Show detailed dataset information

```bash
./cli.sh info research-papers
```

Displays:
- Document list with sizes
- Build timestamps
- Embedding statistics
- File paths

#### `./cli.sh delete <name>`
Delete a dataset

```bash
./cli.sh delete old-project
```

Requires confirmation by typing the dataset name.

---

### Building Embeddings

#### `./cli.sh build <name>`
Build embeddings from documents

```bash
./cli.sh build research-papers
```

Processes all files in `datasets/<name>/documents/` and creates:
- `knowledge.mp4` - QR code video with embeddings
- `knowledge_index.json` - Metadata index
- `knowledge_index.faiss` - Vector search index

#### `./cli.sh append <name>`
Add new documents to existing dataset

```bash
# 1. Add new files to documents/
cp new-file.pdf datasets/research-papers/documents/

# 2. Append to embeddings
./cli.sh append research-papers
```

**Note:** Currently rebuilds entire dataset (Memvid limitation)

#### `./cli.sh rebuild <name>`
Rebuild embeddings from scratch

```bash
./cli.sh rebuild research-papers
```

Deletes existing embeddings and rebuilds from all documents.

**When to rebuild:**
- After updating to v1.0.2 (adds source attribution)
- When chat responses seem inaccurate
- After changing chunk size settings

---

### Interactive Chat

#### `./cli.sh chat <name>`
Start interactive chat session

```bash
./cli.sh chat research-papers
```

Features:
- Context-aware responses with 10-chunk retrieval window
- Semantic search across all documents
- Source attribution prevents data mixing
- Conversation history
- Type `quit` or `exit` to end

Example session:
```
You: What did Company A offer in their proposal?
Assistant: [Source: Proposal_CompanyA_3.11.pdf]
Based on the Company A proposal, they offered...

You: What about B pricing?
Assistant: [Source: Proposal_CompanyB_3.11.pdf]
According to the Company B proposal, their pricing structure...

You: quit
```

**Note:** The chat now correctly distinguishes between different source files!

---

## Complete Workflow Example

### Example: Research Paper Analysis

```bash
# 1. Setup (first time only)
./cli.sh setup
# Enter your OpenAI API key

# 2. Create dataset
./cli.sh create quantum-research

# 3. Add research papers
cp ~/Downloads/quantum-*.pdf datasets/quantum-research/documents/

# 4. Build embeddings
./cli.sh build quantum-research
# Processing 15 documents...
# Build complete!

# 5. Start chatting
./cli.sh chat quantum-research
You: What are the key breakthroughs in quantum computing?
Assistant: The research papers highlight several key breakthroughs...

# 6. Later: Add more papers
cp new-paper.pdf datasets/quantum-research/documents/
./cli.sh append quantum-research

# 7. Chat with updated knowledge
./cli.sh chat quantum-research
```

---

## Project Structure

```
ChatVid/
├── cli.sh                      # Main CLI entry point
├── memvid_cli.py              # Python implementation
├── requirements.txt           # Python dependencies
├── .env.example              # API key template
├── .env                      # Your API key (created by setup)
├── README.md                 # This file
├── venv/                     # Virtual environment (auto-created)
└── datasets/                 # All your datasets
    ├── research-papers/
    │   ├── documents/        # Your PDF, TXT, MD files
    │   ├── metadata.json     # Dataset tracking
    │   ├── knowledge.mp4     # Embeddings (QR video)
    │   ├── knowledge_index.json
    │   └── knowledge_index.faiss
    └── meeting-notes/
        └── documents/
```

---

## API Keys

### OpenAI

1. Get key: https://platform.openai.com/api-keys
2. Run `./cli.sh setup`
3. Choose option 1 (OpenAI)
4. Enter your key: `sk-...`

### OpenRouter

1. Get key: https://openrouter.ai/keys
2. Run `./cli.sh setup`
3. Choose option 2 (OpenRouter)
4. Enter your key: `sk-or-v1-...`

**Or manually edit `.env` file:**
```bash
# For OpenAI
OPENAI_API_KEY=sk-your-key

# For OpenRouter
OPENAI_API_BASE=https://openrouter.ai/api/v1
OPENAI_API_KEY=sk-or-v1-your-key
```

---

## Configuration

ChatVid is fully configurable via environment variables in the `.env` file.

### Available Settings

#### Chunking Configuration (Build Phase)

| Variable | Range | Default | Description |
|----------|-------|---------|-------------|
| `CHUNK_SIZE` | 100-1000 | 300 | Size of text chunks in characters |
| `CHUNK_OVERLAP` | 20-200 | 50 | Overlap between consecutive chunks |

**Example**: For technical documents with complex topics:
```bash
CHUNK_SIZE=400
CHUNK_OVERLAP=80
```

#### LLM Configuration (Chat Phase)

| Variable | Range | Default | Description |
|----------|-------|---------|-------------|
| `LLM_MODEL` | - | gpt-4o-mini-2024-07-18 (OpenAI)<br>openai/gpt-4o (OpenRouter) | Model to use for chat |
| `LLM_TEMPERATURE` | 0.0-2.0 | 0.7 | Response creativity level |
| `LLM_MAX_TOKENS` | 100-4000 | 1000 | Maximum response length |
| `CONTEXT_CHUNKS` | 1-20 | 10 | Chunks retrieved per query |
| `MAX_HISTORY` | 1-50 | 10 | Conversation turns remembered |

> **Note**: Setup command automatically uses the correct model based on provider choice.

**Example**: For cost optimization:
```bash
LLM_MODEL=gpt-4o-mini-2024-07-18
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=500
CONTEXT_CHUNKS=7
MAX_HISTORY=5
```

**Example**: For maximum quality:
```bash
LLM_MODEL=gpt-4o-mini-2024-07-18
LLM_TEMPERATURE=0.3
LLM_MAX_TOKENS=2000
CONTEXT_CHUNKS=15
MAX_HISTORY=20
```

### Configuration Presets

#### For Technical Documentation
```bash
CHUNK_SIZE=400
CHUNK_OVERLAP=80
LLM_MODEL=gpt-4o-mini-2024-07-18
LLM_TEMPERATURE=0.3
CONTEXT_CHUNKS=12
```

#### For Creative Content
```bash
CHUNK_SIZE=300
CHUNK_OVERLAP=50
LLM_MODEL=gpt-4o-mini-2024-07-18
LLM_TEMPERATURE=1.0
CONTEXT_CHUNKS=10
```

#### For Cost Optimization
```bash
CHUNK_SIZE=300
CHUNK_OVERLAP=40
LLM_MODEL=gpt-4o-mini-2024-07-18
LLM_MAX_TOKENS=500
CONTEXT_CHUNKS=7
```

### How to Configure

1. **During setup** (recommended):
   ```bash
   ./cli.sh setup
   ```
   Creates `.env` with all default values

2. **Manual editing**:
   ```bash
   nano .env  # or use any text editor
   ```

3. **Per-project configuration**:
   - Copy ChatVid to different directories
   - Each directory can have its own `.env` file
   - Different settings for different use cases

### When to Rebuild

After changing chunking settings (`CHUNK_SIZE`, `CHUNK_OVERLAP`), rebuild your datasets:
```bash
./cli.sh rebuild <dataset-name>
```

LLM settings (`LLM_MODEL`, `LLM_TEMPERATURE`, etc.) take effect immediately, no rebuild needed.

---

## File Format Support

| Format | Extension | Support | Notes |
|--------|-----------|---------|-------|
| PDF | `.pdf` | ✅ Full | Via PyPDF2 |
| Text | `.txt` | ✅ Full | Plain text |
| Markdown | `.md` | ✅ Full | Plain text |
| Word | `.docx` | ✅ Full | Via python-docx |
| Word (old) | `.doc` | ⚠️ Limited | May require conversion |
| HTML | `.html`, `.htm` | ✅ Full | Via BeautifulSoup4, strips tags/scripts |

---

## Troubleshooting

### "Module not found" errors

```bash
# Reinstall dependencies
./cli.sh setup
```

### "API key not configured"

```bash
# Run setup to configure
./cli.sh setup

# Or check .env file exists and has OPENAI_API_KEY=...
cat .env
```

### "No documents found"

```bash
# Make sure files are in the right place
ls datasets/my-project/documents/

# Supported extensions: .pdf, .txt, .md, .html
```

### "Embeddings not built"

```bash
# Build embeddings first
./cli.sh build my-project

# Then try chat again
./cli.sh chat my-project
```

### Chat mixing up data from different files

**Solution**: Rebuild your dataset to add source attribution (v1.0.2+)

```bash
./cli.sh rebuild my-project
```

---

## Advanced Usage

### Custom Chunk Sizes
Adjust document chunk sizes in the `.env` file:
```
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```
After modifying these values, rebuild datasets:
```
./cli.sh rebuild <dataset_name>
```

### Model Configuration
Edit `.env` to define API source and model:
```
OPENAI_API_KEY=sk-your-key
```
For OpenRouter integration:
```
OPENAI_API_BASE=https://openrouter.ai/api/v1
OPENAI_API_KEY=sk-or-v1-your-key
LLM_MODEL=openai/gpt-4o
```
Examples of alternative models:
```
LLM_MODEL=anthropic/claude-4.5-haiku
LLM_MODEL=google/gemini-pro-2.5
```

### Multiple Projects

Each dataset is independent:
```bash
./cli.sh create work-docs
./cli.sh create personal-notes
./cli.sh create research-papers

# Each has its own embeddings and chat
./cli.sh chat work-docs
./cli.sh chat personal-notes
```

---

## How It Works

1. **Text Extraction**: Reads PDF/TXT/MD/HTML files and extracts text
2. **Source Attribution**: Prepends `[Source: filename.pdf]` to each document (v1.0.2+)
3. **Chunking**: Splits text into overlapping chunks (~300 chars with 50 char overlap)
4. **Embeddings**: Generates semantic vectors using sentence-transformers (all-MiniLM-L6-v2)
5. **QR Encoding**: Encodes chunks as QR codes
6. **Video Creation**: Creates MP4 video where each frame is a QR code
7. **Vector Index**: Builds FAISS index for fast similarity search
8. **Chat**: Retrieves 10 most relevant chunks and sends to LLM for contextual answers

---

## Performance

### Build Times (approximate)
- 10 pages: ~30 seconds
- 100 pages: ~3 minutes
- 1000 pages: ~20 minutes

### Chat Response Times
- Search: <2 seconds for 1M chunks
- LLM response: 2-5 seconds (depends on model)

### Storage
- 10K chunks: ~20MB video + ~15MB index
- Text compression: ~10:1 ratio

---

## Tips & Best Practices

1. **Organize by topic**: Create separate datasets for different subjects
2. **Rebuild after updates**: Run `./cli.sh rebuild <name>` after updating ChatVid
3. **Clean documents**: Remove headers/footers for better results
4. **Chunk size**: Use larger chunks (400-500) for technical docs, smaller (200-300) for mixed content
5. **API costs**: Use GPT-4o-mini (current default) for cost efficiency
6. **Backup**: Keep original documents separate from datasets/
7. **File naming**: Use descriptive filenames - they appear in source attribution
8. **Context window**: 10 chunks is optimal; increase in `memvid_cli.py` line 527 if needed

---

## Limitations & Known Issues

- **Append**: Currently rebuilds entire dataset (Memvid API limitation)
- **Binary files**: Only text-based formats supported
- **OCR**: Scanned PDFs require pre-processing with Tesseract (see TODO.md)
- **Large files**: Very large PDFs (>100MB) may be slow to process
- **API costs**: Chat requires API key with credits
- **Metadata**: memvid doesn't support chunk metadata - workaround: source attribution in text
- **Page numbers**: Not yet tracked for PDFs (planned in TODO.md)

---

## Dependencies

All automatically installed by `./cli.sh setup`:

**Core:**
- **`memvid>=0.1.3`** - [Memvid v1](https://github.com/Olow304/memvid) - Core embedding storage and semantic search engine

**Document Processing:**
- `PyPDF2>=3.0.1` - PDF text extraction
- `python-docx>=0.8.11` - Word document support
- `beautifulsoup4>=4.12.0` - HTML/web content parsing
- `lxml>=4.9.0` - HTML parser backend

**API & Configuration:**
- `openai>=1.0.0` - LLM integration (OpenAI and OpenRouter)
- `python-dotenv>=1.0.0` - Environment variable management

---

## Support

**Get API Keys:**
- OpenAI: https://platform.openai.com/api-keys
- OpenRouter: https://openrouter.ai/keys

**Memvid Documentation:**
- GitHub: https://github.com/olow304/memvid

**Issues:**
- Check `./cli.sh list` to verify datasets
- Check `./cli.sh info <name>` for details
- Ensure API key is set in `.env`
- Run `./cli.sh setup` to reconfigure

---

## Built With Memvid

**ChatVid** is powered by [**Memvid v1**](https://github.com/Olow304/memvid) - an innovative library that turns millions of text chunks into a single, searchable video file.

### What is Memvid?

Memvid compresses an entire knowledge base into MP4 files while keeping millisecond-level semantic search. Think of it as **SQLite for AI memory** - portable, efficient, and self-contained.

**Key Features:**
- 📦 **50-100× smaller storage** than traditional vector databases
- 🎬 **Encodes text as QR codes** in video frames
- 🚀 **Zero infrastructure** required - just video files
- 🔍 **Millisecond-level semantic search**
- 💾 **Portable and self-contained**

**Learn more:**
- GitHub: https://github.com/Olow304/memvid
- PyPI: https://pypi.org/project/memvid/
- License: MIT
- Author: [Olow304](https://github.com/Olow304)

**Why Memvid?**

ChatVid leverages Memvid's unique approach to storing embeddings as video files, making your document knowledge bases portable, efficient, and requiring zero database infrastructure. The entire dataset fits in a single `.mp4` file!

---

## Acknowledgments

- **[Memvid v1](https://github.com/Olow304/memvid)** by [Olow304](https://github.com/Olow304) - The core technology that makes ChatVid possible
- OpenAI - API for embeddings and chat completions
- OpenRouter - Alternative API provider supporting multiple models

---

## License

MIT License

Copyright (c) 2025 Esmaabi (ChatVid)

This project is built upon and complies with the MIT License of the Memvid library:
- Memvid v1: Copyright (c) 2025 Olow304

See [LICENSE](LICENSE) for full details.

---

## Quick Reference Card

```bash
# Interactive Menu (Recommended for beginners)
./cli.sh                       # Start interactive menu - NEW in v1.2.0!

# Help & Documentation
./cli.sh help                  # Comprehensive help - NEW!
./cli.sh --help                # Quick command reference

# Setup
./cli.sh setup                 # First-time configuration

# Datasets
./cli.sh create <name>         # Create new
./cli.sh list                  # Show all
./cli.sh info <name>           # Details
./cli.sh delete <name>         # Remove

# Documents
# → Add files to: datasets/<name>/documents/

# Embeddings
./cli.sh build <name>          # Initial build
./cli.sh append <name>         # Add more docs
./cli.sh rebuild <name>        # Start fresh

# Chat
./cli.sh chat <name>           # Interactive Q&A

# Configuration
# → Edit .env to change: chunk size, model, temperature, etc.
```

---

**Ready to get started?**

- **Beginners**: Run `./cli.sh` for interactive menu 🎯
- **Advanced**: Run `./cli.sh setup` for command-line mode 🚀
