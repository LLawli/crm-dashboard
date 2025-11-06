from app.models import LeadRequest
def create_treated_lead(lead_data: dict):
    campos_fixos = {
        "utm_source", "utm_medium", "utm_campaign", "utm_content",
        "utm_term", "utm_id", "fbclid", "gclid", "code", "nome", "whatsapp"
    }

    perguntas = {key: value for key, value in lead_data.items() if key not in campos_fixos and not key.startswith(("tracking.", "score", "responses", "l8gge1", "submit")) and isinstance(value, str)}

    cleaned_data = {
        **{key: lead_data.get(key, None) for key in campos_fixos if key not in ["nome", "name"]},
        "name": lead_data.get("nome", None) or lead_data.get("name", None),
        "responses": perguntas
    }
    return LeadRequest(**cleaned_data)