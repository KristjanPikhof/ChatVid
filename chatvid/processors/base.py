"""
Base classes for document processors.

Provides the abstract base class for all document processors and the registry
for automatic processor discovery and management.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Optional


class DocumentProcessor(ABC):
    """Abstract base class for document processors.

    Each processor is responsible for extracting text from a specific file format.
    Processors are automatically registered when they are imported.

    Example:
        @ProcessorRegistry.register
        class MyProcessor(DocumentProcessor):
            name = "My Format"
            extensions = [".myformat"]
            dependencies = ["mylib"]

            def extract_text(self, file_path: Path) -> str:
                # extraction logic
                return text
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of the format (e.g., 'PDF Document')"""
        pass

    @property
    @abstractmethod
    def extensions(self) -> List[str]:
        """List of supported file extensions (e.g., ['.pdf', '.PDF'])"""
        pass

    @property
    def dependencies(self) -> List[str]:
        """List of required Python packages for this processor"""
        return []

    def is_available(self) -> bool:
        """Check if all required dependencies are installed.

        Returns:
            True if processor can be used, False otherwise
        """
        for dep in self.dependencies:
            try:
                __import__(dep)
            except ImportError:
                return False
        return True

    @abstractmethod
    def extract_text(self, file_path: Path) -> str:
        """Extract text from the given file.

        Args:
            file_path: Path to the file to process

        Returns:
            Extracted text as a string. Returns empty string on error.
        """
        pass

    def get_metadata(self, file_path: Path) -> Dict:
        """Extract metadata from the file (optional).

        Args:
            file_path: Path to the file to process

        Returns:
            Dictionary of metadata (e.g., {'pages': 10, 'author': 'Name'})
        """
        return {}


class ProcessorRegistry:
    """Registry for document processors.

    Maintains a mapping of file extensions to processor instances.
    Processors are automatically registered when decorated with @ProcessorRegistry.register
    """

    _processors: Dict[str, DocumentProcessor] = {}

    @classmethod
    def register(cls, processor_class):
        """Decorator to auto-register a processor class.

        The processor will only be registered if its dependencies are available.

        Args:
            processor_class: A class that inherits from DocumentProcessor

        Returns:
            The processor class (allows use as decorator)

        Example:
            @ProcessorRegistry.register
            class PDFProcessor(DocumentProcessor):
                ...
        """
        try:
            processor = processor_class()

            # Only register if dependencies are available
            if processor.is_available():
                for ext in processor.extensions:
                    cls._processors[ext.lower()] = processor
                # Also register uppercase versions
                for ext in processor.extensions:
                    cls._processors[ext.upper()] = processor
        except Exception as e:
            # Silently skip processors that fail to initialize
            pass

        return processor_class

    @classmethod
    def get_processor(cls, file_path: Path) -> Optional[DocumentProcessor]:
        """Get the appropriate processor for a given file.

        Args:
            file_path: Path to the file

        Returns:
            DocumentProcessor instance if available, None otherwise
        """
        ext = file_path.suffix
        return cls._processors.get(ext)

    @classmethod
    def get_supported_extensions(cls) -> List[str]:
        """Get list of all supported file extensions.

        Returns:
            List of extensions (e.g., ['.pdf', '.txt', '.html'])
        """
        # Return unique lowercase extensions only
        return sorted(list(set(ext.lower() for ext in cls._processors.keys())))

    @classmethod
    def list_processors(cls) -> Dict[str, DocumentProcessor]:
        """Get all registered processors.

        Returns:
            Dictionary mapping extensions to processor instances
        """
        return cls._processors.copy()

    @classmethod
    def get_processor_info(cls) -> List[Dict]:
        """Get information about all registered processors.

        Returns:
            List of dicts with processor information
        """
        seen = set()
        info = []

        for ext, processor in cls._processors.items():
            if processor.name not in seen:
                seen.add(processor.name)
                info.append({
                    'name': processor.name,
                    'extensions': processor.extensions,
                    'dependencies': processor.dependencies,
                    'available': processor.is_available()
                })

        return sorted(info, key=lambda x: x['name'])
