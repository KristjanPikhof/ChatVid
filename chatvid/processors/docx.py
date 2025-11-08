"""
Microsoft Word document processor.

Extracts text from DOCX and DOC files using python-docx.
"""

from pathlib import Path
from .base import DocumentProcessor, ProcessorRegistry


@ProcessorRegistry.register
class DOCXProcessor(DocumentProcessor):
    """Processor for Microsoft Word documents"""

    name = "Word Document"
    extensions = [".docx", ".doc"]
    dependencies = ["docx"]  # python-docx package

    def extract_text(self, file_path: Path) -> str:
        """Extract text from DOCX file.

        Args:
            file_path: Path to the DOCX file

        Returns:
            Extracted text from all paragraphs as a string
        """
        try:
            import docx

            doc = docx.Document(file_path)
            text = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text.append(paragraph.text)
            return "\n\n".join(text)
        except Exception as e:
            # Import here to avoid circular dependency
            import sys
            print(f"Error reading DOCX {file_path.name}: {e}", file=sys.stderr)
            return ""
