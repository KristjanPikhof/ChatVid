"""
Advanced retrieval system for ChatVid.

Provides query analysis, adaptive retrieval, query expansion, and multi-stage retrieval
capabilities for improved RAG performance.
"""

from typing import Dict, List, Optional, Tuple
import re


class QueryComplexityAnalyzer:
    """
    Analyzes user queries to determine complexity and recommend optimal retrieval parameters.

    Distinguishes between:
    - Specific questions: "What is X?" → fewer chunks needed
    - Broad questions: "Explain Y" → more chunks needed for comprehensive coverage
    """

    # Keywords indicating broad, exploratory queries
    BROAD_KEYWORDS = [
        'what', 'how', 'why', 'explain', 'describe', 'discuss',
        'overview', 'summary', 'all', 'any', 'everything', 'comprehensive',
        'tell me about', 'what are', 'how do', 'why do', 'explain how'
    ]

    # Keywords indicating specific, targeted queries
    SPECIFIC_KEYWORDS = [
        'when', 'where', 'who', 'which', 'does', 'is', 'can', 'will',
        'how many', 'how much', 'what is', 'name', 'define'
    ]

    def __init__(self, min_top_k: int = 5, max_top_k: int = 25):
        """
        Initialize the analyzer.

        Args:
            min_top_k: Minimum chunks to retrieve for specific questions
            max_top_k: Maximum chunks to retrieve for broad questions
        """
        self.min_top_k = min_top_k
        self.max_top_k = max_top_k

    def analyze(self, query: str) -> Dict:
        """
        Analyze query complexity and recommend retrieval parameters.

        Args:
            query: User's question

        Returns:
            Dictionary with analysis results:
            - top_k: Recommended number of chunks to retrieve
            - is_broad: Whether query is broad/exploratory
            - complexity_score: Numerical complexity (0-1)
            - query_type: 'specific' or 'broad'
            - reasoning: Human-readable explanation
        """
        query_lower = query.lower().strip()

        # Calculate complexity indicators
        word_count = len(query.split())
        has_broad_keyword = self._check_keywords(query_lower, self.BROAD_KEYWORDS)
        has_specific_keyword = self._check_keywords(query_lower, self.SPECIFIC_KEYWORDS)
        has_multiple_subjects = self._has_multiple_subjects(query_lower)
        is_long_query = word_count > 8
        has_question_mark = '?' in query

        # Calculate complexity score (0-1 scale)
        complexity_score = 0.0

        # Broad keywords add more weight
        if has_broad_keyword:
            complexity_score += 0.4

        # Specific keywords reduce complexity
        if has_specific_keyword and not has_broad_keyword:
            complexity_score -= 0.2

        # Multiple subjects indicate broader scope
        if has_multiple_subjects:
            complexity_score += 0.3

        # Long queries tend to be more complex
        if is_long_query:
            complexity_score += 0.2

        # Clamp to 0-1 range
        complexity_score = max(0.0, min(1.0, complexity_score))

        # Determine query type
        is_broad = complexity_score >= 0.4
        query_type = 'broad' if is_broad else 'specific'

        # Calculate recommended top_k
        # Linear interpolation between min and max based on complexity
        top_k_range = self.max_top_k - self.min_top_k
        recommended_top_k = int(self.min_top_k + (complexity_score * top_k_range))

        # Ensure within bounds
        recommended_top_k = max(self.min_top_k, min(self.max_top_k, recommended_top_k))

        # Generate reasoning
        reasons = []
        if has_broad_keyword:
            reasons.append("broad keyword detected")
        if has_specific_keyword:
            reasons.append("specific keyword detected")
        if has_multiple_subjects:
            reasons.append("multiple subjects")
        if is_long_query:
            reasons.append("long query")

        reasoning = f"{query_type.capitalize()} question" + (
            f" ({', '.join(reasons)})" if reasons else ""
        )

        return {
            'top_k': recommended_top_k,
            'is_broad': is_broad,
            'complexity_score': round(complexity_score, 2),
            'query_type': query_type,
            'reasoning': reasoning
        }

    def _check_keywords(self, query: str, keywords: List[str]) -> bool:
        """Check if any keyword appears in query."""
        for keyword in keywords:
            if keyword in query:
                return True
        return False

    def _has_multiple_subjects(self, query: str) -> bool:
        """Detect if query asks about multiple subjects."""
        # Look for conjunctions that indicate multiple topics
        conjunctions = [' and ', ' or ', ', ']
        return any(conj in query for conj in conjunctions)


