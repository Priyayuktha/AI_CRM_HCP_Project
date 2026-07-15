from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.hcp import HCPCreate, HCPResponse
from app.services.hcp_service import create_hcp, get_all_hcps

router = APIRouter(prefix="/hcp", tags=["HCP"])


@router.post("/", response_model=HCPResponse)
def add_hcp(hcp: HCPCreate, db: Session = Depends(get_db)):
    return create_hcp(db, hcp)


@router.get("/", response_model=list[HCPResponse])
def list_hcps(db: Session = Depends(get_db)):
    return get_all_hcps(db)