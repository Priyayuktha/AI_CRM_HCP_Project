from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import SessionLocal
from app.models.hcp import HCP
from app.models.interaction import Interaction


def get_history(data):

    db: Session = SessionLocal()

    try:

        # If AI returned a list, use the first item
        if isinstance(data, list):
            data = data[0] if data else {}

        if not isinstance(data, dict):
            return {
                "status": "not_found",
                "message": "No interaction history found.",
                "history": [],
            }

        hcp_id = data.get("hcp_id")

        if not hcp_id:
            return {
                "status": "not_found",
                "message": "No interaction history found.",
                "history": [],
            }

        interactions = (
            db.query(Interaction)
            .filter(Interaction.hcp_id == hcp_id)
            .order_by(desc(Interaction.interaction_date), desc(Interaction.created_at))
            .all()
        )

        hcp = db.query(HCP).filter(HCP.id == hcp_id).first()

        history = []

        for item in interactions:

            history.append({
                "id": item.id,
                "doctor_name": hcp.name if hcp else "",
                "hospital": hcp.hospital if hcp else "",
                "interaction_type": item.interaction_type,
                "interaction_date": str(item.interaction_date) if item.interaction_date else "",
                "interaction_time": item.interaction_time,
                "topics_discussed": item.topics_discussed,
                "materials_shared": item.materials_shared,
                "samples_distributed": item.samples_distributed,
                "outcome": item.outcome,
                "summary": item.summary,
                "sentiment": item.sentiment,
                "follow_up_date": str(item.follow_up_date) if item.follow_up_date else "",
                "next_action": item.next_action,
                "priority": item.follow_up_priority,
                "status": item.follow_up_status,
            })

        return {
            "status": "success",
            "message": "Interaction history loaded." if history else "No interaction history found.",
            "history": history
        }

    finally:
        db.close()
