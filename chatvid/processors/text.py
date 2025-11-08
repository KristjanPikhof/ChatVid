"""
Text and Markdown file processor.

Handles plain text files (.txt) and Markdown files (.md, .markdown).
"""

from pathlib import Path
from .base import DocumentProcessor, ProcessorRegistry


@ProcessorRegistry.register
class TextProcessor(DocumentProcessor):
    """Processor for plain text and Markdown files"""

    name = "Text/Markdown"
    extensions = [".txt", ".md", ".markdown"]
    dependencies = []  # No external dependencies needed

    def extract_text(self, file_path: Path) -> str:
        """Read plain text file.

        Args:
            file_path: Path to the text file

        Returns:
            Contents of the file as a string
        """
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception as e:
            # Import here to avoid circular dependency
            import sys
            print(f"Error reading text file {file_path.name}: {e}", file=sys.stderr)
            return ""
