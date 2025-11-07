# Changelog

All notable changes to ChatVid will be documented in this file.

## [1.3.0] - 2025-01-07
### Added - HTML/Web Content Support
- **HTML Support**: ChatVid now supports `.html` and `.htm` files as input for dataset building and chat.
- **Dependencies**:
  - `beautifulsoup4>=4.12.0` – HTML parsing and text extraction
  - `lxml>=4.9.0` – High-performance parsing backend
- **New Functionality (`memvid_cli.py`)**:
  - Added optional `HTML_SUPPORT` flag for conditional import of HTML parsing modules.
  - Implemented `read_html_file()` (lines 343–375):
    - Parses HTML via BeautifulSoup using the `lxml` parser.
    - Removes `<script>` and `<style>` elements.
    - Extracts plain text content from remaining nodes.
    - Normalizes whitespace and preserves layout where meaningful.
  - Updated `process_file()` to route and handle `.html` / `.htm` extensions.
  - Included HTML file patterns in `Dataset.get_documents()` glob expansion.

### Documentation
- **README.md**
  - Expanded supported file formats to include HTML.
  - Updated dependency table with BeautifulSoup4 and lxml.
  - Clarified system requirements for optional components.

### Features
- ✅ HTML and web-page text extraction
- ✅ Automatic removal of non-content elements (`script`, `style`)
- ✅ Clean text normalization for readability
- ✅ Structural preservation of nested content
- ✅ Functional for both `.html` and `.htm` extensions
- ✅ Graceful degradation if optional dependencies not present

### Benefits
- Enables integration of saved web pages into ChatVid datasets.
- Uniform chat access across PDFs, DOCX, TXT, MD, and now HTML files.
- No config changes required for existing datasets.

### Breaking Changes
None – fully backward compatible with v1.2.0.

## [1.2.0] - 2025-01-07

### Added - Interactive Menu System
- **Interactive Menu Mode**: Comprehensive menu-driven interface with numbered selection
- **Default Behavior**: Running `./cli.sh` with no arguments now starts interactive menu
- **Dataset Selection**: Choose datasets from numbered list instead of typing names
- **File Management**: New interactive file browser to view, remove, and manage files
- **Help Command**: New `./cli.sh help` command with comprehensive documentation
- **Menu Helper Functions**: `clear_screen()`, `print_menu_header()`, `pause_for_user()`, `get_menu_choice()`, `confirm_action()`, `print_dataset_list()`, `select_dataset()`
- **Auto-Selection**: Single dataset automatically selected without prompting
- **Status Indicators**: Visual indicators for dataset state (✓ Built, ⚠️ Not built, 📁 Empty)
- **Progress Feedback**: Real-time feedback for long-running operations
- **Folder Integration**: Open documents folder in system file manager (macOS/Windows/Linux)

### Changed
- `main()`: Now starts interactive menu when no command provided
- `main()`: Added `--interactive` flag for explicit menu mode
- `cli.sh`: Removed automatic `--help` display, delegates to Python for no-args behavior
- All command functions: Compatible with both CLI and interactive menu invocation
- Argument parser: Added help subcommand to routing table

### Menu Options
1. **Setup / Configure API** - Interactive API configuration wizard
2. **Create New Dataset** - Guided dataset creation with validation
3. **Build Dataset** - Select dataset from list, process documents
4. **Chat with Dataset** - Select dataset and start interactive chat
5. **Append Documents** - Select dataset and add new/modified files
6. **Rebuild Dataset** - Select dataset and rebuild from scratch
7. **List All Datasets** - View all datasets with status
8. **Dataset Info** - Select dataset and view detailed information
9. **Manage Dataset Files** - Interactive file browser and management
10. **Delete Dataset** - Select dataset and delete with confirmation
11. **Help & Documentation** - Comprehensive help system
0. **Exit** - Quit interactive menu

