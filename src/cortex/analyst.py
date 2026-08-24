import time
import requests
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from src.config import settings


class CortexAnalystResponse(BaseModel):
    """Normalized internal response structure for Snowflake Cortex Analyst queries."""
    success: bool = True
    status_code: int = 200
    answer: str = ""
    sql: Optional[str] = None
    query_results: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None
    verified_query_used: bool = False
    confidence: Optional[Dict[str, Any]] = None
    model_names: List[str] = Field(default_factory=list)
    warnings: List[Any] = Field(default_factory=list)
    error_message: Optional[str] = None
    latency_ms: float = 0.0


class CortexAnalystClient:
    """Dedicated service for communicating with Snowflake Cortex Analyst REST API."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        pat: Optional[str] = None,
        semantic_view: Optional[str] = None,
        timeout: int = 120,
    ):
        self.base_url = (base_url or settings.snowflake_base_url).rstrip("/")
        self.pat = pat or settings.snowflake_pat
        self.semantic_view = semantic_view or settings.snowflake_semantic_view
        self.timeout = timeout

    @property
    def endpoint_url(self) -> str:
        return f"{self.base_url}/api/v2/cortex/analyst/message"

    def is_configured(self) -> bool:
        """Check if required Snowflake Cortex configuration parameters are present."""
        return bool(self.base_url and self.pat and self.semantic_view)

    def execute_sql(self, sql_statement: str) -> Optional[Dict[str, Any]]:
        """Executes a SQL query on Snowflake via the Snowflake SQL REST API (/api/v2/statements)."""
        if not self.base_url or not self.pat:
            return {
                "success": False,
                "columns": [],
                "rows": [],
                "row_count": 0,
                "error": "Missing Snowflake base URL or PAT credentials.",
            }

        url = f"{self.base_url}/api/v2/statements"
        headers = {
            "Authorization": f"Bearer {self.pat}",
            "X-Snowflake-Authorization-Token-Type": "PROGRAMMATIC_ACCESS_TOKEN",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        payload = {
            "statement": sql_statement,
            "timeout": self.timeout,
            "database": settings.snowflake_database,
            "schema": settings.snowflake_schema,
            "warehouse": settings.snowflake_warehouse,
            "role": settings.snowflake_role,
        }

        try:
            res = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
            if res.status_code != 200:
                err_text = ""
                try:
                    err_json = res.json()
                    err_text = err_json.get("message", res.text)
                except Exception:
                    err_text = res.text
                return {
                    "success": False,
                    "columns": [],
                    "rows": [],
                    "row_count": 0,
                    "error": f"Snowflake SQL API execution failed (HTTP {res.status_code}): {err_text}",
                }

            data = res.json()
            row_type = data.get("resultSetMetaData", {}).get("rowType", [])
            columns = [col.get("name", f"COL_{idx+1}") for idx, col in enumerate(row_type)]
            rows = data.get("data", [])

            return {
                "success": True,
                "columns": columns,
                "rows": rows,
                "row_count": len(rows),
                "error": None,
            }
        except Exception as e:
            return {
                "success": False,
                "columns": [],
                "rows": [],
                "row_count": 0,
                "error": f"Exception executing SQL query: {str(e)}",
            }

    def query(self, question: str) -> CortexAnalystResponse:
        """Sends a natural language question to Snowflake Cortex Analyst REST API."""
        start_time = time.time()

        if not self.is_configured():
            return CortexAnalystResponse(
                success=False,
                status_code=401,
                answer="Snowflake Cortex Analyst is not configured. Missing SNOWFLAKE_PAT or base URL.",
                error_message="Authentication credentials or base URL missing from environment.",
                latency_ms=round((time.time() - start_time) * 1000, 2),
            )

        headers = {
            "Authorization": f"Bearer {self.pat}",
            "X-Snowflake-Authorization-Token-Type": "PROGRAMMATIC_ACCESS_TOKEN",
            "Content-Type": "application/json",
        }

        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": question,
                        }
                    ],
                }
            ],
            "semantic_view": self.semantic_view,
        }

        try:
            response = requests.post(
                self.endpoint_url,
                headers=headers,
                json=payload,
                timeout=self.timeout,
            )
        except requests.exceptions.RequestException as e:
            latency = round((time.time() - start_time) * 1000, 2)
            return CortexAnalystResponse(
                success=False,
                status_code=503,
                answer="Unable to reach Snowflake Cortex Analyst service. Network or connection failure.",
                error_message=f"Request exception: {type(e).__name__}",
                latency_ms=latency,
            )

        latency = round((time.time() - start_time) * 1000, 2)

        if response.status_code != 200:
            return self._handle_error_response(response, latency)

        try:
            data = response.json()
        except Exception:
            return CortexAnalystResponse(
                success=False,
                status_code=response.status_code,
                answer="Received invalid response format from Snowflake Cortex Analyst.",
                error_message="Failed to parse JSON response payload.",
                latency_ms=latency,
            )

        return self._parse_cortex_response(data, latency)

    def _parse_cortex_response(self, data: Dict[str, Any], latency_ms: float) -> CortexAnalystResponse:
        message = data.get("message", {})
        contents = message.get("content", [])

        text_parts = []
        sql_statement = None
        verified_query_used = False
        confidence = None

        for item in contents:
            item_type = item.get("type")
            if item_type == "text":
                text_val = item.get("text", "").strip()
                if text_val:
                    text_parts.append(text_val)
            elif item_type == "sql":
                sql_statement = item.get("statement", "").strip()
                confidence_meta = item.get("confidence", {})
                if confidence_meta:
                    confidence = confidence_meta
                    if "verified_query_used" in confidence_meta and confidence_meta["verified_query_used"]:
                        verified_query_used = True

        answer_text = "\n\n".join(text_parts) if text_parts else "Analyst response received."
        req_id = data.get("request_id")
        warnings = data.get("warnings", [])

        query_results = None
        if sql_statement:
            query_results = self.execute_sql(sql_statement)

        return CortexAnalystResponse(
            success=True,
            status_code=200,
            answer=answer_text,
            sql=sql_statement,
            query_results=query_results,
            request_id=req_id,
            verified_query_used=verified_query_used,
            confidence=confidence,
            warnings=warnings,
            latency_ms=latency_ms,
        )

    def _handle_error_response(self, response: requests.Response, latency_ms: float) -> CortexAnalystResponse:
        status = response.status_code
        err_msg = ""
        user_answer = ""

        try:
            err_json = response.json()
            err_msg = err_json.get("message", response.text)
        except Exception:
            err_msg = response.text

        if status == 401:
            user_answer = "Authentication error (401): Invalid Snowflake Programmatic Access Token (PAT) or network policy restriction."
        elif status == 403:
            user_answer = "Permission error (403): Current Snowflake role lacks privileges to access Cortex Analyst or the semantic view."
        elif status == 400:
            user_answer = f"Bad request (400): Snowflake Cortex Analyst reported an issue with the query or semantic view: {err_msg}"
        elif status == 404:
            user_answer = "Not found (404): Invalid Snowflake Cortex Analyst endpoint URL or account configuration."
        elif status == 429:
            user_answer = "Rate limited (429): Snowflake Cortex Analyst request quota exceeded. Please retry shortly."
        else:
            user_answer = f"Snowflake Cortex Analyst error (HTTP {status}): {err_msg}"

        return CortexAnalystResponse(
            success=False,
            status_code=status,
            answer=user_answer,
            error_message=err_msg,
            latency_ms=latency_ms,
        )
