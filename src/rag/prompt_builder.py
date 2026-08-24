from typing import Optional


class PromptBuilder:
    """Constructs structured, grounded RAG prompts for LLM completion."""

    DEFAULT_SYSTEM_PROMPT = (
        "You are an Enterprise Knowledge Intelligence Assistant. "
        "Your task is to answer the user's question accurately based strictly on the provided Context Information. "
        "Do not invent facts, speculate, or draw upon unverified outside information. "
        "If the context does not contain sufficient information to answer the question, clearly state that."
    )

    @staticmethod
    def build_prompt(query: str, formatted_context: str) -> str:
        prompt = (
            f"Context Information:\n"
            f"---------------------\n"
            f"{formatted_context}\n"
            f"---------------------\n\n"
            f"Question: {query}\n\n"
            f"Answer the question based strictly on the context above. Include citations or document names where applicable."
        )
        return prompt
