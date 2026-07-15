from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.interaction import (
    InteractionCreate,
    InteractionResponse,
)
from app.services.interaction_service import (
    create_interaction,
    get_all_interactions,
)

router = APIRouter(prefix="/interaction", tags=["Interaction"])


@router.post("/", response_model=InteractionResponse)
def add_interaction(
    interaction: InteractionCreate,
    db: Session = Depends(get_db),
):
    return create_interaction(db, interaction)


@router.get("/", response_model=list[InteractionResponse])
def list_interactions(db: Session = Depends(get_db)):
    return get_all_interactions(db)