from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import SessionLocal
from app.models.hcp import HCP
from app.models.interaction import Interaction


def _serialize_hcp(db: Session, hcp: HCP):
    last_interaction = (
        db.query(Interaction)
        .filter(Interaction.hcp_id == hcp.id)
        .order_by(desc(Interaction.interaction_date), desc(Interaction.created_at))
        .first()
    )

    return {
        "id": hcp.id,
        "name": hcp.name or "",
        "hospital": hcp.hospital or "",
        "city": hcp.city or "",
        "specialization": hcp.specialization or "",
        "last_interaction_date": str(last_interaction.interaction_date) if last_interaction and last_interaction.interaction_date else "",
    }


def search_hcp(data: dict):

    db: Session = SessionLocal()

    try:
        hcp_id = data.get("hcp_id")
        doctor_name = data.get("Doctor Name", "").strip()

        if hcp_id:
            hcps = db.query(HCP).filter(HCP.id == hcp_id).all()
        elif doctor_name:
            hcps = (
                db.query(HCP)
                .filter(HCP.name.ilike(f"%{doctor_name}%"))
                .order_by(HCP.name.asc())
                .all()
            )
        else:
            return {
                "status": "not_found",
                "message": "No matching doctor profile found.",
                "hcps": [],
            }

        if not hcps:
            return {
                "status": "not_found",
                "message": "No matching doctor profile found.",
                "hcps": [],
            }

        serialized = [_serialize_hcp(db, hcp) for hcp in hcps]

        return {
            "status": "success",
            "message": "Doctor profile found.",
            "hcp": serialized[0],
            "hcps": serialized,
        }

    finally:
        db.close()
