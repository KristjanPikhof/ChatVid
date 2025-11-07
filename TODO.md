# ChatVid - TODO List & Future Enhancements

## 🚀 High Priority

### Document Format Support

- [ ] **HTML/Web Content**
  - Add BeautifulSoup4 for HTML parsing
  - Extract text from HTML files (.html, .htm)
  - Support for cleaning HTML tags and scripts
  - Optional: Preserve links and structure
  - Dependencies: `beautifulsoup4>=4.12.0`, `lxml>=4.9.0`

- [ ] **OCR Support for Scanned PDFs**
  - Integrate Tesseract OCR for image-based PDFs
  - Detect if PDF is scanned (no extractable text)
  - Automatic fallback to OCR when needed
  - Dependencies: `pytesseract>=0.3.10`, `pdf2image>=1.16.0`
  - System deps: tesseract, poppler-utils

- [ ] **RTF (Rich Text Format)**
  - Add RTF parsing support
  - Extract plain text from .rtf files
  - Dependencies: `striprtf>=0.0.26`

- [ ] **EPUB (E-books)**
  - Parse EPUB files for book content
  - Extract text from all chapters
  - Preserve chapter structure in metadata
  - Dependencies: `ebooklib>=0.18`

### Enhanced Document Processing

- [ ] **Spreadsheet Support (Excel, CSV)**
  - Extract text from Excel files (.xlsx, .xls)
  - Convert CSV to readable format
  - Option to include headers and cell descriptions
  - Dependencies: `openpyxl>=3.1.0`, `pandas>=2.0.0`

- [ ] **Presentation Support (PowerPoint)**
  - Extract text from slides (.pptx, .ppt)
  - Include slide notes and titles
  - Dependencies: `python-pptx>=0.6.21`

- [ ] **Code File Support**
  - Parse common code files (.py, .js, .java, .cpp, etc.)
  - Extract docstrings and comments
  - Optional: Include code structure (functions, classes)
  - Syntax-aware chunking for better context

- [ ] **JSON/YAML Configuration Files**
  - Parse structured data files
  - Convert to human-readable text for embedding
  - Preserve key-value relationships

## 🎯 Medium Priority

### Embedding & Search Improvements

- [ ] **True Append Support**
  - Implement incremental embedding addition
  - Avoid full rebuild when appending
  - Track which chunks belong to which files
  - Requires: Memvid API investigation or custom solution

- [ ] **Custom Chunking Strategies**
  - Sentence-based chunking (preserve sentence boundaries)
  - Paragraph-based chunking
  - Semantic chunking (split by topic)
  - Configurable chunk size per dataset
  - CLI flags: `--chunk-size`, `--chunk-strategy`

- [ ] **Multiple Embedding Models**
  - Support for different embedding models
  - Model selection per dataset
  - Options: all-MiniLM-L6-v2, all-mpnet-base-v2, instructor-large
  - CLI flag: `--embedding-model <model-name>`

- [ ] **Metadata Enrichment**
  - Extract creation date, author, title from documents
  - File-level metadata (size, type, date modified)
  - Custom metadata via config file
  - Search/filter by metadata

### Chat Enhancements

- [ ] **Multi-Turn Conversation Context**
  - Improved conversation history management
  - Context window optimization
  - Follow-up question handling

- [ ] **Citation & Source Tracking**
  - Show which document(s) answer came from
  - Include page numbers for PDFs
  - "Show source" command in chat

- [ ] **Chat Session Management**
  - Save and resume chat sessions
  - Export conversation history
  - Session statistics (questions asked, sources used)

- [ ] **Multiple LLM Support**
  - Native Google Gemini support
  - Native Anthropic Claude support
  - Local model support (Ollama, LlamaCpp)
  - Model switching per chat session

### CLI/UX Improvements

- [ ] **Interactive Dataset Selection**
  - `./cli.sh chat` without name shows menu
  - Arrow key navigation for dataset selection
  - Recently used datasets at top

- [ ] **Progress Bar Improvements**
  - Better progress indicators during build
  - ETA for long operations
  - File-by-file progress display

