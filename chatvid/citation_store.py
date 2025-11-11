"""
Citation metadata storage for ChatVid.

Stores citation information for each chunk that can't be stored
in Memvid's knowledge_index.json format. This parallel store enables
tracking page numbers, document metadata, and format-specific references.

File: datasets/<name>/citation_index.json
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any


class CitationStore:
    """
    Manages citation metadata for document chunks.

    Stored separately from Memvid index to preserve backward compatibility
    and enable rich citation features without modifying Memvid internals.

    File format:
    {
        "version": "1.0",
        "chunking_config": {...},
        "citations": {
            "0": {
                "document": "report.pdf",
                "page_start": 5,
                "page_end": 6,
                "doc_metadata": {
                    "title": "Annual Report",
                    "author": "John Doe",
                    "total_pages": 50,
                    "format": "pdf"
                }
            },
            ...
        }
    }
    """

    def __init__(self, dataset_path: Path):
        """
        Initialize citation store for a dataset.

        Args:
            dataset_path: Path to dataset directory
        """
        self.dataset_path = Path(dataset_path)
        self.citation_file = self.dataset_path / "citation_index.json"
        self.citations: Dict[int, Dict[str, Any]] = {}
        self.chunking_config: Dict[str, Any] = {}

        # Load existing citations if file exists
        if self.citation_file.exists():
            self.load()

    def add_citation(
        self,
        chunk_id: int,
        document: str,
        page_start: Optional[int] = None,
        page_end: Optional[int] = None,
        doc_metadata: Optional[Dict] = None,
        extra: Optional[Dict] = None
    ):
        """
        Add citation metadata for a chunk.

        Args:
            chunk_id: Chunk ID (index in embeddings list)
            document: Document filename (e.g., "report.pdf")
            page_start: First page this chunk appears on (None for non-PDF)
            page_end: Last page if chunk spans pages (None if single page)
            doc_metadata: Document metadata from processor.get_metadata()
            extra: Additional format-specific metadata (sheet names, slide numbers, etc.)
        """
        citation_data = {
            'document': document,
            'page_start': page_start,
            'page_end': page_end
        }

        if doc_metadata:
            citation_data['doc_metadata'] = doc_metadata

        if extra:
            citation_data.update(extra)

        self.citations[chunk_id] = citation_data

    def get_citation(self, chunk_id: int) -> Optional[Dict]:
        """
        Get citation metadata for a chunk.

        Args:
            chunk_id: Chunk ID

        Returns:
            Citation dict or None if not found
        """
        return self.citations.get(chunk_id)

    def get_citations_for_chunks(self, chunk_ids: List[int]) -> List[Dict]:
        """
        Get citations for multiple chunks.

        Args:
            chunk_ids: List of chunk IDs

        Returns:
            List of citation dicts with chunk_id added
        """
        citations = []
        for cid in chunk_ids:
            if cid in self.citations:
                citation = {'chunk_id': cid, **self.citations[cid]}
                citations.append(citation)
        return citations

    def set_chunking_config(self, config: Dict[str, Any]):
        """
        Store chunking configuration used for this build.

        Args:
            config: Chunking configuration dict
        """
        self.chunking_config = config

    def get_chunking_config(self) -> Dict[str, Any]:
        """Get stored chunking configuration."""
        return self.chunking_config

    def has_page_numbers(self) -> bool:
        """
        Check if any citations have page numbers.

        Returns:
            True if at least one citation has page_start
        """
        return any(
            cite.get('page_start') is not None
            for cite in self.citations.values()
        )

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about citations.

        Returns:
            Dict with counts and metadata
        """
        total = len(self.citations)
        with_pages = sum(1 for c in self.citations.values() if c.get('page_start'))
        unique_docs = len(set(c['document'] for c in self.citations.values()))

        return {
            'total_chunks': total,
            'chunks_with_pages': with_pages,
            'unique_documents': unique_docs,
            'has_page_tracking': self.has_page_numbers()
        }

    def save(self):
        """Save citations to disk as JSON."""
        data = {
            'version': '1.0',
            'chunking_config': self.chunking_config,
            'citations': {str(k): v for k, v in self.citations.items()}
        }

        with open(self.citation_file, 'w') as f:
            json.dump(data, f, indent=2)

    def load(self):
        """Load citations from disk."""
        if not self.citation_file.exists():
            return

        with open(self.citation_file, 'r') as f:
            data = json.load(f)

        # Convert string keys back to int
        self.citations = {
            int(k): v
            for k, v in data.get('citations', {}).items()
        }

        self.chunking_config = data.get('chunking_config', {})

    def clear(self):
        """Clear all citations and delete file."""
        self.citations = {}
        self.chunking_config = {}

        if self.citation_file.exists():
            self.citation_file.unlink()

    def exists(self) -> bool:
        """Check if citation file exists on disk."""
        return self.citation_file.exists()
