import re
from datetime import date, timedelta

from app.langgraph.agent import detect_intent_and_extract
from app.database import SessionLocal
from app.models.interaction import Interaction
from app.tools.create_hcp import create_hcp
from app.tools.create_interaction import create_interaction
from app.tools.follow_up_planner import follow_up_planner
from app.tools.get_history import get_history
from app.tools.search_hcp import search_hcp
from app.tools.update_hcp import update_hcp
from app.tools.update_interaction import update_interaction


CONVERSATION_MEMORY = {
    "default": {
        "messages": [],
        "active_interaction": {},
        "last_interaction_id": None,
        "last_hcp_id": None,
    }
}


FOLLOW_UP_FIELDS = ("Follow-up Date", "Next Action", "Priority", "Status", "Follow-up Operation")
WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}

MATERIAL_RULES = (
    ("Brochure", ("brochure", "pamphlet", "leaflet")),
    ("Sample Kit", ("sample kit", "medicine sample", "medicine samples", "samples", "drug sample", "starter kit")),
    ("Prescription", ("prescription", "prescribed", "rx", "script")),
    ("Clinical Trial Document", ("clinical trial", "trial document", "study document", "trial protocol")),
    ("Medical Report", ("medical report", "blood test report", "lab report", "diagnostic report", "report reviewed", "reports")),
    ("Leave Behind Literature", ("leave behind", "leave-behind", "literature")),
)


def _memory():
    return CONVERSATION_MEMORY["default"]


def _clean_entities(data: dict) -> dict:
    cleaned = {}
    for key, value in (data or {}).items():
        if value not in ("", None, [], {}):
            cleaned[key] = value
    return cleaned


def _normalize_follow_up_aliases(data: dict) -> dict:
    normalized = dict(data or {})
    if normalized.get("Follow-up Priority") and not normalized.get("Priority"):
        normalized["Priority"] = normalized["Follow-up Priority"]
    if normalized.get("Follow-up Status") and not normalized.get("Status"):
        normalized["Status"] = normalized["Follow-up Status"]
    if normalized.get("Follow Up Date") and not normalized.get("Follow-up Date"):
        normalized["Follow-up Date"] = normalized["Follow Up Date"]
    return normalized


def _append_unique(existing: str, values: list[str], separator: str = ", ") -> str:
    current = [
        item.strip()
        for item in str(existing or "").split(",")
        if item and item.strip()
    ]
    current_lower = {item.lower() for item in current}
    for value in values:
        if value and value.lower() not in current_lower:
            current.append(value)
            current_lower.add(value.lower())
    return separator.join(current)


def _append_unique_sentences(existing: str, values: list[str]) -> str:
    current = str(existing or "").strip()
    current_lower = current.lower()
    additions = [
        value.strip().rstrip(".")
        for value in values
        if value and value.strip().lower().rstrip(".") not in current_lower
    ]
    if not additions:
        return current
    suffix = ". ".join(additions) + "."
    return f"{current.rstrip('. ')}. {suffix}" if current else suffix


def _detect_materials(user_input: str) -> list[str]:
    lowered = user_input.lower()
    detected = []
    for label, keywords in MATERIAL_RULES:
        if any(keyword in lowered for keyword in keywords):
            detected.append(label)
    return detected


def _detect_clinical_outcomes(user_input: str) -> list[str]:
    patterns = (
        r"\b(?:the\s+)?doctor\s+suggested\s+([^.;\n]+)",
        r"\b(?:the\s+)?doctor\s+recommended\s+([^.;\n]+)",
        r"\b(?:the\s+)?patient\s+was\s+advised\s+([^.;\n]+)",
        r"\b(?:the\s+)?doctor\s+advised\s+([^.;\n]+)",
        r"\b(?:the\s+)?doctor\s+prescribed\s+([^.;\n]+)",
        r"\b([^.;\n]*\breport\s+was\s+reviewed\b[^.;\n]*)",
        r"\b([^.;\n]*\breports\s+were\s+reviewed\b[^.;\n]*)",
    )
    outcomes = []
    lowered = user_input.lower()
    for pattern in patterns:
        for match in re.finditer(pattern, user_input, flags=re.IGNORECASE):
            if "prescribed" in pattern:
                outcomes.append(f"Doctor prescribed {match.group(1).strip()}")
            elif "suggested" in pattern:
                outcomes.append(f"Doctor suggested {match.group(1).strip()}")
            elif "recommended" in pattern:
                outcomes.append(f"Doctor recommended {match.group(1).strip()}")
            elif "patient" in pattern:
                outcomes.append(f"Patient was advised {match.group(1).strip()}")
            elif "doctor" in pattern:
                outcomes.append(f"Doctor advised {match.group(1).strip()}")
            else:
                report_text = match.group(1).strip()
                if "blood test report" in report_text.lower():
                    outcomes.append("Blood test report was reviewed")
                else:
                    outcomes.append(report_text.capitalize())

    if "blood test report was reviewed" in lowered and not any("blood test report" in item.lower() for item in outcomes):
        outcomes.append("Blood test report was reviewed")

    unique = []
    seen = set()
    for outcome in outcomes:
        normalized = re.sub(r"\s+", " ", outcome).strip(" ,")
        if normalized and normalized.lower() not in seen:
            unique.append(normalized)
            seen.add(normalized.lower())
    return unique


