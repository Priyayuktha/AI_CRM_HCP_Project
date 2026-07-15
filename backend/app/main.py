from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect

from app.database import Base, engine

from app.models.hcp import HCP
from app.models.interaction import Interaction

from app.routers import hcp, interaction, chat

Base.metadata.create_all(bind=engine)


def ensure_interaction_demo_columns():
    inspector = inspect(engine)
    existing = {column["name"] for column in inspector.get_columns("interactions")}
    required = {
        "interaction_time": "VARCHAR(30)",
        "samples_distributed": "VARCHAR(300)",
        "outcome": "VARCHAR(1000)",
        "follow_up_date": "DATE",
        "next_action": "VARCHAR(500)",
        "follow_up_priority": "VARCHAR(50)",
        "follow_up_status": "VARCHAR(50)",
    }

    with engine.begin() as connection:
        for column, column_type in required.items():
            if column not in existing:
                connection.exec_driver_sql(
                    f"ALTER TABLE interactions ADD COLUMN {column} {column_type}"
                )


ensure_interaction_demo_columns()

app = FastAPI(title="AI CRM API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "AI CRM Backend is Running Successfully!"
    }


app.include_router(hcp.router)
app.include_router(interaction.router)
app.include_router(chat.router)
