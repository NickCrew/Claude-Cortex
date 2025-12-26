"""Semantic similarity matching using embeddings for intelligent recommendations.

This module provides lightweight semantic matching to find similar past sessions
and make intelligent agent recommendations based on actual usage patterns.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Literal, Dict, Union

import numpy as np  # type: ignore

logger = logging.getLogger(__name__)


# Claude model pricing (per million tokens)
CLAUDE_PRICING: Dict[str, Dict[str, Union[float, str]]] = {
    "claude-opus-4-20250514": {
        "input": 15.0,  # $15/MTok
        "output": 75.0,  # $75/MTok
        "name": "Opus 4",
    },
    "claude-sonnet-4-20250514": {
        "input": 3.0,  # $3/MTok
        "output": 15.0,  # $15/MTok
        "name": "Sonnet 4",
    },
    "claude-haiku-4-20250514": {
        "input": 0.25,  # $0.25/MTok
        "output": 1.25,  # $1.25/MTok
        "name": "Haiku 4",
    },
}


class ModelSelector:
    """Intelligent model selection for cost optimization.

    Chooses the appropriate Claude model based on task complexity and context size.
    Uses Haiku for simple tasks, Sonnet for standard complexity, and Opus for
    complex analysis requiring deep reasoning.
    """

    @staticmethod
    def select_model(
        context_size: int,
        agent_count: int,
        confidence_threshold: float = 0.5,
    ) -> tuple[str, int]:
        """Select optimal model and max_tokens based on task characteristics.

        Args:
            context_size: Estimated tokens in the context
            agent_count: Number of available agents to analyze
            confidence_threshold: Required confidence level (0.0-1.0)

        Returns:
            Tuple of (model_name, max_tokens)

        Selection Strategy:
        - Haiku (10-12x cheaper): Simple agent recommendations, small context
        - Sonnet (baseline): Standard complexity, medium context
        - Opus (premium): Complex analysis, large context, high confidence needed
        """
        # Calculate complexity score (0-1 range)
        # Uses weighted combination of context size, agent count, and confidence

        # Factor 1: Context size (40% weight)
        # Small: <2000 tokens, Medium: 2000-5000, Large: >5000
        if context_size < 2000:
            context_score = 0.3
        elif context_size < 5000:
            context_score = 0.6
        else:
            context_score = 0.9

        # Factor 2: Agent catalog size (30% weight)
        # Few: <=10 agents, Medium: 11-30, Many: >30
        if agent_count <= 10:
            agent_score = 0.2
        elif agent_count <= 30:
            agent_score = 0.5
        else:
            agent_score = 0.8

        # Factor 3: Required confidence (30% weight)
        confidence_score = confidence_threshold

        # Weighted combination
        complexity_score = (
            context_score * 0.4 +
            agent_score * 0.3 +
            confidence_score * 0.3
        )

        # Select model based on complexity
        if complexity_score < 0.4:
            # Simple task: Use Haiku for maximum cost savings
            model = "claude-haiku-4-20250514"
            max_tokens = 512  # Smaller output for recommendations
        elif complexity_score < 0.75:
            # Standard task: Use Sonnet (balanced)
            model = "claude-sonnet-4-20250514"
            max_tokens = 1024
        else:
            # Complex task: Use Opus (premium)
            model = "claude-opus-4-20250514"
            max_tokens = 2048

        logger.debug(
            f"Selected {CLAUDE_PRICING[model]['name']} "
            f"(complexity: {complexity_score:.2f}, max_tokens: {max_tokens})"
        )

        return model, max_tokens

    @staticmethod
    def calculate_cost(
        model: str, input_tokens: int, output_tokens: int
    ) -> dict[str, Any]:
        """Calculate actual API cost for a request.

        Args:
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Dictionary with cost breakdown:
            - input_cost: Cost for input tokens
            - output_cost: Cost for output tokens
            - total_cost: Total cost
            - model_name: Human-readable model name
            - savings_vs_sonnet: Cost savings compared to Sonnet (if using cheaper model)
            - savings_percentage: Percentage savings vs Sonnet
        """
        pricing = CLAUDE_PRICING.get(
            model, CLAUDE_PRICING["claude-sonnet-4-20250514"]
        )

        input_cost = (input_tokens / 1_000_000) * float(pricing["input"])
        output_cost = (output_tokens / 1_000_000) * float(pricing["output"])
        total_cost = input_cost + output_cost

        result = {
            "input_cost": round(input_cost, 6),
            "output_cost": round(output_cost, 6),
            "total_cost": round(total_cost, 6),
            "model_name": str(pricing["name"]),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
        }

        # Calculate savings if using a cheaper model than Sonnet
        if model != "claude-sonnet-4-20250514":
            sonnet_pricing = CLAUDE_PRICING["claude-sonnet-4-20250514"]
            sonnet_cost = (
                (input_tokens / 1_000_000) * float(sonnet_pricing["input"])
                + (output_tokens / 1_000_000) * float(sonnet_pricing["output"])
            )
            savings = sonnet_cost - total_cost
            result["savings_vs_sonnet"] = round(savings, 6)
            result["savings_percentage"] = (
                round((savings / sonnet_cost) * 100, 1) if sonnet_cost > 0 else 0.0
            )

        return result


class SemanticMatcher:
    """Lightweight semantic matching for session similarity using FastEmbed.

    Uses the BAAI/bge-small-en-v1.5 model which is:
    - Fast: ~50ms per query
    - Small: 33MB model size
    - Accurate: 0.82 on MTEB benchmark
    - Free: No API costs

    The matcher builds embeddings from session contexts and finds semantically
    similar past sessions to make agent recommendations.
    """

    def __init__(self, cache_dir: Path):
        """Initialize semantic matcher.

        Args:
            cache_dir: Directory for caching embeddings
        """
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Lazy load the embedding model
        self._model = None

        self.embeddings_file = cache_dir / "session_embeddings.jsonl"
        self.embeddings: list[tuple[dict[str, Any], np.ndarray]] = []
        self._load_embeddings()

    @property
    def model(self) -> Any:
        """Lazy load the embedding model only when needed."""
        if self._model is None:
            try:
                from fastembed import TextEmbedding  # type: ignore

                self._model = TextEmbedding("BAAI/bge-small-en-v1.5")
                logger.info("Loaded FastEmbed model: BAAI/bge-small-en-v1.5")
            except ImportError:
                logger.warning(
                    "FastEmbed not installed. Semantic matching disabled. "
                    "Install with: pip install fastembed"
                )
                raise
        return self._model

    def add_session(self, session_data: dict[str, Any]) -> None:
        """Record a successful session for future semantic matching.

        Args:
            session_data: Session metadata including context and agents used
        """
        try:
            context_text = self._session_to_text(session_data)
            embedding = self._embed(context_text)

            self.embeddings.append((session_data, embedding))
            self._save_embedding(session_data, embedding)

            logger.debug(f"Added session embedding: {len(self.embeddings)} total")
        except Exception as e:
            logger.warning(f"Failed to add session embedding: {e}")

    def find_similar(
        self,
        current_context: dict[str, Any],
        top_k: int = 5,
        min_similarity: float = 0.6,
    ) -> list[tuple[dict[str, Any], float]]:
        """Find semantically similar past sessions.

        Args:
            current_context: Current session context
            top_k: Maximum number of results to return
            min_similarity: Minimum similarity threshold (0.0-1.0)

        Returns:
            List of (session_data, similarity_score) tuples, sorted by similarity
        """
        if not self.embeddings:
            logger.debug("No embeddings available for similarity search")
            return []

        try:
            query_text = self._session_to_text(current_context)
            query_emb = self._embed(query_text)

            similarities = []
            for session_data, emb in self.embeddings:
                sim = self._cosine_similarity(query_emb, emb)
                if sim >= min_similarity:
                    similarities.append((session_data, float(sim)))

            # Sort by similarity (highest first)
            similarities.sort(key=lambda x: x[1], reverse=True)

            logger.debug(
                f"Found {len(similarities)} similar sessions (min: {min_similarity})"
            )

            return similarities[:top_k]
        except Exception as e:
            logger.warning(f"Similarity search failed: {e}")
            return []

    def _session_to_text(self, session: dict[str, Any]) -> str:
        """Convert session context to searchable text representation.

        This is the key function that creates a semantic representation capturing
        what the session was about. It combines:
        - File paths (carry strong signals)
        - Domain keywords (auth, api, database, etc.)
        - Task types (feature, bugfix, refactor)
        - Agents used (strong signal for similarity)

        Args:
            session: Session data dictionary

        Returns:
            Text representation suitable for embedding
        """
        parts = []

        # File paths carry strong semantic signals
        files = session.get("files", [])
        if isinstance(files, list):
            parts.extend(files[:30])  # Limit to first 30 files

        # Extract semantic keywords from context
        context = session.get("context", {})

        # Domain-specific signals
        if context.get("has_auth"):
            parts.append("authentication authorization security oauth jwt token")
        if context.get("has_api"):
            parts.append("api rest graphql endpoints routes handlers controller")
        if context.get("has_tests"):
            parts.append("testing pytest unittest integration e2e test-driven")
        if context.get("has_frontend"):
            parts.append("frontend react vue ui components jsx tsx interface")
        if context.get("has_backend"):
            parts.append("backend server fastapi flask django api service")
        if context.get("has_database"):
            parts.append("database sql postgres mysql migrations orm models schema")

        # Task type signals
        task_type = session.get("task_type")
        if task_type:
            parts.append(str(task_type))

        # Agents used (very strong signal for similarity)
        agents = session.get("agents", [])
        if isinstance(agents, list):
            parts.extend([f"agent:{a}" for a in agents])

        # File types
        file_types = context.get("file_types", [])
        if isinstance(file_types, list):
            parts.extend([f"filetype:{ft}" for ft in file_types])

        # Combine all parts
        return " ".join(str(p) for p in parts if p)

    def _embed(self, text: str) -> np.ndarray:
        """Generate embedding vector for text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector as numpy array
        """
        if not text.strip():
            # Return zero vector for empty text
            return np.zeros(384)  # bge-small-en-v1.5 dimension

        embeddings = list(self.model.embed([text]))
        return embeddings[0]

    @staticmethod
    def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        """Compute cosine similarity between two vectors.

        Args:
            a: First vector
            b: Second vector

        Returns:
            Cosine similarity score (0.0-1.0)
        """
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return float(np.dot(a, b) / (norm_a * norm_b))

    def _load_embeddings(self) -> None:
        """Load cached embeddings from disk."""
        if not self.embeddings_file.exists():
            logger.debug("No cached embeddings found")
            return

        try:
            count = 0
            with open(self.embeddings_file) as f:
                for line in f:
                    if not line.strip():
                        continue
                    data = json.loads(line)
                    session_data = data["session"]
                    embedding = np.array(data["embedding"], dtype=np.float32)
                    self.embeddings.append((session_data, embedding))
                    count += 1

            logger.info(f"Loaded {count} cached embeddings")
        except Exception as e:
            logger.warning(f"Failed to load embeddings: {e}")
            self.embeddings = []

    def _save_embedding(
        self, session_data: dict[str, Any], embedding: np.ndarray
    ) -> None:
        """Append embedding to cache file.

        Args:
            session_data: Session metadata
            embedding: Embedding vector
        """
        try:
            with open(self.embeddings_file, "a") as f:
                f.write(
                    json.dumps(
                        {
                            "session": session_data,
                            "embedding": embedding.tolist(),
                        }
                    )
                    + "\n"
                )
        except Exception as e:
            logger.warning(f"Failed to save embedding: {e}")

    def clear_cache(self) -> None:
        """Clear all cached embeddings."""
        self.embeddings = []
        if self.embeddings_file.exists():
            self.embeddings_file.unlink()
        logger.info("Cleared embedding cache")


class LLMIntelligence:
    """Optional LLM-powered intelligence using Claude API.

    This is a premium feature that uses actual Claude API calls to analyze
    context and make intelligent recommendations. It's more expensive but
    provides better reasoning and understanding.

    Features:
    - Smart model selection (Haiku for simple, Sonnet for standard, Opus for complex)
    - Prompt caching for cost optimization (90% reduction on cached tokens)
    - Cost tracking and budget enforcement
    - Configurable via intelligence-config.json

    Only used when:
    1. User explicitly enables it (config: llm_enabled=true)
    2. Semantic matching confidence is low (<threshold)
    3. Anthropic package is installed
    """

    def __init__(
        self,
        available_agents: list[dict[str, Any]],
        config: Any | None = None,
    ):
        """Initialize LLM intelligence.

        Args:
            available_agents: List of available agent definitions
            config: Optional IntelligenceConfig (loads from file if not provided)

        Raises:
            ImportError: If anthropic package is not installed
        """
        self.available_agents = available_agents

        # Load configuration
        if config is None:
            try:
                from .config import get_config

                config = get_config()
            except ImportError:
                # Config module not available, use defaults
                config = None

        self.config = config

        try:
            import anthropic  # type: ignore

            self.client = anthropic.Anthropic()
            logger.info("LLM intelligence initialized (Claude API ready)")
        except ImportError:
            logger.warning(
                "Anthropic package not installed. LLM intelligence disabled. "
                "Install with: pip install anthropic"
            )
            raise

    def analyze_and_recommend(
        self,
        context: dict[str, Any],
        recent_sessions: list[dict[str, Any]] | None = None,
        use_caching: bool = True,
    ) -> dict[str, Any]:
        """Use Claude API to analyze context and recommend agents.

        Args:
            context: Current session context
            recent_sessions: Optional recent session history
            use_caching: Enable prompt caching for cost optimization (default: True)

        Returns:
            Dictionary containing:
            - recommendations: List of recommendation dictionaries
            - metadata: Usage statistics and cost information
        """
        # Build the analysis components
        agent_catalog = self._format_agent_catalog()
        context_summary = self._format_context(context)
        history = (
            self._format_history(recent_sessions) if recent_sessions else "No history."
        )

        # Estimate context size for model selection
        context_size = len(agent_catalog) + len(context_summary) + len(history)
        estimated_tokens = context_size // 4  # Rough estimate: 4 chars per token

        # Select model based on config or complexity
        if self.config and self.config.model_selection.force_model:
            # User forced a specific model
            model = self.config.model_selection.force_model
            max_tokens = 1024  # Standard output size
            logger.info(f"Using forced model: {model}")
        elif self.config and not self.config.model_selection.auto_select:
            # Use default model (no auto-selection)
            model = self.config.model_selection.default_model
            max_tokens = 1024
            logger.info(f"Using default model: {model}")
        else:
            # Auto-select model based on complexity
            model, max_tokens = ModelSelector.select_model(
                context_size=estimated_tokens,
                agent_count=len(self.available_agents),
                confidence_threshold=0.5,
            )

        # Check if caching is enabled
        caching_enabled = use_caching and (
            self.config is None or self.config.caching.enabled
        )

        # Build system message with prompt caching
        # The agent catalog rarely changes, so it's an ideal candidate for caching
        system_messages = []

        if caching_enabled:
            # Cache the agent catalog (static, rarely changes)
            system_messages.append(
                {
                    "type": "text",
                    "text": f"""You are an AI development assistant analyzer. Based on the current development context, recommend which specialized agents should be activated.