- [ ] **Batch Operations**
  - Build multiple datasets at once
  - Rebuild all outdated datasets
  - CLI: `./cli.sh build --all`

- [ ] **Export/Import Datasets**
  - Export dataset to portable format
  - Import datasets from other users
  - Share-friendly packaging

## 💡 Nice to Have

### Advanced Features

- [ ] **Web Scraping Integration**
  - Scrape websites and add to dataset
  - CLI: `./cli.sh add-url <dataset> <url>`
  - Recursive crawling option
  - Dependencies: `playwright>=1.40.0` or `scrapy>=2.11.0`

- [ ] **YouTube Transcript Integration**
  - Download and process YouTube video transcripts
  - CLI: `./cli.sh add-youtube <dataset> <video-url>`
  - Dependencies: `youtube-transcript-api>=0.6.0`

- [ ] **RSS Feed Monitoring**
  - Subscribe to RSS feeds
  - Automatically update dataset with new articles
  - Background sync option

- [ ] **Document Summarization**
  - Generate summaries for long documents
  - Store summaries alongside full text
  - Quick summary view in `info` command

- [ ] **Duplicate Detection**
  - Detect and skip duplicate documents
  - Content-based deduplication
  - Hash-based file tracking (already partially implemented)

- [ ] **Version Control for Datasets**
  - Track dataset versions
  - Rollback to previous versions
  - Diff between versions

### Chat Intelligence

- [ ] **Query Suggestions**
  - Suggest related questions after each answer
  - "You might also want to know..."

- [ ] **Semantic Search Refinement**
  - Rerank results with cross-encoder
  - Hybrid search (vector + keyword)
  - Filter by date/metadata during search

- [ ] **Multi-Dataset Chat**
  - Chat across multiple datasets simultaneously
  - Specify which datasets to search
  - CLI: `./cli.sh chat dataset1 dataset2 dataset3`

- [ ] **Chat Analytics**
  - Most asked questions
  - Most referenced documents
  - Search effectiveness metrics

### Performance & Optimization

- [ ] **Parallel Processing**
  - Multi-threaded document processing
  - Parallel embedding generation
  - Configurable worker count

- [ ] **Caching Layer**
  - Cache frequently accessed chunks
  - Cache embedding computations
  - LRU cache for retrieval

- [ ] **Streaming for Large Files**
  - Process files in chunks for memory efficiency
  - Stream video generation
  - Support for GB-sized documents

- [ ] **Compression Options**
  - Compressed embedding storage
  - Quantization for smaller indexes
  - Trade-off: size vs. accuracy

## 🔧 Technical Debt & Maintenance

### Code Quality

- [ ] **Unit Tests**
  - Test file processors
  - Test dataset operations
  - Test CLI commands
  - Coverage target: >80%

- [ ] **Integration Tests**
  - End-to-end workflow tests
  - Test with real documents
  - CI/CD pipeline setup

- [ ] **Error Handling Improvements**
  - More specific error messages
  - Recovery suggestions for common errors
  - Graceful degradation

- [ ] **Logging System**
  - Structured logging (JSON)
  - Log levels (DEBUG, INFO, WARN, ERROR)
  - Optional log file output
  - CLI flag: `--log-level`, `--log-file`

### Documentation

- [ ] **Video Tutorial**
  - Screen recording of full workflow
  - YouTube/Vimeo hosting

- [ ] **API Documentation**
  - Auto-generated from docstrings
  - Usage examples for each function
  - Sphinx or MkDocs

- [ ] **Contributing Guide**
  - Development setup instructions
  - Code style guide
  - PR template and guidelines

- [ ] **Troubleshooting Database**
  - Common errors and solutions
  - FAQ section
  - Community-contributed fixes

### Security & Privacy

- [ ] **Sensitive Data Detection**
  - Warn if API keys/passwords in documents
  - Optional: Redact sensitive patterns
  - PII detection and masking