def _augment_extractions(data: dict, user_input: str) -> dict:
    augmented = dict(data)
    materials = _detect_materials(user_input)
    if materials:
        augmented["Materials Shared"] = _append_unique(augmented.get("Materials Shared", ""), materials)
        if "Sample Kit" in materials and not augmented.get("Samples Distributed"):
            augmented["Samples Distributed"] = "Sample Kit"

    clinical_outcomes = _detect_clinical_outcomes(user_input)
    if clinical_outcomes:
        augmented["Outcome"] = _append_unique_sentences(augmented.get("Outcome", ""), clinical_outcomes)
        augmented["Summary"] = _append_unique_sentences(augmented.get("Summary", ""), clinical_outcomes)

    return augmented


def _normalize_date(value):
    if not isinstance(value, str):
        return value

    lowered = value.strip().lower()
    if lowered == "today":
        return str(date.today())
    if lowered == "tomorrow":
        return str(date.today() + timedelta(days=1))
    if lowered == "yesterday":
        return str(date.today() - timedelta(days=1))
    if "after" in lowered or "in " in lowered:
        import re

        match = re.search(r"(?:after|in)\s+(\d+)\s+day", lowered)
        if match:
            return str(date.today() + timedelta(days=int(match.group(1))))
    for weekday, index in WEEKDAYS.items():
        if weekday in lowered:
            days_ahead = (index - date.today().weekday()) % 7
            if days_ahead == 0 or "next" in lowered:
                days_ahead += 7
            return str(date.today() + timedelta(days=days_ahead))
    return value


def _infer_defaults(data: dict, user_input: str, intent: str) -> dict:
    if intent != "log_interaction":
        return data

    lowered = user_input.lower()
    has_interaction_signal = any(
        value
        for key, value in data.items()
        if key in ("Doctor Name", "Hospital", "Topics Discussed", "Materials Shared", "Sentiment")
    )

    if has_interaction_signal and not data.get("Interaction Type"):
        data["Interaction Type"] = "Meeting"

    if "today" in lowered and not data.get("Interaction Date"):
        data["Interaction Date"] = str(date.today())

    if data.get("Topics Discussed") and not data.get("Summary"):
        data["Summary"] = f"Discussed {data['Topics Discussed']}."

    if data.get("Follow-up Date") and not data.get("Status"):
        data["Status"] = "Planned"

    if data.get("Follow-up Date") and not data.get("Priority"):
        data["Priority"] = "Medium"

    return data


def _merge_active_interaction(memory: dict, extracted: dict, user_input: str, intent: str) -> dict:
    merged = {
        **memory.get("active_interaction", {}),
        **_clean_entities(extracted),
    }
    merged = _infer_defaults(merged, user_input, intent)

    for date_key in ("Interaction Date", "Follow-up Date"):
        if date_key in merged:
            merged[date_key] = _normalize_date(merged[date_key])

    memory["active_interaction"] = merged
    return merged


def _ensure_hcp(data: dict, memory: dict) -> int | None:
    if data.get("hcp_id"):
        memory["last_hcp_id"] = data.get("hcp_id")
        return data.get("hcp_id")

    if memory.get("last_hcp_id") and not data.get("Doctor Name"):
        return memory["last_hcp_id"]

    if not data.get("Doctor Name"):
        return None

    search_result = search_hcp(data)
    hcp = search_result.get("hcp") if isinstance(search_result, dict) else None
    if hcp and hcp.get("id"):
        memory["last_hcp_id"] = hcp["id"]
        return hcp["id"]

    created = create_hcp(data)
    hcp_id = created.get("hcp_id") if isinstance(created, dict) else None
    if hcp_id:
        memory["last_hcp_id"] = hcp_id
    return hcp_id


def _find_hcp_id(data: dict, memory: dict) -> int | None:
    if data.get("hcp_id"):
        return data.get("hcp_id")

    if not data.get("Doctor Name"):
        if memory.get("last_hcp_id"):
            return memory.get("last_hcp_id")
        _latest_interaction_id(memory)
        return memory.get("last_hcp_id")

    search_result = search_hcp(data)
    hcp = search_result.get("hcp") if isinstance(search_result, dict) else None
    if hcp and hcp.get("id"):
        memory["last_hcp_id"] = hcp["id"]
        return hcp["id"]

    return None