### File Management Features
- **View File Details**: Size, type, modified date, processing status
- **Remove Files**: Delete files from dataset with confirmation
- **Open Folder**: Launch system file manager to documents directory
- **File List**: Numbered list with sizes for easy selection

### Help System
- **Command Reference**: All commands with syntax and examples
- **Configuration Guide**: Environment variable reference table
- **Workflow Tutorials**: Step-by-step guides for common tasks
- **Troubleshooting**: Common issues and solutions
- **Configuration Presets**: Recommended settings for different use cases

### Benefits
- ✅ **Beginner-Friendly**: No need to memorize commands
- ✅ **Zero Dependencies**: Uses native Python input(), works everywhere
- ✅ **Fully Backward Compatible**: All existing CLI commands work unchanged
- ✅ **Discoverable**: Easy to explore features through menus
- ✅ **Validated Input**: Clear error messages and re-prompting
- ✅ **Progress Tracking**: Visual feedback for operations
- ✅ **File Management**: Manage files without leaving CLI

### Documentation
- Added INTERACTIVE_MENU.md - Complete interactive menu guide
- Added HELP_REFERENCE.md - Comprehensive command and configuration reference
- Updated examples in main epilog to show interactive menu

### Breaking Changes
None - fully backward compatible with v1.1.0 and earlier

---

## [1.1.0] - 2025-01-07

### Added
- **Environment Variable Configuration**: Complete `.env` file support for all settings
- **Chunking Configuration**: `CHUNK_SIZE` and `CHUNK_OVERLAP` environment variables
- **LLM Configuration**: Environment variables for model, temperature, max tokens, context chunks, and history
- **Validation Helpers**: Three new helper functions (`get_env_int`, `get_env_float`, `get_env_str`) with validation
- **Auto-Configuration**: `./cli.sh setup` now creates complete `.env` with all default values
- **Provider-Specific Defaults**: Setup automatically uses correct model for OpenAI vs OpenRouter
- **Configuration Display**: Build and chat commands now show active configuration settings

### Changed
- `cmd_build`: Now reads chunk settings from environment instead of hardcoded values
- `cmd_chat`: Now reads LLM parameters from environment instead of hardcoded values
- `cmd_chat`: Fixed OpenRouter integration by recreating OpenAI client with correct base_url
- `cmd_setup`: Generates full `.env` file with provider-specific defaults
  - OpenAI setup → uses `gpt-4o-mini-2024-07-18`
  - OpenRouter setup → uses `openai/gpt-4o` (correct format for OpenRouter)
- `.env.example`: Expanded with comprehensive documentation and usage examples

### Environment Variables Added

| Variable | Default | Range | Phase |
|----------|---------|-------|-------|
| `CHUNK_SIZE` | 300 | 100-1000 | Build |
| `CHUNK_OVERLAP` | 50 | 20-200 | Build |
| `LLM_MODEL` | gpt-4o-mini-2024-07-18 | - | Chat |
| `LLM_TEMPERATURE` | 0.7 | 0.0-2.0 | Chat |
| `LLM_MAX_TOKENS` | 1000 | 100-4000 | Chat |
| `CONTEXT_CHUNKS` | 10 | 1-20 | Chat |
| `MAX_HISTORY` | 10 | 1-50 | Chat |

### Benefits
- ✅ No code edits needed for common configuration changes
- ✅ Easy experimentation with different settings
- ✅ Per-project configuration support
- ✅ Automatic validation with helpful warnings
- ✅ Backward compatible (uses defaults if env vars not set)

### Fixed
- **OpenRouter Integration**: Chat now works correctly with OpenRouter by recreating the OpenAI client with proper base_url
- Previously caused 401 authentication errors when using OpenRouter API keys

### Breaking Changes
None - fully backward compatible

### Documentation
- Added comprehensive "Configuration" section to README.md
- Added configuration presets for different use cases
- Updated QUICKSTART.md with configuration info
- Enhanced `.env.example` with detailed comments
- Added PROVIDER_SETUP.md - Complete guide for OpenAI vs OpenRouter
- Added OPENROUTER_FIX.md - Technical details of OpenRouter fix

