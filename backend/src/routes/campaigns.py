from src.db import get_connection
from fastapi import APIRouter, status, HTTPException, Query
from src.schemas import CreateCampaign, Campaign
from typing import Optional
import sqlite3

router = APIRouter(prefix="/api/v1")

@router.post("/campaigns", status_code=status.HTTP_201_CREATED)
def add_campaign(campaign: CreateCampaign):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
CREATE TABLE IF NOT EXISTS campaigns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
)INDEX
""")
    
    cursor.execute("SELECT id FROM campaigns WHERE name = ?", (campaign.name,))
    resultado = cursor.fetchone()

    if resultado:
        conn.close()
        raise HTTPException(400, f"Campaign '{campaign.name}' already exists with ID {resultado[0]}")
    
    cursor.execute("INSERT INTO campaigns (name) VALUES (?)", (campaign.name,))
    conn.commit()
    campaign_id = cursor.lastrowid

    conn.close()

    return {"id": campaign_id, "name": campaign.name}

@router.get("/campaigns", status_code=status.HTTP_200_OK, response_model=list[Campaign])
def get_campaigns(search: str | None = Query(None, description="Search by name")):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = "SELECT id, name FROM campaigns"
    params = []

    if search:
        query += " WHERE name LIKE ?"
        params.append(f"%{search}%")

    cursor.execute(query, params)
    rows = cursor.fetchall()

    campaigns = [Campaign(**dict(row)) for row in rows]
    conn.close()
    return campaigns