class QueryExpander:
    """
    Expands user queries with synonyms and variations for better retrieval coverage.

    Phase 2 feature: Generates multiple query variants to catch semantically similar
    chunks that might use different terminology.
    """

    # Semantic variants dictionary (expandable via config in future)
    SEMANTIC_VARIANTS = {
        'challenge': ['problem', 'issue', 'obstacle', 'difficulty', 'risk', 'concern'],
        'solution': ['fix', 'resolution', 'answer', 'approach', 'remedy', 'workaround'],
        'benefit': ['advantage', 'pro', 'positive', 'gain', 'value'],
        'drawback': ['disadvantage', 'con', 'negative', 'downside', 'limitation'],
        'cost': ['budget', 'expense', 'price', 'funding', 'investment'],
        'method': ['approach', 'technique', 'way', 'process', 'procedure'],
        'result': ['outcome', 'consequence', 'effect', 'impact', 'finding'],
        'reason': ['cause', 'factor', 'rationale', 'explanation', 'motivation'],
    }

    def __init__(self, max_variants: int = 5):
        """
        Initialize the query expander.

        Args:
            max_variants: Maximum number of query variants to generate
        """
        self.max_variants = max_variants

    def expand(self, query: str, method: str = 'keyword') -> List[str]:
        """
        Generate query variants for expanded retrieval.

        Args:
            query: Original user query
            method: Expansion method ('keyword' or 'llm')

        Returns:
            List of query variants (includes original query)
        """
        if method == 'keyword':
            return self._expand_keyword(query)
        elif method == 'llm':
            # Phase 3 feature: LLM-based expansion
            # For now, fall back to keyword
            return self._expand_keyword(query)
        else:
            return [query]

    def _expand_keyword(self, query: str) -> List[str]:
        """
        Keyword-based query expansion using synonym dictionary.

        Args:
            query: Original query

        Returns:
            List of query variants
        """
        variants = [query]  # Always include original
        query_lower = query.lower()

        # Find semantic variants
        for key, synonyms in self.SEMANTIC_VARIANTS.items():
            if key in query_lower:
                # Generate variants by replacing key with synonyms
                for synonym in synonyms[:self.max_variants - len(variants)]:
                    # Case-preserving replacement
                    variant = re.sub(
                        key,
                        synonym,
                        query_lower,
                        flags=re.IGNORECASE
                    )
                    if variant not in [v.lower() for v in variants]:
                        variants.append(variant.capitalize() if query[0].isupper() else variant)

                    if len(variants) >= self.max_variants:
                        return variants

        return variants


class AdvancedChatVidRetriever:
    """
    Advanced retrieval wrapper for ChatVid.

    Phase 2+ feature: Provides enhanced retrieval capabilities including:
    - Multi-query retrieval (query expansion)
    - Adaptive top_k adjustment
    - Result deduplication
    - Context aggregation
    - Foundation for two-stage retrieval and re-ranking (Phase 3)

    Note: This is a placeholder for Phase 2 implementation.
    Will wrap MemvidChat and add enhanced features.
    """

    def __init__(self, video_file: str, index_file: str, config: dict):
        """
        Initialize the advanced retriever.

        Args:
            video_file: Path to knowledge.mp4
            index_file: Path to knowledge_index.json
            config: Configuration dictionary
        """
        self.video_file = video_file
        self.index_file = index_file
        self.config = config

        # Initialize query analyzer and expander
        self.query_analyzer = QueryComplexityAnalyzer(
            min_top_k=config.get('min_top_k', 5),
            max_top_k=config.get('max_top_k', 25)
        )

        self.query_expander = QueryExpander(
            max_variants=config.get('max_query_variants', 5)
        )

        # Will be initialized in Phase 2
        self.base_retriever = None

    def retrieve(self, query: str) -> List[Tuple[str, float]]:
        """
        Retrieve relevant chunks for query.

        Phase 2 implementation will add:
        - Query expansion
        - Multi-query retrieval
        - Deduplication
        - Result aggregation

        Args:
            query: User question

        Returns:
            List of (chunk_text, relevance_score) tuples
        """
        # Analyze query complexity
        analysis = self.query_analyzer.analyze(query)

        # Phase 2: Expand query if enabled
        if self.config.get('enable_query_expansion', False):
            queries = self.query_expander.expand(
                query,
                method=self.config.get('expansion_method', 'keyword')
            )
        else:
            queries = [query]

        # Phase 2: Multi-query retrieval and aggregation
        # For now, return empty list (will be implemented in Phase 2)
        return []

    def chat(self, query: str, conversation_history: List = None) -> str:
        """
        Process chat query with enhanced retrieval.

        Phase 2 implementation.

        Args:
            query: User question
            conversation_history: Previous conversation turns

        Returns:
            LLM response
        """
        # Phase 2 implementation
        pass
