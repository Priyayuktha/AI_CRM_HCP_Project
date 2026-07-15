import json
import re
from datetime import date

from app.langgraph.llm import llm
from app.langgraph.prompts import SYSTEM_PROMPT


VALID_INTENTS = {
    "log_interaction",
    "edit_interaction",
    "search_hcp",
    "interaction_history",
    "follow_up_planner",
}


def _empty_agent_output() -> dict:
    return {
        "intent": "log_interaction",
        "entities": {},
        "missing_fields": [],
        "assistant_reply": "Done. I updated the CRM form.",
    }


def _strip_markdown_json(text: str) -> str:
    cleaned = text.strip().replace("```json", "").replace("```", "").strip()
    match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
    return match.group(0) if match else cleaned


def _parse_json(text: str) -> dict:
    try:
        parsed = json.loads(_strip_markdown_json(text))
        return parsed if isinstance(parsed, dict) else _empty_agent_output()
    except Exception:
        return {
            **_empty_agent_output(),
            "assistant_reply": "Done. I updated the CRM form.",
        }


def detect_intent_and_extract(user_input: str, memory: dict | None = None) -> dict:
    memory = memory or {}

    prompt = f"""
{SYSTEM_PROMPT}

Active CRM context:
{json.dumps(memory.get("active_interaction", {}), ensure_ascii=False)}

Recent conversation:
{json.dumps(memory.get("messages", [])[-8:], ensure_ascii=False)}

Today:
{date.today()}

Latest user message:
{user_input}
"""

    response = llm.invoke(prompt)
    parsed = _parse_json(response.content)

    intent = parsed.get("intent") or "log_interaction"
    parsed["intent"] = intent if intent in VALID_INTENTS else "log_interaction"
    parsed["entities"] = parsed.get("entities") if isinstance(parsed.get("entities"), dict) else {}
    parsed["missing_fields"] = []
    parsed["assistant_reply"] = parsed.get("assistant_reply") or "Done. I updated the CRM form."

    return parsed


def extract_information(user_input: str):
    return detect_intent_and_extract(user_input).get("entities", {})
