from pydantic import BaseModel
from typing import Optional


class HCPCreate(BaseModel):
    name: str
    specialization: Optional[str] = None
    hospital: Optional[str] = None
    city: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class HCPResponse(HCPCreate):
    id: int

    class Config:
        from_attributes = True