from fastapi import APIRouter, Request, HTTPException
from app.services.treatment_lead import create_treated_lead
import os
import tempfile
import httpx
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/api/v1/lead")

@router.post("/form")
async def submit_lead_form(lead_data: Request):
    data = await lead_data.json()
    treated_lead = create_treated_lead(data)
    
    temp = tempfile.NamedTemporaryFile("w+", delete=False, suffix=".txt", encoding="utf-8")

    try:
        for key, value in treated_lead.responses.items():
            temp.write(f"{key}: {value}\n")
        temp.flush()
        temp_path = temp.name
        temp_size = os.path.getsize(temp_path)

        KOMMO_DRIVE_URL = "https://drive-c.kommo.com/v1.0/sessions"
        KOMMO_TOKEN = os.getenv("KOMMO_KEY")

        payload = {
            "file_name": f"respostas-{treated_lead.name or 'lead'}.txt",
            "file_size": temp_size,
            "content_type": "application/octet-stream",
            "with_preview": False,
        }

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {KOMMO_TOKEN}"
        }

        async with httpx.AsyncClient(headers=headers) as client:
            response = await client.post(KOMMO_DRIVE_URL, json=payload)
            response.raise_for_status()
            upload_url = response.json().get("upload_url")
            max_part_size = response.json().get("max_part_size", 131072)

            archive_uuid = None
            with open(temp_path, "rb") as file:
                next_url = upload_url
                while True:
                    chunk = file.read(max_part_size)
                    if not chunk:
                        break
                    chunk_response = await client.post(next_url, data=chunk, headers={"Content-Type": "application/octet-stream", "Accept": "application/json"})
                    chunk_response.raise_for_status()
                    resp_json = chunk_response.json()
                    if "next_url" in resp_json:
                        next_url = resp_json["next_url"]
                    else:
                        archive_uuid = resp_json.get("uuid")
                        break
            
            os.remove(temp_path)
    except:
        raise HTTPException(status_code=500, detail="Error uploading file to Kommo Drive")

    payload_lead = [
            {
                "name": treated_lead.name,
                "pipeline_id": 11704932,
                "status_id": 90440911,
                "custom_fields_values": [
                    {
                        "field_id": 746041,
                        "values": [{"value": treated_lead.utm_content}]
                    },
                    {
                        "field_id": 746043,
                        "values": [{"value": treated_lead.utm_medium}]
                    },
                    {
                        "field_id": 746045,
                        "values": [{"value": treated_lead.utm_campaign}]
                    },
                    {
                        "field_id": 746047,
                        "values": [{"value": treated_lead.utm_source}]
                    },
                    {
                        "field_id": 746049,
                        "values": [{"value": treated_lead.utm_term}]
                    },
                    {
                        "field_id": 746051,
                        "values": [{"value": treated_lead.utm_id}]
                    },
                    {
                        "field_id": 746057,
                        "values": [{"value": treated_lead.gclid}]
                    },
                    {
                        "field_id": 746059,
                        "values": [{"value": treated_lead.fbclid}]
                    },
                    {
                        "field_id": 1485285,
                        "values": [{"value": {"file_uuid": archive_uuid}}]
                    }
                ],
                "_embedded": {
                    "contacts": [
                        {
                            "name": treated_lead.name,
                            "custom_fields_values": [
                                {
                                    "field_code": "PHONE",
                                    "values": [{"value": treated_lead.whatsapp}]
                                }
                            ]
                        }
                    ]
                }
            }
        ]
    
    KOMMO_LEADS_URL = f"https://{os.getenv("KOMMO_DOMAIN")}.kommo.com/api/v4/leads/complex"

    async with httpx.AsyncClient(headers=headers) as client:
        lead_response = await client.post(KOMMO_LEADS_URL, json=payload_lead)
        lead_response.raise_for_status()
        return {"status": "Lead submitted successfully", "data": lead_response.json()}