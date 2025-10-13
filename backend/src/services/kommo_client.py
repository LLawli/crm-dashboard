import httpx
import time
from collections import deque
from src.config import KOMMO_DOMAIN, KOMMO_KEY
from src.utils import period_handler
from src.db import get_connection


def fetch_leads(
    campaigns: list[int] | None = None,
    period: str = "day",
    date_from: str | None = None,
    date_to: str | None = None,
    pipeline_id: int | None = None,
    status_id: int | None = None
):
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT name FROM campaigns"
    if campaigns:
        placeholders = ",".join("?" for _ in campaigns)
        query += f" WHERE id IN ({placeholders})"
        cursor.execute(query, campaigns)
    else:
        cursor.execute(query)

    rows = cursor.fetchall()
    campaigns_name = [row[0] for row in rows]
    conn.close()

    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {KOMMO_KEY}"
    }

    base_url = f"https://{KOMMO_DOMAIN}.kommo.com/api/v4/leads"
    leads = []

    request_timestamps = deque(maxlen=7)

    def rate_limit():
        now = time.time()
        if len(request_timestamps) == 7:
            elapsed = now - request_timestamps[0]
            if elapsed < 1.0:
                time.sleep(1.0 - elapsed)
        request_timestamps.append(time.time())

    def get_utm_campaign(lead):
        for field in lead.get("custom_fields_values", []):
            if field.get("field_code") == "UTM_CAMPAIGN":
                return field["values"][0]["value"] if field.get("values") else None
        return None


    def _fetch_period(start_ts: int, end_ts: int):
        for campaign in campaigns_name:
            page = 1
            while True:
                rate_limit()

                params = {
                    "with": "contacts",
                    "limit": 250,
                    "page": page,
                    "query": campaign,
                    "filter[created_at][from]": int(start_ts),
                    "filter[created_at][to]": int(end_ts)
                }

                if pipeline_id:
                    params["filter[statuses][0][pipeline_id]"] = pipeline_id
                if status_id:
                    params["filter[statuses][0][status_id]"] = status_id

                with httpx.Client(headers=headers, timeout=30.0) as client:
                    resp = client.get(base_url, params=params)

                if resp.status_code != 200:
                    raise RuntimeError(
                        f"Erro na requisição para utm_campaign '{campaign}' (status {resp.status_code}): {resp.text}"
                    )

                data = resp.json()
                items = data.get("_embedded", {}).get("leads", [])
                if not items:
                    break

                print(items)

                items = [lead for lead in items if get_utm_campaign(lead) == campaign]

                leads.extend(items)

                if "_links" not in data or "next" not in data["_links"]:
                    break

                page += 1

    init, end = period_handler(period, date_from, date_to)

    _fetch_period(init.timestamp(), end.timestamp())


    return leads