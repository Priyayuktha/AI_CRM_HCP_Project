from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta

from app.database import SessionLocal
from app.models.interaction import Interaction


FIELD_MAP = {
    "Interaction Type": "interaction_type",
    "Interaction Date": "interaction_date",
    "Interaction Time": "interaction_time",
    "Topics Discussed": "topics_discussed",
    "Sentiment": "sentiment",
    "Materials Shared": "materials_shared",
    "Samples Distributed": "samples_distributed",
    "Outcome": "outcome",
    "Summary": "summary",
    "Attendees": "attendees",
    "Follow-up Date": "follow_up_date",
    "Follow Up Date": "follow_up_date",
    "Next Action": "next_action",
    "next_action": "next_action",
    "Follow-up": "next_action",
    "Follow Up": "next_action",
    "Priority": "follow_up_priority",
    "Follow-up Priority": "follow_up_priority",
    "follow_up_priority": "follow_up_priority",
    "Status": "follow_up_status",
    "Follow-up Status": "follow_up_status",
    "follow_up_status": "follow_up_status",
}

WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


def _parse_date(value):
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered == "today":
            return date.today()
        if lowered == "tomorrow":
            return date.fromordinal(date.today().toordinal() + 1)
        for weekday, index in WEEKDAYS.items():
            if weekday in lowered:
                days_ahead = (index - date.today().weekday()) % 7
                if days_ahead == 0 or "next" in lowered:
                    days_ahead += 7
                return date.today() + timedelta(days=days_ahead)
        try:
            return datetime.fromisoformat(value).date()
        except ValueError:
            return None
    return value


def update_interaction(data: dict):
    db: Session = SessionLocal()

    try:
        interaction = (
            db.query(Interaction)
            .filter(Interaction.id == data.get("interaction_id"))
            .first()
        )

        if not interaction:
            return {
                "status": "not_found"
            }

        for key, value in data.items():
            model_key = FIELD_MAP.get(key, key)
            if model_key in ("interaction_date", "follow_up_date"):
                value = _parse_date(value)
            if hasattr(interaction, model_key) and value not in ("", None, [], {}):
                setattr(interaction, model_key, value)

        db.commit()
        db.refresh(interaction)

        return {
            "status": "success",
            "interaction_id": interaction.id
        }

    finally:
        db.close()
