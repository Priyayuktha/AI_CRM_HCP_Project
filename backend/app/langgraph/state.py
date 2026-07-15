from typing import TypedDict


class AgentState(TypedDict):
    user_input: str
    intent: str
    agent_output: dict
    extracted_patch: dict
    extracted_data: dict
    missing_fields: list
    assistant_reply: str
    tool: str
    result: dict
    memory: dict
    response: dict
