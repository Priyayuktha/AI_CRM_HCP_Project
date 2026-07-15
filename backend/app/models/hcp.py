from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from app.database import Base


class HCP(Base):
    __tablename__ = "hcps"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)

    specialization = Column(String(100))

    hospital = Column(String(150))

    city = Column(String(100))

    email = Column(String(120))

    phone = Column(String(20))

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )