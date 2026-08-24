import unittest
from src.cortex.router import QueryRouter, QueryDestination


class TestQueryRouter(unittest.TestCase):

    def test_structured_analytics_routing(self):
        structured_queries = [
            "Which city has the highest average customer revenue?",
            "What is the total annual revenue across all customers?",
            "Which industry has the most customers?",
            "Show customers with annual_revenue above 10 million.",
            "What is the average revenue per customer?",
            "How many customers are in Chicago?",
        ]
        for q in structured_queries:
            res = QueryRouter.route(q, mode="auto")
            self.assertEqual(
                res.destination,
                QueryDestination.CORTEX_ANALYST,
                f"Query '{q}' should route to Cortex Analyst, got {res.destination}",
            )

    def test_document_knowledge_routing(self):
        document_queries = [
            "What is our password security policy?",
            "What does the enterprise security policy say about remote access?",
            "What are the HR guidelines?",
            "What does the security document say about VPN access?",
            "Explain the data retention procedures.",
        ]
        for q in document_queries:
            res = QueryRouter.route(q, mode="auto")
            self.assertEqual(
                res.destination,
                QueryDestination.RAG,
                f"Query '{q}' should route to RAG, got {res.destination}",
            )

    def test_explicit_mode_override(self):
        res = QueryRouter.route("What is our password security policy?", mode="cortex_analyst")
        self.assertEqual(res.destination, QueryDestination.CORTEX_ANALYST)

        res = QueryRouter.route("Which city has highest revenue?", mode="rag")
        self.assertEqual(res.destination, QueryDestination.RAG)


if __name__ == "__main__":
    unittest.main()
