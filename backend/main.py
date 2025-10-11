from fastapi import FastAPI
from src.routes import campaigns, leads
from src.db import init_database

app = FastAPI()

init_database()


@app.get("/ping")
def ping():
    return {"data": "pong"}

app.include_router(campaigns.router)
app.include_router(leads.router)