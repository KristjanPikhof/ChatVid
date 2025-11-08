"""
EPUB (E-book) file processor.

Extracts text from EPUB e-books using ebooklib and BeautifulSoup.
Supports both EPUB2 and EPUB3 formats.
"""

from pathlib import Path
from .base import DocumentProcessor, ProcessorRegistry


@ProcessorRegistry.register
class EPUBProcessor(DocumentProcessor):
    """Processor for EPUB e-book files"""

    name = "EPUB E-book"
    extensions = [".epub"]
    dependencies = ["ebooklib", "bs4"]

    def extract_text(self, file_path: Path) -> str:
        """Extract text from EPUB file.

        Extracts text from all chapters/documents in the e-book,
        with clear separators between chapters.

        Args:
            file_path: Path to the EPUB file

        Returns:
            Extracted text from all chapters
        """
        try:
            import ebooklib
            from ebooklib import epub
            from bs4 import BeautifulSoup

            # Read the EPUB file
            book = epub.read_epub(str(file_path))
            text_parts = []
            chapter_num = 0

            # Extract text from all document items
            for item in book.get_items():
                if item.get_type() == ebooklib.ITEM_DOCUMENT:
                    chapter_num += 1

                    # Parse HTML content with BeautifulSoup
                    soup = BeautifulSoup(item.get_content(), 'html.parser')

                    # Remove script and style elements
                    for script in soup(['script', 'style']):
                        script.decompose()

                    # Get text content
                    text = soup.get_text()

                    # Normalize whitespace
                    lines = [line.strip() for line in text.splitlines() if line.strip()]
                    chapter_text = "\n".join(lines)

                    if chapter_text:
                        # Add chapter separator
                        text_parts.append(f"## Chapter {chapter_num}\n\n{chapter_text}\n")

            return "\n".join(text_parts)

        except Exception as e:
            import sys
            print(f"Error reading EPUB {file_path.name}: {e}", file=sys.stderr)
            return ""

    def get_metadata(self, file_path: Path) -> dict:
        """Extract metadata from EPUB.

        Args:
            file_path: Path to the EPUB file

        Returns:
            Dictionary with metadata (title, author, publisher, etc.)
        """
        try:
            import ebooklib
            from ebooklib import epub

            book = epub.read_epub(str(file_path))
            metadata = {}

            # Extract title
            title = book.get_metadata('DC', 'title')
            if title:
                metadata['title'] = title[0][0]

            # Extract author
            author = book.get_metadata('DC', 'creator')
            if author:
                metadata['author'] = author[0][0]

            # Extract publisher
            publisher = book.get_metadata('DC', 'publisher')
            if publisher:
                metadata['publisher'] = publisher[0][0]

            # Extract language
            language = book.get_metadata('DC', 'language')
            if language:
                metadata['language'] = language[0][0]

            # Count chapters (document items)
            chapter_count = sum(1 for item in book.get_items()
                              if item.get_type() == ebooklib.ITEM_DOCUMENT)
            metadata['chapter_count'] = chapter_count

            return metadata

        except Exception:
            return {}
