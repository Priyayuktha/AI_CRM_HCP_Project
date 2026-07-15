CHECK = "\u2705"


def _updated_field_name(extracted: dict) -> str:
    for key in (
        "Doctor Name",
        "Sentiment",
        "Hospital",
        "Interaction Date",
        "Interaction Time",
        "Materials Shared",
        "Samples Distributed",
        "Summary",
        "Follow-up Date",
        "Next Action",
    ):
        if extracted.get(key):
            return key.lower()
    return "interaction"


def _fallback_reply(tool: str, result: dict, missing_fields: list, extracted: dict) -> str:
    if tool == "search_hcp":
        return "Doctor profile found." if result.get("status") == "success" else "No matching doctor profile found."

    if tool == "interaction_history":
        return "Interaction history loaded." if result.get("history") else "No interaction history found."

    if tool == "follow_up_planner":
        if result.get("operation") == "list":
            return "Upcoming follow-ups loaded." if result.get("follow_ups") else "No upcoming follow-ups found."
        return f"{CHECK} Follow-up updated successfully."

    if tool == "edit_interaction":
        if extracted.get("Doctor Name"):
            return f"{CHECK} Doctor information updated successfully."
        return f"{CHECK} Interaction updated successfully."

    if result.get("status") == "success":
        return f"{CHECK} Interaction logged successfully. The CRM form has been updated."

    return f"{CHECK} CRM form updated successfully."


def _friendly_result(result: dict) -> dict:
    if not isinstance(result, dict):
        return {
            "status": "not_found",
            "message": "I could not find matching CRM records for that request.",
        }

    friendly = dict(result)
    if friendly.get("status") == "error":
        friendly["status"] = "not_found"
        friendly["message"] = "I could not find matching CRM records for that request."
    return friendly


def response_node(state):
    result = _friendly_result(state.get("result", {}))
    extracted = state.get("extracted_data", {})
    extracted_patch = state.get("extracted_patch", {})
    tool = state.get("tool", "log_interaction")
    missing_fields = state.get("missing_fields", [])
    assistant_reply = _fallback_reply(tool, result, [], extracted_patch or extracted)

    state["memory"]["messages"].append({"role": "assistant", "content": assistant_reply})

    state["response"] = {
        "success": result.get("status") != "error",
        "tool": tool,
        "tool_used": tool,
        "intent": state.get("intent", tool),
        "extracted_data": extracted,
        "missing_fields": [],
        "result": result,
        "database_result": result,
        "message": assistant_reply,
    }

    return state
