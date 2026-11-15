from fastapi import FastAPI

from app import models
from app.database import Base, engine
from app.routers import games

app = FastAPI(title="Game Backlog Tracker API", version="0.1.0")

Base.metadata.create_all(bind=engine)

app.include_router(games.router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
