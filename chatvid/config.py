"""
Configuration management for ChatVid.

Provides type-safe configuration dataclasses with validation and environment variable loading.
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class ChunkingConfig:
    """Configuration for text chunking."""

    # Legacy fixed chunking parameters
    chunk_size: int = 500
    chunk_overlap: int = 50

    # Phase 2: Semantic chunking parameters
    chunking_strategy: str = "semantic"  # "fixed" or "semantic"
    min_chunk_size: int = 300
    max_chunk_size: int = 700
    overlap_sentences: int = 1

    def __post_init__(self):
        """Validate configuration values."""
        # Fixed chunking validation
        if self.chunk_size <= 0:
            raise ValueError(f"chunk_size must be positive, got {self.chunk_size}")
        if self.chunk_overlap < 0:
            raise ValueError(f"chunk_overlap must be non-negative, got {self.chunk_overlap}")
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError(f"chunk_overlap ({self.chunk_overlap}) must be less than chunk_size ({self.chunk_size})")

        # Semantic chunking validation
        if self.chunking_strategy not in ['fixed', 'semantic']:
            raise ValueError(f"chunking_strategy must be 'fixed' or 'semantic', got {self.chunking_strategy}")
        if self.min_chunk_size <= 0:
            raise ValueError(f"min_chunk_size must be positive, got {self.min_chunk_size}")
        if self.max_chunk_size <= 0:
            raise ValueError(f"max_chunk_size must be positive, got {self.max_chunk_size}")
        if self.min_chunk_size > self.max_chunk_size:
            raise ValueError(f"min_chunk_size ({self.min_chunk_size}) must be <= max_chunk_size ({self.max_chunk_size})")
        if self.overlap_sentences < 0:
            raise ValueError(f"overlap_sentences must be non-negative, got {self.overlap_sentences}")


@dataclass
class LLMConfig:
    """Configuration for LLM provider."""

    provider: str = "openrouter"
    base_url: str = "https://openrouter.ai/api/v1"
    api_key: Optional[str] = None
    model: str = "meta-llama/llama-3.1-8b-instruct:free"
    embedding_model: str = "text-embedding-3-small"
    temperature: float = 0.7
    max_tokens: int = 2000
    top_k: int = 5

    def __post_init__(self):
        """Validate configuration values."""
        if self.temperature < 0.0 or self.temperature > 2.0:
            raise ValueError(f"temperature must be between 0.0 and 2.0, got {self.temperature}")
        if self.max_tokens <= 0:
            raise ValueError(f"max_tokens must be positive, got {self.max_tokens}")
        if self.top_k <= 0:
            raise ValueError(f"top_k must be positive, got {self.top_k}")

        # Warning for missing API key (not error, as it may be set later)
        # Only warn if building embeddings, not during normal operation
        if not self.api_key and self.provider == "openrouter":
            # Don't warn during import, only when actually used
            pass


@dataclass
class RetrievalConfig:
    """Configuration for retrieval system (Phase 1 feature)."""

    # Adaptive retrieval settings
    min_top_k: int = 5
    max_top_k: int = 25
    enable_adaptive_top_k: bool = True

    # Phase 2+ features (placeholders)
    enable_query_expansion: bool = False
    expansion_method: str = "keyword"  # "keyword" or "llm"
    max_query_variants: int = 5

    # Phase 3 features (placeholders)
    enable_two_stage_retrieval: bool = False
    stage1_candidates: int = 50
    enable_reranking: bool = False
    reranking_model: str = "ms-marco-MiniLM-L-6-v2"

    def __post_init__(self):
        """Validate configuration values."""
        if self.min_top_k <= 0:
            raise ValueError(f"min_top_k must be positive, got {self.min_top_k}")
        if self.max_top_k <= 0:
            raise ValueError(f"max_top_k must be positive, got {self.max_top_k}")
        if self.min_top_k > self.max_top_k:
            raise ValueError(f"min_top_k ({self.min_top_k}) must be <= max_top_k ({self.max_top_k})")
        if self.max_query_variants <= 0:
            raise ValueError(f"max_query_variants must be positive, got {self.max_query_variants}")
        if self.stage1_candidates < self.max_top_k:
            raise ValueError(f"stage1_candidates ({self.stage1_candidates}) must be >= max_top_k ({self.max_top_k})")
        if self.expansion_method not in ['keyword', 'llm']:
            raise ValueError(f"expansion_method must be 'keyword' or 'llm', got {self.expansion_method}")


@dataclass
class ChatConfig:
    """Configuration for chat interface."""

    system_prompt: str = "You are a helpful assistant that answers questions based on the provided context."
    context_separator: str = "\n---\n"
    max_history: int = 10

    def __post_init__(self):
        """Validate configuration values."""
        if self.max_history < 0:
            raise ValueError(f"max_history must be non-negative, got {self.max_history}")


@dataclass
class Config:
    """Main configuration container."""

    chunking: ChunkingConfig
    llm: LLMConfig
    retrieval: RetrievalConfig
    chat: ChatConfig

    @classmethod
    def from_env(cls) -> "Config":
        """Create configuration from environment variables.

        Environment Variables:
            CHUNK_SIZE: Text chunk size (default: 500)
            CHUNK_OVERLAP: Overlap between chunks (default: 50)

            LLM_PROVIDER: LLM provider name (default: openrouter)
            LLM_BASE_URL: Base URL for LLM API (default: https://openrouter.ai/api/v1)
            OPENROUTER_API_KEY: API key for OpenRouter
            LLM_MODEL: Model to use (default: meta-llama/llama-3.1-8b-instruct:free)
            EMBEDDING_MODEL: Embedding model (default: text-embedding-3-small)
            LLM_TEMPERATURE: Temperature for generation (default: 0.7)
            LLM_MAX_TOKENS: Maximum tokens to generate (default: 2000)
            TOP_K: Number of context chunks to retrieve (default: 5)

            SYSTEM_PROMPT: System prompt for chat (default: helpful assistant)
            CONTEXT_SEPARATOR: Separator between context chunks (default: \n---\n)
            MAX_HISTORY: Maximum chat history length (default: 10)

        Returns:
            Config instance with values from environment or defaults

        Raises:
            ValueError: If any configuration value is invalid
        """
        # Helper functions for type-safe env reading
        def get_env_str(key: str, default: str) -> str:
            return os.getenv(key, default)

        def get_env_int(key: str, default: int) -> int:
            value = os.getenv(key)
            if value is None:
                return default
            try:
                return int(value)
            except ValueError:
                raise ValueError(f"Environment variable {key}={value} is not a valid integer")

        def get_env_float(key: str, default: float) -> float:
            value = os.getenv(key)
            if value is None:
                return default
            try:
                return float(value)
            except ValueError:
                raise ValueError(f"Environment variable {key}={value} is not a valid float")

        # Build configuration from environment
        chunking = ChunkingConfig(
            # Legacy fixed chunking
            chunk_size=get_env_int("CHUNK_SIZE", 500),
            chunk_overlap=get_env_int("CHUNK_OVERLAP", 50),
            # Phase 2: Semantic chunking
            chunking_strategy=get_env_str("CHUNKING_STRATEGY", "semantic"),
            min_chunk_size=get_env_int("MIN_CHUNK_SIZE", 300),
            max_chunk_size=get_env_int("MAX_CHUNK_SIZE", 700),
            overlap_sentences=get_env_int("OVERLAP_SENTENCES", 1),
        )

        # API key with backward compatibility
        # Try OPENROUTER_API_KEY first, then fall back to OPENAI_API_KEY
        api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")

        # Base URL with backward compatibility
        # Try LLM_BASE_URL first, then fall back to OPENAI_API_BASE
        base_url = os.getenv("LLM_BASE_URL") or os.getenv("OPENAI_API_BASE") or "https://openrouter.ai/api/v1"

        llm = LLMConfig(
            provider=get_env_str("LLM_PROVIDER", "openrouter"),
            base_url=base_url,
            api_key=api_key,
            model=get_env_str("LLM_MODEL", "meta-llama/llama-3.1-8b-instruct:free"),
            embedding_model=get_env_str("EMBEDDING_MODEL", "text-embedding-3-small"),
            temperature=get_env_float("LLM_TEMPERATURE", 0.7),
            max_tokens=get_env_int("LLM_MAX_TOKENS", 2000),
            top_k=get_env_int("CONTEXT_CHUNKS", 5),  # Use CONTEXT_CHUNKS for backward compat
        )

        # Phase 1: Retrieval configuration
        retrieval = RetrievalConfig(
            min_top_k=get_env_int("MIN_TOP_K", 5),
            max_top_k=get_env_int("MAX_TOP_K", 25),
            enable_adaptive_top_k=get_env_str("ENABLE_ADAPTIVE_TOP_K", "true").lower() == "true",
            # Phase 2+ placeholders
            enable_query_expansion=get_env_str("ENABLE_QUERY_EXPANSION", "false").lower() == "true",
            expansion_method=get_env_str("EXPANSION_METHOD", "keyword"),
            max_query_variants=get_env_int("MAX_QUERY_VARIANTS", 5),
            # Phase 3 placeholders
            enable_two_stage_retrieval=get_env_str("ENABLE_TWO_STAGE_RETRIEVAL", "false").lower() == "true",
            stage1_candidates=get_env_int("STAGE1_CANDIDATES", 50),
            enable_reranking=get_env_str("ENABLE_RERANKING", "false").lower() == "true",
            reranking_model=get_env_str("RERANKING_MODEL", "ms-marco-MiniLM-L-6-v2"),
        )

        chat = ChatConfig(
            system_prompt=get_env_str(
                "SYSTEM_PROMPT",
                "You are a helpful assistant that answers questions based on the provided context."
            ),
            context_separator=get_env_str("CONTEXT_SEPARATOR", "\n---\n"),
            max_history=get_env_int("MAX_HISTORY", 10),
        )

        return cls(chunking=chunking, llm=llm, retrieval=retrieval, chat=chat)

    def validate(self) -> None:
        """Validate entire configuration.

        Raises:
            ValueError: If any configuration is invalid
        """
        # Dataclass __post_init__ already validates individual components
        # This method is for cross-component validation if needed in the future
        pass
