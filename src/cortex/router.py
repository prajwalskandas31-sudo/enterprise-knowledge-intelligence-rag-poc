import re
from enum import Enum
from typing import Optional
from pydantic import BaseModel


class QueryDestination(str, Enum):
    CORTEX_ANALYST = "cortex_analyst"
    RAG = "rag"


class QueryRouteResult(BaseModel):
    destination: QueryDestination
    reasoning: str
    confidence: float


class QueryRouter:
    """Lightweight rule-based query classifier routing questions to Cortex Analyst vs Enterprise RAG."""

    STRUCTURED_KEYWORDS = [
        r"\brevenue\b",
        r"\bannual_revenue\b",
        r"\bcustomer(s)?\b",
        r"\bcity\b",
        r"\bcities\b",
        r"\bindustry\b",
        r"\bindustries\b",
        r"\baverage\b",
        r"\bavg\b",
        r"\btotal\b",
        r"\bsum\b",
        r"\bhighest\b",
        r"\blowest\b",
        r"\bmost\b",
        r"\bleast\b",
        r"\bcount\b",
        r"\bhow many\b",
        r"\btop\s+\d+\b",
        r"\bmillion\b",
        r"\bbillion\b",
        r"\bsql\b",
        r"\bmetrics?\b",
    ]

    DOCUMENT_KEYWORDS = [
        r"\bpolicy\b",
        r"\bpolicies\b",
        r"\bguideline(s)?\b",
        r"\bdocument(s)?\b",
        r"\bsecurity\b",
        r"\bremote work\b",
        r"\bvpn\b",
        r"\bpassword(s)?\b",
        r"\bhr\b",
        r"\bhandbook\b",
        r"\baccess\b",
        r"\bretention\b",
        r"\bcompliance\b",
        r"\bprocedure(s)?\b",
    ]

    @classmethod
    def route(cls, query: str, mode: Optional[str] = "auto") -> QueryRouteResult:
        """Determines the appropriate query engine for a user's question."""
        if mode and mode.lower() in [QueryDestination.CORTEX_ANALYST.value, "cortex"]:
            return QueryRouteResult(
                destination=QueryDestination.CORTEX_ANALYST,
                reasoning="Explicit user request override for Cortex Analyst.",
                confidence=1.0,
            )
        
        if mode and mode.lower() in [QueryDestination.RAG.value, "rag_pipeline"]:
            return QueryRouteResult(
                destination=QueryDestination.RAG,
                reasoning="Explicit user request override for Enterprise RAG.",
                confidence=1.0,
            )

        query_lower = query.lower()

        structured_matches = sum(1 for pat in cls.STRUCTURED_KEYWORDS if re.search(pat, query_lower))
        document_matches = sum(1 for pat in cls.DOCUMENT_KEYWORDS if re.search(pat, query_lower))

        if structured_matches > document_matches:
            return QueryRouteResult(
                destination=QueryDestination.CORTEX_ANALYST,
                reasoning=f"Matched {structured_matches} structured data analytics keyword(s).",
                confidence=min(0.6 + (0.1 * structured_matches), 0.95),
            )
        elif document_matches > structured_matches:
            return QueryRouteResult(
                destination=QueryDestination.RAG,
                reasoning=f"Matched {document_matches} enterprise document knowledge keyword(s).",
                confidence=min(0.6 + (0.1 * document_matches), 0.95),
            )
        else:
            # Default fallback strategy: if any structured keyword matched, lean cortex, else RAG
            if structured_matches > 0:
                return QueryRouteResult(
                    destination=QueryDestination.CORTEX_ANALYST,
                    reasoning="Defaulted to Cortex Analyst due to quantitative query terms.",
                    confidence=0.51,
                )
            return QueryRouteResult(
                destination=QueryDestination.RAG,
                reasoning="Defaulted to Enterprise RAG document store.",
                confidence=0.5,
            )
