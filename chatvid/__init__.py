"""
ChatVid - Memvid Dataset Management Tool

A modular CLI tool for managing document datasets with embeddings and interactive chat.
"""

__version__ = "1.3.0"

# Export main components
try:
    from .config import Config, ChunkingConfig, LLMConfig, ChatConfig
    __all__ = ["Config", "ChunkingConfig", "LLMConfig", "ChatConfig"]
except ImportError:
    __all__ = []