## Available Agents
{agent_catalog}

## Task Instructions
Analyze the context and recommend agents. For each recommendation, provide:
1. agent_name (must match available agents exactly)
2. confidence (0.0-1.0)
3. reason (brief explanation)
4. urgency (low/medium/high/critical)
5. auto_activate (true if confidence > 0.8 AND urgency is high/critical)

Respond with a JSON array of recommendations, ordered by priority.
Only recommend agents that would genuinely help with the detected context.
If no agents are clearly relevant, return an empty array.""",
                    "cache_control": {"type": "ephemeral"},
                }
            )
        else:
            # No caching
            system_messages.append(
                {
                    "type": "text",
                    "text": f"""You are an AI development assistant analyzer. Based on the current development context, recommend which specialized agents should be activated.

## Available Agents
{agent_catalog}

## Task Instructions
Analyze the context and recommend agents. For each recommendation, provide:
1. agent_name (must match available agents exactly)
2. confidence (0.0-1.0)
3. reason (brief explanation)
4. urgency (low/medium/high/critical)
5. auto_activate (true if confidence > 0.8 AND urgency is high/critical)

Respond with a JSON array of recommendations, ordered by priority.
Only recommend agents that would genuinely help with the detected context.
If no agents are clearly relevant, return an empty array.""",
                }
            )

        # User message with current context (changes frequently, don't cache)
        user_prompt = f"""## Current Context
{context_summary}

