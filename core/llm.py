# core/llm.py
import os
import json
import logging
from functools import lru_cache

import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "").strip()
DEEPSEEK_BASE = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"


def get_llm():
    """
    Returns a placeholder for the LLM.
    """
    return None


@lru_cache(maxsize=128)
async def generate_report_with_deepseek(report_data: str, language: str = "en") -> str:
    """
    Generates a report using the DeepSeek API with caching.
    The report_data is a JSON string to be cacheable.
    Returns a local placeholder if the API key is not set.
    """
    if not DEEPSEEK_API_KEY:
        logger.info("DEEPSEEK_API_KEY not set, returning local placeholder.")
        return (
            f"[LOCAL REPORT] City snapshot in {language}\n"
            f"- Data: {report_data}\n"
            "- Tip: Set the DEEPSEEK_API_KEY environment variable to use the real LLM."
        )

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }

    system_prompt = (
        "You are an assistant that writes concise city-status reports. "
        "Return 6–10 bullet points and a short recommendation section. "
        f"Write in {language}."
    )

    user_prompt = f"Generate a city analysis report based on the following data: {report_data}"

    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.3,
    }

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            logger.info(f"Generating report for: {report_data}")
            r = await client.post(DEEPSEEK_BASE, json=payload, headers=headers)
            r.raise_for_status()
            data = r.json()
            report = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            if not report:
                logger.error(f"Malformed API response: {data}")
                return "[API ERROR] Malformed API response"
            return report
        except httpx.HTTPStatusError as e:
            logger.error(f"API request failed with status {e.response.status_code}: {e.response.text}")
            return f"[API ERROR] Failed to generate report: {e.response.status_code}"
        except Exception as e:
            logger.exception("An unexpected error occurred during report generation.")
            return f"[UNEXPECTED ERROR] An unexpected error occurred: {e}"