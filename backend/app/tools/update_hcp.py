from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.hcp import HCP


FIELD_MAP = {
    "Doctor Name": "name",
    "Hospital": "hospital",
    "City": "city",
    "Specialization": "specialization",
    "Email": "email",
    "Phone": "phone",
}


def update_hcp(data: dict):
    db: Session = SessionLocal()

    try:
        hcp = (
            db.query(HCP)
            .filter(HCP.id == data.get("hcp_id"))
            .first()
        )

        if not hcp:
            return {"status": "not_found"}

        for key, value in data.items():
            model_key = FIELD_MAP.get(key)
            if model_key and value:
                setattr(hcp, model_key, value)

        db.commit()
        db.refresh(hcp)

        return {
            "status": "success",
            "hcp_id": hcp.id,
        }

    finally:
        db.close()
