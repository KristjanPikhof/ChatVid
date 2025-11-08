"""
RTF (Rich Text Format) file processor.

Extracts plain text from RTF documents using striprtf.
"""

from pathlib import Path
from .base import DocumentProcessor, ProcessorRegistry


@ProcessorRegistry.register
class RTFProcessor(DocumentProcessor):
    """Processor for Rich Text Format files"""

    name = "Rich Text Format"
    extensions = [".rtf"]
    dependencies = ["striprtf"]

    def extract_text(self, file_path: Path) -> str:
        """Extract text from RTF file.

        Converts RTF formatting codes to plain text while preserving content.

        Args:
            file_path: Path to the RTF file

        Returns:
            Extracted plain text as a string
        """
        try:
            from striprtf.striprtf import rtf_to_text

            # Try different encodings
            encodings = ['cp1252', 'utf-8', 'latin1']
            rtf_content = None

            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                        rtf_content = f.read()
                    break
                except UnicodeDecodeError:
                    continue

            if rtf_content is None:
                # Final fallback: binary read
                with open(file_path, 'rb') as f:
                    rtf_content = f.read().decode('cp1252', errors='ignore')

            # Convert RTF to plain text
            text = rtf_to_text(rtf_content)

            # Normalize whitespace
            text = text.strip()
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            text = "\n".join(lines)

            return text

        except Exception as e:
            import sys
            print(f"Error reading RTF {file_path.name}: {e}", file=sys.stderr)
            return ""

    def get_metadata(self, file_path: Path) -> dict:
        """Extract metadata from RTF.

        Args:
            file_path: Path to the RTF file

        Returns:
            Dictionary with minimal metadata
        """
        try:
            file_size = file_path.stat().st_size
            return {
                'file_size_bytes': file_size
            }
        except Exception:
            return {}
