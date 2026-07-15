from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.hcp import HCP


def create_hcp(data: dict):
    db: Session = SessionLocal()

    try:
        hcp = HCP(
            name=data.get("Doctor Name", ""),
            specialization=data.get("Specialization", ""),
            hospital=data.get("Hospital", ""),
            city=data.get("City", ""),
            email=data.get("Email", ""),
            phone=data.get("Phone", ""),
        )

        db.add(hcp)
        db.commit()
        db.refresh(hcp)

        return {
            "status": "success",
            "hcp_id": hcp.id,
            "message": "HCP created successfully"
        }

    finally:
        db.close()