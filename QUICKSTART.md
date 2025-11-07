# ChatVid Quick Start

Get up and running in 5 minutes!

## Step 1: Setup (30 seconds)

```bash
cd ChatVid
./cli.sh setup
```

When prompted:
1. Choose provider (OpenAI or OpenRouter)
2. Enter your API key
3. Done!

## Step 2: Create Dataset (10 seconds)

```bash
./cli.sh create my-docs
```

## Step 3: Add Files (1 minute)

```bash
# Copy your PDF, TXT, MD, or DOCX files to the documents folder
cp ~/Documents/*.pdf datasets/my-docs/documents/
cp ~/Documents/*.txt datasets/my-docs/documents/
```

**Supported formats:**
- PDF (`.pdf`) - Extracts text from PDFs
- Text (`.txt`) - Plain text files
- Markdown (`.md`, `.markdown`) - Markdown files
- Word (`.docx`, `.doc`) - Microsoft Word documents

## Step 4: Build Embeddings (2-5 minutes)

```bash
./cli.sh build my-docs
```

This will:
- Extract text from all documents
- Add source attribution to each chunk (fixes data mixing)
- Generate semantic embeddings
- Create searchable knowledge base

## Step 5: Chat! (instant)

```bash
./cli.sh chat my-docs
```

Ask questions about your documents! The AI will now correctly distinguish between different source files.

---

## Example Session

```bash
$ ./cli.sh setup
Choose your LLM provider:
1) OpenAI
2) OpenRouter
Enter choice (1 or 2): 1
Enter your OpenAI API key: sk-...
✓ OpenAI API key saved to .env

$ ./cli.sh create research
✓ Dataset 'research' created successfully!

$ cp ~/papers/*.pdf datasets/research/documents/

$ ./cli.sh build research
[1/5] Processing: paper1.pdf
✓ Added (12453 characters)
...
✓ Build complete!

$ ./cli.sh chat research
You: What are the main findings?
Assistant: Based on the research papers, the main findings are...
```

---

## Common Commands

```bash
./cli.sh list              # See all datasets
./cli.sh info my-docs      # Dataset details
./cli.sh append my-docs    # Add more files
./cli.sh rebuild my-docs   # Rebuild from scratch (recommended after updates)
./cli.sh chat my-docs      # Start chatting
```

## Recent Fixes & Improvements

✅ **v1.0.2** - Source attribution: Each chunk now includes filename to prevent data mixing
✅ **v1.0.1** - Increased context window: 10 chunks (was 5) for better answers
✅ **v1.0.0** - Fixed metadata parameter compatibility with memvid package

**Important:** If you built datasets before v1.0.2, rebuild them to get source attribution:
```bash
./cli.sh rebuild my-docs
```

## Get Help

```bash
./cli.sh --help           # Show all commands
./cli.sh build --help     # Command-specific help
```

**Full documentation:** See `README.md`
**Troubleshooting:** See `BUGFIX.md`, `CHAT_IMPROVEMENT.md`, `SOURCE_ATTRIBUTION_FIX.md`
