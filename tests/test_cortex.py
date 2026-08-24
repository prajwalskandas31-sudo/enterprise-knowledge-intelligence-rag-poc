import unittest
from unittest.mock import patch, MagicMock
from src.cortex.analyst import CortexAnalystClient, CortexAnalystResponse


class TestCortexAnalystClient(unittest.TestCase):

    def setUp(self):
        self.client = CortexAnalystClient(
            base_url="https://test-account.snowflakecomputing.com",
            pat="test_pat_token_12345",
            semantic_view="FDP_CORTEX_POC.RAW_DATA.CUSTOMER_ANALYTICS",
        )

    def test_configuration_loading(self):
        self.assertTrue(self.client.is_configured())
        self.assertEqual(self.client.endpoint_url, "https://test-account.snowflakecomputing.com/api/v2/cortex/analyst/message")

    @patch("requests.post")
    def test_request_payload_and_headers_construction(self, mock_post):
        mock_cortex_res = MagicMock()
        mock_cortex_res.status_code = 200
        mock_cortex_res.json.return_value = {
            "message": {
                "role": "analyst",
                "content": [
                    {"type": "text", "text": "Which city has highest revenue?"},
                    {"type": "sql", "statement": "SELECT city FROM customers;"}
                ]
            },
            "request_id": "test-req-id-123"
        }

        mock_sql_res = MagicMock()
        mock_sql_res.status_code = 200
        mock_sql_res.json.return_value = {
            "resultSetMetaData": {
                "rowType": [{"name": "CITY"}]
            },
            "data": [["New York"], ["Chicago"]]
        }

        mock_post.side_effect = [mock_cortex_res, mock_sql_res]

        res = self.client.query("Which city has highest revenue?")

        self.assertTrue(res.success)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.request_id, "test-req-id-123")
        self.assertIn("Which city has highest revenue?", res.answer)
        self.assertEqual(res.sql, "SELECT city FROM customers;")
        self.assertIsNotNone(res.query_results)
        self.assertEqual(res.query_results["columns"], ["CITY"])
        self.assertEqual(res.query_results["rows"], [["New York"], ["Chicago"]])

    @patch("requests.post")
    def test_cortex_response_parsing_verified_query(self, mock_post):
        mock_cortex_res = MagicMock()
        mock_cortex_res.status_code = 200
        mock_cortex_res.json.return_value = {
            "message": {
                "role": "analyst",
                "content": [
                    {"type": "text", "text": "Top city is Chicago"},
                    {
                        "type": "sql",
                        "statement": "SELECT city, AVG(annual_revenue) FROM customers GROUP BY city LIMIT 1;",
                        "confidence": {
                            "verified_query_used": {
                                "name": "VQR_1",
                                "question": "Top city by revenue"
                            }
                        }
                    }
                ]
            },
            "request_id": "req-999"
        }

        mock_sql_res = MagicMock()
        mock_sql_res.status_code = 200
        mock_sql_res.json.return_value = {
            "resultSetMetaData": {
                "rowType": [{"name": "CITY"}, {"name": "AVG_REVENUE"}]
            },
            "data": [["Chicago", 500000]]
        }

        mock_post.side_effect = [mock_cortex_res, mock_sql_res]

        res = self.client.query("Top city by revenue")

        self.assertTrue(res.success)
        self.assertTrue(res.verified_query_used)
        self.assertEqual(res.request_id, "req-999")
        self.assertIn("Chicago", res.answer)
        self.assertEqual(res.query_results["columns"], ["CITY", "AVG_REVENUE"])

    @patch("requests.post")
    def test_execute_sql_direct(self, mock_post):
        mock_sql_res = MagicMock()
        mock_sql_res.status_code = 200
        mock_sql_res.json.return_value = {
            "resultSetMetaData": {
                "rowType": [{"name": "STATE"}, {"name": "TOTAL_CUSTOMERS"}]
            },
            "data": [["CA", 120], ["NY", 95]]
        }
        mock_post.return_value = mock_sql_res

        res = self.client.execute_sql("SELECT state, count(*) FROM customers GROUP BY state;")
        self.assertTrue(res["success"])
        self.assertEqual(res["columns"], ["STATE", "TOTAL_CUSTOMERS"])
        self.assertEqual(res["row_count"], 2)
        self.assertEqual(res["rows"], [["CA", 120], ["NY", 95]])

    @patch("requests.post")
    def test_error_response_handling(self, mock_post):
        # Test 401
        mock_401 = MagicMock()
        mock_401.status_code = 401
        mock_401.json.return_value = {"code": "390432", "message": "Fail : Network policy is required."}
        mock_post.return_value = mock_401

        res = self.client.query("Test query")
        self.assertFalse(res.success)
        self.assertEqual(res.status_code, 401)
        self.assertIn("Authentication error", res.answer)

        # Test 400
        mock_400 = MagicMock()
        mock_400.status_code = 400
        mock_400.json.return_value = {"message": "Invalid semantic view"}
        mock_post.return_value = mock_400

        res = self.client.query("Test query")
        self.assertFalse(res.success)
        self.assertEqual(res.status_code, 400)
        self.assertIn("Bad request", res.answer)


if __name__ == "__main__":
    unittest.main()
