from pydantic import BaseModel
from typing import Optional
from datetime import date


class InteractionCreate(BaseModel):
    hcp_id: Optional[int] = None
    interaction_type: Optional[str] = None
    interaction_date: Optional[date] = None
    interaction_time: Optional[str] = None
    attendees: Optional[str] = None
    topics_discussed: Optional[str] = None
    sentiment: Optional[str] = None
    materials_shared: Optional[str] = None
    samples_distributed: Optional[str] = None
    outcome: Optional[str] = None
    summary: Optional[str] = None
    follow_up_date: Optional[date] = None
    next_action: Optional[str] = None
    follow_up_priority: Optional[str] = None
    follow_up_status: Optional[str] = None


class InteractionResponse(InteractionCreate):
    id: int

    class Config:
        from_attributes = True
