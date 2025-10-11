from src.db import get_connection
from fastapi import APIRouter, status, HTTPException, Query
from src.services. kommo_client import fetch_leads
from src.utils import process_leads, dashboard_format, dashboard_format_flat

router = APIRouter(prefix="/api/v1")

@router.get("/leads", status_code=status.HTTP_200_OK)
def get_leads(
    campaigns: list[int] | None = Query(None, description="Campaign IDs"),
    period: str = Query("day", description="Period: day, yesterday, week, month, custom"),
    date_from: str | None = Query(None, description="Initial date (dd/mm/YYYY)"),
    date_to: str | None = Query(None, description="Final date (dd/mm/YYYY)"),
    pipeline_id: int | None = Query(None, description="Pipeline ID"),
    status_id: int | None = Query(None, description="Status ID")
):
    leads = fetch_leads(
        campaigns=campaigns,
        period=period,
        date_from=date_from,
        date_to=date_to,
        pipeline_id=pipeline_id,
        status_id=status_id,
    )

    leads = process_leads(leads)
    return {"count": len(leads), "data": leads}

@router.get("/leads/dashboard", status_code=status.HTTP_200_OK)
def get_dashboard(
    campaigns: list[int] | None = Query(None, description="Campaign IDs"),
    period: str = Query("all", description="Period: day, yesterday, week, month, custom, all (slow)"),
    date_from: str | None = Query(None, description="Initial date (dd/mm/YYYY)"),
    date_to: str | None = Query(None, description="Final date (dd/mm/YYYY)"),
    pipeline_id: int | None = Query(None, description="Pipeline ID"),
    status_id: int | None = Query(None, description="Status ID"),
    flat: bool = Query(False, description="Flat data for dashboard (default=False)")
):
    leads = fetch_leads(
        campaigns=campaigns,
        period=period,
        date_from=date_from,
        date_to=date_to,
        pipeline_id=pipeline_id,
        status_id=status_id,
    )

    leads = process_leads(leads)
    num = len(leads)
    if flat:
        leads = dashboard_format_flat(leads)
    else:
        leads = dashboard_format(leads)
    return {"count": num, "data": leads}
