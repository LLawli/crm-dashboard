from httpx import Client
from dotenv import load_dotenv
import os
from app.db import db, con

load_dotenv()

def extract_utm(lead, campaign):
    utm_params = {
        "utm_source": None,
        "utm_medium": None,
        "utm_campaign": None,
        "utm_content": None,
        "utm_term": None
    }
    if not lead.get("custom_fields_values", None):
        return None
    for field in lead.get("custom_fields_values"):
        if field["field_name"] in utm_params and field["values"]:
            utm_params[field["field_name"].lower()] = field["values"][0]["value"]

    if utm_params["utm_campaign"] != campaign:
        return None

    return utm_params

def ts_to_datetime(ts):
    from datetime import datetime
    if ts is None:
        return None
    return datetime.fromtimestamp(ts)

def sync_data():
    campaigns = db.execute("SELECT name FROM campaigns").fetchall()
    KOMMO_KEY = os.getenv("KOMMO_KEY")
    KOMMO_DOMAIN = os.getenv("KOMMO_DOMAIN")
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {KOMMO_KEY}"
    }
    
    lead_list = []

    with Client(headers=headers) as client:
        for campaign in campaigns:
            campaign_name = campaign[0]
            response = client.get(f"https://{KOMMO_DOMAIN}.kommo.com/api/v4/leads", params={"with": "contacts", "query": campaign_name})
            if response.status_code != 200:
                print(f"Error fetching data for campaign {campaign_name}: {response.status_code}")
                continue
            
            data = response.json()
            lead_list.extend(data["_embedded"]["leads"])

            if data["_links"].get("next"):
                while data["_links"].get("next"):
                    next_url = data["_links"]["next"]["href"]
                    response = client.get(next_url)
                    if response.status_code != 200:
                        print(f"Error fetching next page for campaign {campaign_name}: {response.status_code}")
                        break
                    data = response.json()
                    lead_list.extend(data["_embedded"]["leads"])

            con.execute("DELETE FROM LEADS WHERE utm_campaign = ?", [campaign_name])

            for lead in lead_list:
                utm_data = extract_utm(lead, campaign_name)
                if not utm_data:
                    continue

                con.execute("""
                    INSERT INTO leads (id, lead, price, status_id, pipeline_id, closed_at, created_at,
                                        utm_source, utm_medium, utm_campaign, utm_content, utm_term)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
""", parameters=[
    lead["id"],
    lead["_embedded"]["contacts"][0]["id"],
    lead.get("price"),
    lead["status_id"],
    lead["pipeline_id"],
    ts_to_datetime(lead.get("closed_at")),
    ts_to_datetime(lead.get("created_at")),
    utm_data["utm_source"],
    utm_data["utm_medium"],
    utm_data["utm_campaign"],
    utm_data["utm_content"],
    utm_data["utm_term"]
])