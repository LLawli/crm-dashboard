from datetime import datetime, timedelta
from collections import defaultdict
from src.config import CONVERT_PIPE, PLAN_PIPE, WON_STATUS

def period_handler(period: str, date_from: str | None = None, date_to: str | None = None) -> tuple[datetime, datetime, datetime, datetime]:
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    try:
        if period == "yesterday":
            init = today - timedelta(days=1)
            end = init.replace(hour=23, minute=59, second=59, microsecond=999999)
            prev_init = init - timedelta(days=1)
            prev_end = end - timedelta(days=1)
            return init, end, prev_init, prev_end

        elif period == "week":
            init = today - timedelta(days=((today.weekday() + 1) % 7))
            init = init.replace(hour=0, minute=0, second=0, microsecond=0)
            end = datetime.now()
            prev_init = init - timedelta(days=7)
            prev_end = init - timedelta(microseconds=1)
            return init, end, prev_init, prev_end

        elif period == "month":
            init = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end = today
            prev_end = init - timedelta(microseconds=1)
            prev_init = prev_end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            return init, end, prev_init, prev_end

        elif period == "custom" and date_from and date_to:
            try:
                date_from_datetime = datetime.strptime(date_from, "%d/%m/%Y")
                date_to_datetime = datetime.strptime(date_to, "%d/%m/%Y")
            except Exception:
                raise  

            if date_from_datetime > date_to_datetime:
                date_to_datetime = date_from_datetime + timedelta(days=1) 

            init = date_from_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
            end = date_to_datetime.replace(hour=23, minute=59, second=59, microsecond=999999)
            delta = end - init
            prev_end = init - timedelta(microseconds=1)
            prev_init = prev_end - delta
            return init, end, prev_init, prev_end

    except Exception:
        pass  


    init = today
    end = today.replace(hour=23, minute=59, second=59, microsecond=999999)
    prev_end = init - timedelta(microseconds=1)
    prev_init = init - timedelta(days=1)
    return init, end, prev_init, prev_end

def process_leads(leads_list):
    if not leads_list:
        return []

    def get_fbclid(lead):
        for field in lead.get("custom_fields_values", []):
            if field.get("field_code") == "FBCLID":
                return field["values"][0]["value"]
        return None

    def get_main_contact_id(lead):
        contacts = lead.get("_embedded", {}).get("contacts", [])
        for c in contacts:
            if c.get("is_main"):
                return c.get("id")
        return None

    groups = defaultdict(list)
    for lead in leads_list:
        key = get_fbclid(lead) or get_main_contact_id(lead)
        groups[key].append(lead)

    result = []
    for group_leads in groups.values():
        converted = any(l["pipeline_id"] == CONVERT_PIPE and l["status_id"] == WON_STATUS for l in group_leads)
        plan = any(l["pipeline_id"] == PLAN_PIPE and l["status_id"] == WON_STATUS for l in group_leads)

        latest_lead = max(group_leads, key=lambda l: l["created_at"])
        oldest_created_at = min(l["created_at"] for l in group_leads)
        latest_lead["created_at"] = oldest_created_at

        latest_lead["converted"] = converted
        latest_lead["plan"] = plan

        result.append(latest_lead)

    return result