- [ ] **Encryption at Rest**
  - Optional encryption for embeddings
  - Encrypted .env file storage
  - Password-protected datasets

- [ ] **Audit Log**
  - Track all dataset operations
  - User action history
  - Export audit logs

## 🌐 Platform & Deployment

### Cross-Platform Support

- [ ] **Windows Support**
  - PowerShell script version of cli.sh
  - Windows-specific path handling
  - Test on Windows 10/11

- [ ] **Docker Container**
  - Dockerfile for isolated environment
  - Docker Compose for easy deployment
  - Pre-built images on Docker Hub

- [ ] **Web Interface**
  - Flask/FastAPI web UI
  - Browser-based chat interface
  - Dataset management dashboard

### Cloud Integration

- [ ] **Cloud Storage Backend**
  - Store embeddings in S3/GCS/Azure
  - Reduce local storage requirements
  - Share datasets across machines

- [ ] **Hosted Service Option**
  - SaaS version with user accounts
  - Usage-based pricing
  - Managed infrastructure

## 📊 Analytics & Monitoring

- [ ] **Usage Statistics**
  - Track queries per dataset
  - Popular documents
  - Performance metrics

- [ ] **Quality Metrics**
  - Answer relevance scoring
  - User feedback collection
  - Continuous improvement loop

- [ ] **Cost Tracking**
  - Track API costs per dataset
  - Estimate costs before operations
  - Budget alerts

## 🎨 UI/UX Enhancements

- [ ] **Rich Terminal Output**
  - Tables for dataset listings
  - Syntax highlighting in code responses
  - Markdown rendering in terminal

- [ ] **Configuration Management**
  - Config file for default settings
  - Per-dataset configuration
  - Global config overrides

- [ ] **Themes**
  - Dark/light terminal themes
  - Custom color schemes
  - Accessibility options

## 🔌 Integration & Extensions

- [ ] **Plugin System**
  - Custom file format plugins
  - Custom embedding model plugins
  - Custom retrieval strategies

- [ ] **API Server**
  - REST API for programmatic access
  - Webhook support for automation
  - API documentation (OpenAPI/Swagger)

- [ ] **Slack/Discord Bot**
  - Chat with datasets from Slack
  - Discord integration
  - Team collaboration features

- [ ] **VS Code Extension**
  - Chat with code documentation
  - Inline code explanations
  - Context-aware code suggestions

## 📝 Notes & Ideas

### Research Areas

- [ ] **Investigate hybrid search** (combining vector + BM25)
- [ ] **Explore RAG optimization techniques**
- [ ] **Research on optimal chunk sizes** for different document types
- [ ] **Evaluate alternative embedding models** for domain-specific content
- [ ] **Study incremental learning** for embeddings

### Community Features

- [ ] **Dataset marketplace** - Share and download public datasets
- [ ] **User ratings** - Rate dataset quality and usefulness
- [ ] **Templates** - Pre-built datasets for common use cases
- [ ] **Collaboration** - Multi-user dataset editing

### Advanced AI Features

- [ ] **Question generation** - Auto-generate Q&A from documents
- [ ] **Knowledge graph** - Build relationship maps between concepts
- [ ] **Auto-tagging** - Automatic topic tagging
- [ ] **Sentiment analysis** - Analyze document sentiment
- [ ] **Entity extraction** - Extract people, places, organizations

---

## 📅 Priority Labels

- 🔥 **Critical** - Needed for production use
- ⚡ **High** - Significant impact, should do soon
- 🎯 **Medium** - Nice to have, plan for future
- 💡 **Low** - Ideas for exploration
- 🔬 **Research** - Needs investigation before implementation

## 🤝 Contributing

Want to work on something from this list? Great!

1. Check if someone is already working on it
2. Comment on the task to claim it
3. Create a feature branch
4. Submit a PR with tests and documentation
5. Tag @maintainer for review

---

## 📌 Recent Additions

- 2025-01-07: Initial TODO list created
- Add your changes here with date

---

**Last Updated:** 2025-01-07
**Status:** Active Development
**Contributors Welcome:** Yes

