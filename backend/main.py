from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routes import campaigns, leads
from src.db import init_database

app = FastAPI()

init_database()

origins = [
    "http://localhost:3000",  
    "http://localhost:3001"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/ping")
def ping():
    return {"data": "pong"}

app.include_router(campaigns.router)
app.include_router(leads.router)