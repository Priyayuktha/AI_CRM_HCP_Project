from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Date
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy.sql import func

from app.database import Base


class Interaction(Base):

    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)

    hcp_id = Column(Integer, ForeignKey("hcps.id"))

    interaction_type = Column(String(50))

    interaction_date = Column(Date)

    interaction_time = Column(String(30))

    attendees = Column(String(300))

    topics_discussed = Column(String(500))

    sentiment = Column(String(30))

    materials_shared = Column(String(300))

    samples_distributed = Column(String(300))

    outcome = Column(String(1000))

    summary = Column(String(1000))

    follow_up_date = Column(Date)

    next_action = Column(String(500))

    follow_up_priority = Column(String(50))

    follow_up_status = Column(String(50))

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