def _update_active_hcp(data: dict, memory: dict) -> dict | None:
    hcp_id = data.get("hcp_id") or memory.get("last_hcp_id")
    hcp_fields = {
        key: value
        for key, value in data.items()
        if key in ("Doctor Name", "Hospital", "City", "Specialization", "Email", "Phone") and value
    }

    if not hcp_id or not hcp_fields:
        return None

    result = update_hcp({**hcp_fields, "hcp_id": hcp_id})
    if result.get("status") == "success":
        memory["last_hcp_id"] = hcp_id
    return result


def _latest_interaction_id(memory: dict) -> int | None:
    if memory.get("last_interaction_id"):
        return memory["last_interaction_id"]

    db = SessionLocal()
    try:
        interaction = (
            db.query(Interaction)
            .order_by(Interaction.created_at.desc(), Interaction.id.desc())
            .first()
        )
        if not interaction:
            return None
        memory["last_interaction_id"] = interaction.id
        if interaction.hcp_id:
            memory["last_hcp_id"] = interaction.hcp_id
        return interaction.id
    finally:
        db.close()


def reset_conversation_memory():
    memory = _memory()
    memory["messages"] = []
    memory["active_interaction"] = {}
    memory["last_interaction_id"] = None
    memory["last_hcp_id"] = None
    return memory


def extract_node(state):
    memory = _memory()
    user_input = state["user_input"]

    agent_output = detect_intent_and_extract(user_input, memory)
    extracted = _normalize_follow_up_aliases(_clean_entities(agent_output.get("entities", {})))
    for date_key in ("Interaction Date", "Follow-up Date"):
        if date_key in extracted:
            extracted[date_key] = _normalize_date(extracted[date_key])
    extracted = _augment_extractions(extracted, user_input)
    intent = agent_output.get("intent", "log_interaction")
    active_interaction = _merge_active_interaction(memory, extracted, user_input, intent)

    memory["messages"].append({"role": "user", "content": user_input})

    state["agent_output"] = agent_output
    state["intent"] = intent
    state["extracted_patch"] = extracted
    state["extracted_data"] = active_interaction
    state["missing_fields"] = agent_output.get("missing_fields", [])
    state["assistant_reply"] = agent_output.get("assistant_reply", "")
    state["memory"] = memory
    return state


def decide_tool(state):
    state["tool"] = state.get("intent", "log_interaction")
    return state


def execute_tool(state):
    tool = state["tool"]
    data = state["extracted_data"]
    patch = state.get("extracted_patch") or {}
    memory = state.get("memory") or _memory()

    if tool == "search_hcp":
        search_data = patch or data
        if not search_data.get("Doctor Name") and not search_data.get("hcp_id"):
            hcp_id = _find_hcp_id(search_data, memory)
            search_data = {**search_data, "hcp_id": hcp_id}
        result = search_hcp(search_data)

    elif tool == "interaction_history":
        hcp_id = _find_hcp_id(patch or data, memory)
        result = get_history({"hcp_id": hcp_id}) if hcp_id else {"status": "not_found", "history": []}

    elif tool == "edit_interaction":
        interaction_id = data.get("interaction_id") or _latest_interaction_id(memory)
        hcp_result = _update_active_hcp(patch, memory)
        if interaction_id:
            interaction_result = update_interaction({**patch, "interaction_id": interaction_id})
            result = interaction_result if interaction_result.get("status") == "success" else (hcp_result or interaction_result)
        else:
            result = hcp_result or {"status": "success"}

    elif tool == "follow_up_planner":
        operation = (patch.get("Follow-up Operation") or data.get("Follow-up Operation") or "").lower()
        if operation == "list":
            follow_up_hcp_id = patch.get("hcp_id") or (_find_hcp_id(patch, memory) if patch.get("Doctor Name") else None)
            follow_up_interaction_id = patch.get("interaction_id") or data.get("interaction_id")
        else:
            follow_up_hcp_id = patch.get("hcp_id") or data.get("hcp_id") or memory.get("last_hcp_id")
            follow_up_interaction_id = patch.get("interaction_id") or data.get("interaction_id") or _latest_interaction_id(memory)

        follow_up_data = {
            **data,
            **patch,
            "interaction_id": follow_up_interaction_id,
            "hcp_id": follow_up_hcp_id,
        }
        result = follow_up_planner(follow_up_data)
        follow_up = result.get("follow_up") if isinstance(result, dict) else None
        if follow_up and result.get("operation") == "update":
            updates = {
                "Follow-up Date": follow_up.get("follow_up_date"),
                "Next Action": follow_up.get("next_action"),
                "Priority": follow_up.get("priority"),
                "Status": follow_up.get("status"),
            }
            for key, value in updates.items():
                if value:
                    memory["active_interaction"][key] = value
                    state["extracted_data"][key] = value

    else:
        hcp_id = _ensure_hcp(data, memory)
        result = create_interaction({**data, "hcp_id": hcp_id})
        if isinstance(result, dict) and result.get("interaction_id"):
            memory["last_interaction_id"] = result["interaction_id"]

    state["result"] = result
    state["memory"] = memory
    return state
