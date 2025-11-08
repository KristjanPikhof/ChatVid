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
