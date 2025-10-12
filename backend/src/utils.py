from datetime import datetime, timedelta
from collections import defaultdict
from src.config import CONVERT_PIPE, PLAN_PIPE, FOLLOW_PIPE, WON_STATUS

def period_handler(period: str, date_from: str | None = None, date_to: str | None = None) -> tuple[datetime, datetime]:
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    try:
        if period == "yesterday":
            end = today - timedelta(microseconds=1)
            init = end.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
            return init, end

        elif period == "week":
            init = today - timedelta(days=(((today.weekday() + 1) % 7))+7)
            end = today.replace(hour=23, minute=59, second=59, microsecond=999999)
            return init, end

        elif period == "month":
            init_at = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_at = init_at - timedelta(microseconds=1)
            init = end_at.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end = today
            return init, end
        
        elif period == "all":
            end = today.replace(hour=23, minute=59, second=59, microsecond=999999)
            init = datetime.fromtimestamp(0)
            return init, end

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
            return end, prev_end

    except Exception:
        pass  


    init = today - timedelta(days=1)
    end = today.replace(hour=23, minute=59, second=59, microsecond=999999)
    return init, end

def process_leads(leads_list: list):
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
        converted = any(l["pipeline_id"] == int(CONVERT_PIPE) and l["status_id"] == int(WON_STATUS) for l in group_leads)
        plan = any(l["pipeline_id"] == int(PLAN_PIPE) and l["status_id"] == int(WON_STATUS) for l in group_leads)
        follow_up = any(l["pipeline_id"] == int(FOLLOW_PIPE) for l in group_leads)

        latest_lead = max(group_leads, key=lambda l: l["created_at"])

        oldest_created_at = min(l["created_at"] for l in group_leads)
        latest_lead["created_at"] = oldest_created_at

        latest_lead["converted"] = converted
        latest_lead["plan"] = plan
        latest_lead["follow_up"] = follow_up

        result.append(latest_lead)

    return result


def dashboard_format(leads: list):
    result_dict = {}

    for lead in leads:
        date_str = datetime.fromtimestamp(lead["created_at"]).strftime("%d/%m/%Y")

        fields = {f.get("field_code"): f["values"][0]["value"] for f in lead.get("custom_fields_values", []) if f.get("field_code")}
        campaign = fields.get("UTM_CAMPAIGN", "Unknown")
        term = fields.get("UTM_TERM", "Unknown")
        content = fields.get("UTM_CONTENT", "Unknown")

        if date_str not in result_dict:
            result_dict[date_str] = {}
        if campaign not in result_dict[date_str]:
            result_dict[date_str][campaign] = {}
        if term not in result_dict[date_str][campaign]:
            result_dict[date_str][campaign][term] = {}
        if content not in result_dict[date_str][campaign][term]:
            result_dict[date_str][campaign][term][content] = {"leads": 0, "follow_up": 0, "converted_leads": 0, "plan_leads": 0}

        counts = result_dict[date_str][campaign][term][content]
        counts["leads"] += 1
        if lead.get("converted"):
            counts["converted_leads"] += 1
        if lead.get("plan"):
            counts["plan_leads"] += 1
        if lead.get("follow_up"):
            counts["follow_up"] += 1

    final_result = []
    for date, campaigns in result_dict.items():
        campaign_list = []
        for campaign_name, terms in campaigns.items():
            term_list = []
            for term_name, contents in terms.items():
                content_list = [{"name": content_name, **counts} for content_name, counts in contents.items()]
                term_list.append({"name": term_name, "contents": content_list})
            campaign_list.append({"name": campaign_name, "terms": term_list})
        final_result.append({"date": date, "campaigns": campaign_list})

    return final_result

def dashboard_format_flat(leads: list):
    flat_dict = {}

    for lead in leads:
        date_str = datetime.fromtimestamp(lead["created_at"]).strftime("%d/%m/%Y")

        fields = {f.get("field_code"): f["values"][0]["value"] for f in lead.get("custom_fields_values", []) if f.get("field_code")}
        campaign = fields.get("UTM_CAMPAIGN", "Unknown")
        term = fields.get("UTM_TERM", "Unknown")
        content = fields.get("UTM_CONTENT", "Unknown")

        key = (date_str, campaign, term, content)

        if key not in flat_dict:
            flat_dict[key] = {"leads": 0, "follow_up": 0, "converted_leads": 0, "plan_leads": 0}

        flat_dict[key]["leads"] += 1
        if lead.get("converted"):
            flat_dict[key]["converted_leads"] += 1
        if lead.get("plan"):
            flat_dict[key]["plan_leads"] += 1
        if lead.get("follow_up"):
            flat_dict[key]["follow_up"] += 1

    flat_list = [
        {
            "date": date,
            "campaign": campaign,
            "term": term,
            "content": content,
            **counts
        }
        for (date, campaign, term, content), counts in flat_dict.items()
    ]

    return flat_list
