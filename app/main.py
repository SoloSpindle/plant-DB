from __future__ import annotations

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import init_db
from app.routers import export, logs, plants

app = FastAPI(title="Plant NFC Tracker", version="1.0.0")
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.on_event("startup")
def on_startup() -> None:
    init_db()


app.include_router(plants.router)
app.include_router(logs.router)
app.include_router(export.router)
