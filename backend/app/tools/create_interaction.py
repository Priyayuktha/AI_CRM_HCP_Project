from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta

from app.database import SessionLocal
from app.models.interaction import Interaction


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
    if not value:
        return None
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


def _first_value(data: dict, *keys):
    for key in keys:
        value = data.get(key)
        if value not in ("", None, [], {}):
            return value
    return None


def create_interaction(data: dict):
    db: Session = SessionLocal()

    try:
        interaction = Interaction(
            hcp_id=data.get("hcp_id"),
            interaction_type=data.get("Interaction Type"),
            interaction_date=_parse_date(data.get("Interaction Date")),
            interaction_time=data.get("Interaction Time"),
            attendees=data.get("Attendees"),
            topics_discussed=data.get("Topics Discussed"),
            sentiment=data.get("Sentiment"),
            materials_shared=data.get("Materials Shared"),
            samples_distributed=data.get("Samples Distributed"),
            outcome=data.get("Outcome"),
            summary=data.get("Summary"),
            follow_up_date=_parse_date(_first_value(data, "Follow-up Date", "Follow Up Date", "follow_up_date")),
            next_action=_first_value(data, "Next Action", "next_action", "Follow-up", "Follow Up"),
            follow_up_priority=_first_value(data, "Priority", "Follow-up Priority", "follow_up_priority"),
            follow_up_status=_first_value(data, "Status", "Follow-up Status", "follow_up_status"),
        )

        db.add(interaction)
        db.commit()
        db.refresh(interaction)

        return {
            "status": "success",
            "interaction_id": interaction.id
        }

    finally:
        db.close()
