"""
PDF file processor.

Extracts text from PDF documents using PyPDF2.
"""

from pathlib import Path
from .base import DocumentProcessor, ProcessorRegistry


@ProcessorRegistry.register
class PDFProcessor(DocumentProcessor):
    """Processor for PDF files"""

    name = "PDF Document"
    extensions = [".pdf"]
    dependencies = ["PyPDF2"]

    def extract_text(self, file_path: Path) -> str:
        """Extract text from PDF file.

        Args:
            file_path: Path to the PDF file

        Returns:
            Extracted text from all pages as a string
        """
        try:
            import PyPDF2

            text = []
            with open(file_path, "rb") as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text.append(page_text)
            return "\n\n".join(text)
        except Exception as e:
            # Import here to avoid circular dependency
            import sys
            print(f"Error reading PDF {file_path.name}: {e}", file=sys.stderr)
            return ""

    def extract_text_with_pages(self, file_path: Path) -> list:
        """
        Extract text from PDF with page numbers.

        Phase 2 feature (v1.7.0): Enables citation tracking with page numbers
        for precise source attribution in chat responses.

        Args:
            file_path: Path to the PDF file

        Returns:
            List of (page_number, page_text) tuples, where page_number is 1-indexed
        """
        try:
            import PyPDF2

            pages = []
            with open(file_path, "rb") as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page_num, page in enumerate(pdf_reader.pages, start=1):
                    page_text = page.extract_text()
                    if page_text and page_text.strip():
                        pages.append((page_num, page_text))

            return pages
        except Exception as e:
            import sys
            print(f"Error reading PDF {file_path.name}: {e}", file=sys.stderr)
            return []

    def get_metadata(self, file_path: Path) -> dict:
        """Extract metadata from PDF.

        Args:
            file_path: Path to the PDF file

        Returns:
            Dictionary with metadata (pages, author, title, etc.)
        """
        try:
            import PyPDF2

            with open(file_path, "rb") as f:
                pdf_reader = PyPDF2.PdfReader(f)
                metadata = {
                    'pages': len(pdf_reader.pages)
                }

                # Add PDF metadata if available
                if pdf_reader.metadata:
                    if pdf_reader.metadata.author:
                        metadata['author'] = pdf_reader.metadata.author
                    if pdf_reader.metadata.title:
                        metadata['title'] = pdf_reader.metadata.title

                return metadata
        except Exception:
            return {}