## Recent Session History
{history}

JSON response:"""

        try:
            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=system_messages,
                messages=[{"role": "user", "content": user_prompt}],
            )

            # Extract usage statistics
            usage = response.usage
            input_tokens = usage.input_tokens
            output_tokens = usage.output_tokens

            # Check for cache hit
            cache_creation_tokens = getattr(usage, "cache_creation_input_tokens", 0)
            cache_read_tokens = getattr(usage, "cache_read_input_tokens", 0)

            # Calculate costs
            cost_info = ModelSelector.calculate_cost(model, input_tokens, output_tokens)

            # Parse response
            text = response.content[0].text

            # Handle potential markdown code blocks
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]

            recs_data = json.loads(text.strip())

            logger.info(
                f"LLM provided {len(recs_data)} recommendations using {cost_info['model_name']} "
                f"(cost: ${cost_info['total_cost']:.6f}, "
                f"cache_hit: {cache_read_tokens > 0})"
            )

            return {
                "recommendations": recs_data,
                "metadata": {
                    "model": model,
                    "model_name": cost_info["model_name"],
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "cache_creation_tokens": cache_creation_tokens,
                    "cache_read_tokens": cache_read_tokens,
                    "cache_hit": cache_read_tokens > 0,
                    "cost": cost_info,
                    "timestamp": json.dumps(
                        __import__("datetime").datetime.now(
                            __import__("datetime").timezone.utc
                        ),
                        default=str,
                    ),
                },
            }

        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            return {
                "recommendations": [],
                "metadata": {
                    "error": str(e),
                    "model": model,
                    "timestamp": json.dumps(
                        __import__("datetime").datetime.now(
                            __import__("datetime").timezone.utc
                        ),
                        default=str,
                    ),
                },
            }

    def _format_agent_catalog(self) -> str:
        """Format available agents for the prompt."""
        lines = []
        for agent in self.available_agents:
            name = agent.get("name", "unknown")
            desc = agent.get("summary", agent.get("description", "No description"))
            lines.append(f"- {name}: {desc}")
        return "\n".join(lines)

    def _format_context(self, context: dict[str, Any]) -> str:
        """Format context for the prompt."""
        files = context.get("files_changed", [])
        file_types = context.get("file_types", [])
        directories = context.get("directories", [])

        return f"""Files changed: {len(files)}
File types: {', '.join(file_types) or 'none'}
Directories: {', '.join(list(directories)[:10]) or 'none'}
Signals detected:
  - Tests: {context.get('has_tests', False)}
  - Auth: {context.get('has_auth', False)}
  - API: {context.get('has_api', False)}
  - Frontend: {context.get('has_frontend', False)}
  - Backend: {context.get('has_backend', False)}
  - Database: {context.get('has_database', False)}
Errors: {context.get('errors_count', 0)}
Test failures: {context.get('test_failures', 0)}
Sample files: {', '.join(files[:10])}"""

    def _format_history(self, sessions: list[dict[str, Any]]) -> str:
        """Format session history for the prompt."""
        if not sessions:
            return "No history."

        lines = []
        for i, session in enumerate(sessions[:5], 1):
            agents = session.get("agents", [])
            outcome = session.get("outcome", "unknown")
            lines.append(f"{i}. Agents: {', '.join(agents)} | Outcome: {outcome}")

        return "\n".join(lines)
