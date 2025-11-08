"""
HTML file processor.

Extracts text from HTML and HTM files using BeautifulSoup4.
Automatically removes script and style tags.
"""

from pathlib import Path
from .base import DocumentProcessor, ProcessorRegistry


@ProcessorRegistry.register
class HTMLProcessor(DocumentProcessor):
    """Processor for HTML files"""

    name = "HTML Document"
    extensions = [".html", ".htm"]
    dependencies = ["bs4"]  # BeautifulSoup4

    def extract_text(self, file_path: Path) -> str:
        """Extract text from HTML file.

        Removes script and style tags and extracts clean text content.

        Args:
            file_path: Path to the HTML file

        Returns:
            Extracted text with scripts/styles removed and whitespace normalized
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
        except Exception as e:
            # Import here to avoid circular dependency
            import sys
            print(f"Error reading HTML {file_path.name}: {e}", file=sys.stderr)
            return ""