## [1.0.2] - 2025-01-07

### Fixed
- **Data Mixing Issue**: Chat was returning information from wrong source files
  - Root cause: No source attribution in chunks
  - Solution: Prepend `[Source: filename.pdf]` to each document before chunking
  - Impact: AI can now correctly distinguish between different documents
  - Files modified: `memvid_cli.py` (line 390)

### Changed
- All chunks now include source filename for accurate attribution
- Improved answer accuracy when asking about specific documents

### Action Required
- **Users must rebuild existing datasets** to get source attribution:
  ```bash
  ./cli.sh rebuild <dataset-name>
  ```

## [1.0.1] - 2025-01-07

### Fixed
- **Poor Chat Responses**: Chat wasn't finding relevant information even though documents were indexed
  - Root cause: Default `context_chunks` setting was only 5 chunks
  - Solution: Increased to 10 chunks for better context coverage
  - Impact: Doubled context window for more complete answers
  - Files modified: `memvid_cli.py` (line 527)

### Changed
- Context retrieval window: 5 chunks → 10 chunks
- LLM max tokens: default → 1000 tokens
- LLM temperature: default → 0.7 for better balance

### Added
- Configuration tips for further customization

## [1.0.0] - 2025-01-07

### Fixed
- **Build Command Error**: `TypeError: MemvidEncoder.add_text() got an unexpected keyword argument 'metadata'`
  - Root cause: Assumed memvid supported metadata parameter, but actual API doesn't
  - Solution: Removed metadata parameter from `add_text()` call
  - Impact: Build command now works correctly
  - Files modified: `memvid_cli.py` (line 389-395)

### Changed
- File tracking moved to `metadata.json` instead of embedded metadata
- Hash-based file change detection still works correctly


### Initial Release Features
- ✅ Self-contained virtual environment management
- ✅ Automatic dependency installation
- ✅ Multiple dataset support
- ✅ Multi-format file support (PDF, TXT, MD)
- ✅ Automatic embedding generation
- ✅ Interactive AI chat
- ✅ Dataset versioning (append/rebuild)
- ✅ Simple CLI interface

---

## Version History Summary
| Version | Date | Key Changes |
|----------|------|-------------|
| 1.3.0 | 2025-01-07 | HTML/Web content parsing support via BeautifulSoup4 + lxml |
| 1.2.0 | 2025-01-07 | Interactive menu system with file management |
| 1.1.0 | 2025-01-07 | Environment variable configuration and OpenRouter fix |
| 1.0.2 | 2025-01-07 | Source attribution fix |
| 1.0.1 | 2025-01-07 | Context window improvement |
| 1.0.0 | 2025-01-07 | Initial release |

---

## Breaking Changes

### v1.0.2
- **Action Required**: Rebuild existing datasets to get source attribution
- **Command**: `./cli.sh rebuild <dataset-name>`
- **Why**: Source attribution is added during the build process, not retroactively

### v1.0.0
- **Initial release**: No breaking changes

---

## Upgrade Guide

### From v1.0.1 to v1.0.2
```bash
# Rebuild all datasets to add source attribution
./cli.sh rebuild dataset1
./cli.sh rebuild dataset2
# ... for each dataset
```

### From v1.0.0 to v1.0.1
- No action required - context improvement is automatic

### New Installation
```bash
cd ChatVid
./cli.sh setup
./cli.sh create my-dataset
# Add documents to datasets/my-dataset/documents/
./cli.sh build my-dataset
./cli.sh chat my-dataset
```

---

## Future Releases

See `TODO.md` for planned features:
- HTML/OCR support
- True append functionality
- Citation tracking with page numbers
- Spreadsheet and presentation support
- Multi-dataset chat
- And 100+ more features!

---

## Documentation

- **README.md**: Complete user guide
- **TODO.md**: Future features and enhancements

---

**Last Updated**: 2025-01-07
