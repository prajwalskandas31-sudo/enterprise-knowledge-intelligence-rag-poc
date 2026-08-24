import os
import requests
from dotenv import load_dotenv

load_dotenv()

account_url = os.getenv("SNOWFLAKE_BASE_URL")
pat = os.getenv("SNOWFLAKE_PAT")
semantic_view = os.getenv("SNOWFLAKE_SEMANTIC_VIEW")

url = f"{account_url}/api/v2/cortex/analyst/message"

headers = {
    "Authorization": f"Bearer {pat}",
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
                    "text": "Which city has the highest average customer revenue?"
                }
            ],
        }
    ],
    "semantic_view": semantic_view,
}

response = requests.post(
    url,
    headers=headers,
    json=payload,
    timeout=120,
)

print("STATUS:", response.status_code)
print()

try:
    print(response.json())
except Exception:
    print(response.text)