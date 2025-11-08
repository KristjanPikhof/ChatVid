# Document Processors

This directory contains document processors for extracting text from various file formats.

## Architecture

The processor system uses a **plugin architecture** with automatic registration. Each processor:

1. Inherits from `DocumentProcessor` abstract base class
2. Is decorated with `@ProcessorRegistry.register`
3. Auto-registers if its dependencies are available
4. Provides text extraction for specific file formats

## Adding a New Document Format

To add support for a new format, create a single file in this directory:

### Step 1: Create the Processor File

Create `chatvid/processors/yourformat.py`:

```python
"""
Your Format processor.

Brief description of what this processor does.
"""

from pathlib import Path
from .base import DocumentProcessor, ProcessorRegistry


@ProcessorRegistry.register
class YourFormatProcessor(DocumentProcessor):
    """Processor for Your Format files"""

    name = "Your Format"  # Human-readable name
    extensions = [".yourext", ".alt"]  # Supported extensions
    dependencies = ["yourlib"]  # Required packages (or [] if none)

    def extract_text(self, file_path: Path) -> str:
        """Extract text from your format.

        Args:
            file_path: Path to the file

        Returns:
            Extracted text as a string
        """
        try:
            import yourlib  # Import inside method

            # Your extraction logic here
            text = yourlib.extract(file_path)
            return text

        except Exception as e:
            import sys
            print(f"Error reading {file_path.name}: {e}", file=sys.stderr)
            return ""

    def get_metadata(self, file_path: Path) -> dict:
        """Optional: Extract metadata.

        Args:
            file_path: Path to the file

        Returns:
            Dictionary with metadata (e.g., {'pages': 10})
        """
        return {}  # Return empty dict if no metadata
```

### Step 2: Register the Processor

Add import to `chatvid/processors/__init__.py`:

```python
from .yourformat import YourFormatProcessor

__all__ = [
    # ... existing processors
    "YourFormatProcessor",
]
```

### Step 3: Add Dependencies

Add required packages to `requirements.txt`:

```
yourlib>=1.0.0
```

**That's it!** The processor will auto-register and start working immediately.

## Examples

### EPUB E-book Processor

```python
from pathlib import Path
from .base import DocumentProcessor, ProcessorRegistry


@ProcessorRegistry.register
class EPUBProcessor(DocumentProcessor):
    """Processor for EPUB e-books"""

    name = "EPUB E-book"
    extensions = [".epub"]
    dependencies = ["ebooklib", "bs4"]

    def extract_text(self, file_path: Path) -> str:
        try:
            import ebooklib
            from ebooklib import epub
            from bs4 import BeautifulSoup

            book = epub.read_epub(str(file_path))
            text = []

            for item in book.get_items():
                if item.get_type() == ebooklib.ITEM_DOCUMENT:
                    soup = BeautifulSoup(item.get_content(), 'html.parser')
                    text.append(soup.get_text())

            return "\n\n".join(text)

        except Exception as e:
            import sys
            print(f"Error reading EPUB {file_path.name}: {e}", file=sys.stderr)
            return ""
```

### CSV/Excel Processor

```python
from pathlib import Path
from .base import DocumentProcessor, ProcessorRegistry


@ProcessorRegistry.register
class ExcelProcessor(DocumentProcessor):
    """Processor for Excel files"""

    name = "Excel Spreadsheet"
    extensions = [".xlsx", ".xls", ".csv"]
    dependencies = ["pandas"]

    def extract_text(self, file_path: Path) -> str:
        try:
            import pandas as pd

            # Read file based on extension
            if file_path.suffix == ".csv":
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)

            # Convert to readable text format
            text = df.to_string()
            return text

        except Exception as e:
            import sys
            print(f"Error reading {file_path.name}: {e}", file=sys.stderr)
            return ""
```

## Best Practices

### 1. Error Handling

Always wrap extraction logic in try/except:

```python
def extract_text(self, file_path: Path) -> str:
    try:
        # extraction logic
        return text
    except Exception as e:
        import sys
        print(f"Error: {e}", file=sys.stderr)
        return ""  # Return empty string on error
```

### 2. Import Dependencies Inside Methods

Import heavy dependencies inside methods, not at module level:

```python
def extract_text(self, file_path: Path) -> str:
    import heavylib  # Import here, not at top
    return heavylib.process(file_path)
```

This allows:
- Faster startup when dependency not installed
- Graceful degradation

### 3. Handle Encoding Issues

Use `encoding="utf-8", errors="ignore"` when opening text files:

```python
with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()
```

### 4. Normalize Whitespace

Clean up extracted text:

```python
text = extracted_text.strip()  # Remove leading/trailing whitespace
text = "\n".join(line.strip() for line in text.splitlines() if line.strip())  # Remove blank lines
```

### 5. Return Empty String on Failure

Never return `None` - always return empty string `""` on error.

## Testing Your Processor

1. Create a test file in the format you're adding
2. Place it in `datasets/test/documents/`
3. Run build: `./cli.sh build test`
4. Check if text was extracted correctly

## Available Processors

| Processor | Extensions | Dependencies | Status |
|-----------|------------|--------------|--------|
| Text | `.txt`, `.md`, `.markdown` | None | ✅ Active |
| PDF | `.pdf` | `PyPDF2` | ✅ Active |
| Word | `.docx`, `.doc` | `python-docx` | ✅ Active |
| HTML | `.html`, `.htm` | `beautifulsoup4`, `lxml` | ✅ Active |

## Troubleshooting

### Processor Not Registering

Check:
1. Is the file in `chatvid/processors/` directory?
2. Is it imported in `__init__.py`?
3. Are dependencies installed? (`pip install dependency`)
4. Does `@ProcessorRegistry.register` decorator exist?

### Dependency Check Failing

The `is_available()` method checks if dependencies can be imported. If a dependency is listed but not installed, the processor won't register.

### Testing Processor Registration

```python
from chatvid.processors import ProcessorRegistry

# List all registered processors
for ext, processor in ProcessorRegistry.list_processors().items():
    print(f"{ext}: {processor.name}")

# Get supported extensions
print(ProcessorRegistry.get_supported_extensions())
```

## Contributing

When adding a processor:

1. Create the processor file with clear documentation
2. Add comprehensive error handling
3. Test with sample files
4. Update this README with the new format
5. Add dependencies to `requirements.txt`
6. Update CLAUDE.md if needed

## Questions?

Check `base.py` for the `DocumentProcessor` interface definition.
