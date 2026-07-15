from datetime import date, datetime, timedelta

from sqlalchemy import asc
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.hcp import HCP
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
            return date.today() + timedelta(days=1)
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


def _serialize_follow_up(interaction: Interaction, hcp: HCP | None):
    return {
        "id": interaction.id,
        "interaction_id": interaction.id,
        "doctor_name": hcp.name if hcp and hcp.name else "Not Available",
        "hospital": hcp.hospital if hcp and hcp.hospital else "",
        "follow_up_date": str(interaction.follow_up_date) if interaction.follow_up_date else "",
        "priority": interaction.follow_up_priority or "Not Available",
        "status": interaction.follow_up_status or "Not Available",
        "next_action": interaction.next_action or "Not Available",
    }


def _operation(data: dict) -> str:
    value = (
        data.get("Follow-up Operation")
        or data.get("operation")
        or data.get("Action")
        or ""
    )
    return str(value).strip().lower()


def _list_follow_ups(db: Session, data: dict):
    today = date.today()
    query = (
        db.query(Interaction, HCP)
        .outerjoin(HCP, Interaction.hcp_id == HCP.id)
        .filter(Interaction.follow_up_date.isnot(None))
        .filter(Interaction.follow_up_date >= today)
    )

    hcp_id = data.get("hcp_id")
    if hcp_id:
        query = query.filter(Interaction.hcp_id == hcp_id)

    range_start = _parse_date(data.get("Date Range Start") or data.get("date_range_start"))
    if range_start:
        query = query.filter(Interaction.follow_up_date >= max(range_start, today))

    range_end = _parse_date(data.get("Date Range End") or data.get("date_range_end"))
    if range_end:
        query = query.filter(Interaction.follow_up_date <= range_end)

    query = query.order_by(asc(Interaction.follow_up_date), asc(Interaction.created_at))
    rows = query.all()
    follow_ups = [_serialize_follow_up(interaction, hcp) for interaction, hcp in rows]

    return {
        "status": "success",
        "operation": "list",
        "message": "Upcoming follow-ups loaded." if follow_ups else "No upcoming follow-ups found.",
        "follow_ups": follow_ups,
    }


def _update_follow_up(db: Session, data: dict):
    operation = _operation(data)
    interaction_id = data.get("interaction_id")
    interaction = None

    if interaction_id:
        interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()

    if not interaction and data.get("hcp_id"):
        interaction = (
            db.query(Interaction)
            .filter(Interaction.hcp_id == data.get("hcp_id"))
            .order_by(asc(Interaction.follow_up_date), asc(Interaction.created_at))
            .first()
        )

    if not interaction:
        interaction = (
            db.query(Interaction)
            .order_by(asc(Interaction.follow_up_date), asc(Interaction.created_at))
            .first()
        )

    if not interaction:
        return {
            "status": "not_found",
            "operation": "update",
            "message": "No matching follow-up found.",
            "follow_ups": [],
        }

    follow_up_date = _parse_date(data.get("Follow-up Date") or data.get("follow_up_date"))
    if follow_up_date:
        interaction.follow_up_date = follow_up_date

    next_action = data.get("Next Action") or data.get("next_action") or data.get("Follow-up") or data.get("Follow Up")
    if next_action:
        interaction.next_action = next_action

    priority = data.get("Priority") or data.get("Follow-up Priority") or data.get("priority") or data.get("follow_up_priority")
    if priority:
        interaction.follow_up_priority = priority

    status = data.get("Status") or data.get("Follow-up Status") or data.get("follow_up_status") or data.get("status")
    if not status and operation in {"complete", "completed", "mark_complete", "mark completed"}:
        status = "Completed"
    if status:
        interaction.follow_up_status = status

    db.commit()
    db.refresh(interaction)

    hcp = db.query(HCP).filter(HCP.id == interaction.hcp_id).first() if interaction.hcp_id else None
    return {
        "status": "success",
        "operation": "update",
        "message": "Follow-up updated successfully.",
        "interaction_id": interaction.id,
        "follow_up": _serialize_follow_up(interaction, hcp),
        "follow_ups": [_serialize_follow_up(interaction, hcp)],
    }


def follow_up_planner(data: dict):
    db: Session = SessionLocal()

    try:
        operation = _operation(data)
        if operation in {"update", "complete", "completed", "reschedule", "mark_complete", "mark completed"}:
            return _update_follow_up(db, data)

        return _list_follow_ups(db, data)

    finally:
        db.close()
