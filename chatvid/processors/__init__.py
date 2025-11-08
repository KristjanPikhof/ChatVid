"""
Document processors for extracting text from various file formats.

This module provides a plugin-based architecture for document processing.
New formats can be added by creating a processor class in this directory.
"""

from .base import DocumentProcessor, ProcessorRegistry

# Import all processors to trigger auto-registration
from .text import TextProcessor
from .pdf import PDFProcessor
from .docx import DOCXProcessor
from .html import HTMLProcessor

__all__ = [
    "DocumentProcessor",
    "ProcessorRegistry",
    "TextProcessor",
    "PDFProcessor",
    "DOCXProcessor",
    "HTMLProcessor",
]
