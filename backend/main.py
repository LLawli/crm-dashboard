from fastapi import FastAPI
from src.routes import campaigns

app = FastAPI()


@app.get("/ping")
def ping():
    return {"data": "pong"}

app.include_router(campaigns.router)