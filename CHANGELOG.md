# Changelog

All notable changes to ChatVid will be documented in this file.

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

### Breaking Changes
None - fully backward compatible

### Documentation
- Added comprehensive "Configuration" section to README.md
- Added configuration presets for different use cases
- Updated QUICKSTART.md with configuration info
- Enhanced `.env.example` with detailed comments

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

### Added
- `SOURCE_ATTRIBUTION_FIX.md` - Detailed documentation of the fix

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
- `CHAT_IMPROVEMENT.md` - Detailed documentation of context improvements
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

### Added
- `BUGFIX.md` - Detailed documentation of the metadata parameter fix
- Workaround documentation for metadata limitations

### Initial Release Features
- ✅ Self-contained virtual environment management
- ✅ Automatic dependency installation
- ✅ Multiple dataset support
- ✅ Multi-format file support (PDF, TXT, MD, DOCX)
- ✅ Automatic embedding generation
- ✅ Interactive AI chat
- ✅ Dataset versioning (append/rebuild)
- ✅ Simple CLI interface

---

## Version History Summary

| Version | Date | Key Changes |
|---------|------|-------------|
| 1.0.2 | 2025-01-07 | Source attribution fix - prevents data mixing |
| 1.0.1 | 2025-01-07 | Context window improvement - 10 chunks instead of 5 |
| 1.0.0 | 2025-01-07 | Initial release with metadata parameter fix |

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
- **QUICKSTART.md**: 5-minute setup guide
- **TODO.md**: Future features and enhancements
- **BUGFIX.md**: v1.0.0 metadata parameter fix
- **CHAT_IMPROVEMENT.md**: v1.0.1 context window improvement
- **SOURCE_ATTRIBUTION_FIX.md**: v1.0.2 data mixing fix

---

**Last Updated**: 2025-01-07
