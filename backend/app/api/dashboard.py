from fastapi import APIRouter, HTTPException, Body, status
from app.db import con, db
from app.models import ConversionQuery, KPIQuery, TimeQuery

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])

@router.post("/query")
def run_query(query: str = Body(..., embed=True)):
    forbidden_statements = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "ATTACH"]
    if any(stmt in query.upper() for stmt in forbidden_statements):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Modification queries are not allowed.")
    
    try:
        df = con.execute(query).fetch_df()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    return {"data": df.to_dict(orient="records")}

@router.get("/campaigns")
def get_campaigns():
    campaign_list = db.execute("SELECT id, name FROM campaigns").fetchall()
    campaigns = [{"id": row[0], "name": row[1]} for row in campaign_list]
    return {"data": campaigns}

@router.get("/leads")
def get_total_leads_by_campaigns(campaigns: str):
    campaign_names = [name.strip() for name in campaigns.split(",")]
    placeholders = ",".join("?" for _ in campaign_names)
    query = f"""
        SELECT utm_campaign AS campaign, utm_term, COUNT(DISTINCT lead) AS total_leads,
        COUNT(DISTINCT CASE WHEN pipeline_id = 11704932 AND status_id = 142 THEN lead END) AS total_consult_leads,
        COUNT(DISTINCT CASE WHEN pipeline_id = 11959711 AND status_id = 142 THEN lead END) AS total_plan_leads
        FROM leads
        WHERE utm_campaign IN ({placeholders})
        GROUP BY utm_campaign, utm_term
        ORDER BY utm_campaign;
        """
    
    try:
        result = con.execute(query=query, parameters=campaign_names).fetch_df()
        return {"data": result.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
@router.post("/analytics/conversions")
def get_conversion_analytics(request: ConversionQuery):
    request.validate()
    request.date_range.validate()
    start_date, end_date = request.date_range.convert()

    query = f"""
        SELECT {request.group_by} AS group_value,
                COUNT(DISTINCT CASE WHEN created_at BETWEEN ? AND ? THEN lead END) AS total_leads,
                COUNT(DISTINCT CASE WHEN pipeline_id = 11704932 AND status_id = 142 AND closed_at BETWEEN ? AND ? THEN lead END) AS total_consult_leads,
                COUNT(DISTINCT CASE WHEN pipeline_id = 11959711 AND status_id = 142 AND closed_at BETWEEN ? AND ? THEN lead END) AS total_plan_leads,
                COALESCE(ROUND(
                    CAST(
                        COUNT(DISTINCT CASE WHEN pipeline_id = 11704932 AND status_id = 142 AND closed_at BETWEEN ? AND ? THEN lead END) / NULLIF(COUNT(DISTINCT CASE WHEN created_at BETWEEN ? AND ? THEN lead END), 0) * 100 AS DOUBLE
                    ), 2), 0) AS consult_conversion_rate,
                COALESCE(ROUND(
                    CAST(
                        COUNT(DISTINCT CASE WHEN pipeline_id = 11959711 AND status_id = 142 AND closed_at BETWEEN ? AND ? THEN lead END) / NULLIF(COUNT(DISTINCT CASE WHEN created_at BETWEEN ? AND ? THEN lead END), 0) * 100 AS DOUBLE
                    ), 2), 0) AS plan_conversion_rate
                FROM leads
                WHERE utm_campaign IN ({','.join('?' for _ in request.campaigns) if isinstance(request.campaigns, list) else '?'})
                GROUP BY {request.group_by}
                ORDER BY total_leads DESC;
        """
    
    params = [
    start_date, end_date,  # total_leads
    start_date, end_date,  # consult
    start_date, end_date,  # plan
    start_date, end_date,  # consult rate numerador
    start_date, end_date,  # consult rate denominador
    start_date, end_date,  # plan rate numerador
    start_date, end_date,  # plan rate denominador
    ]

    parameters = request.campaigns if isinstance(request.campaigns, list) else [request.campaigns]
    params.extend(parameters)
    try:
        df = con.execute(query=query, parameters=params).fetch_df()
        df = df[
    (df["total_leads"] > 0) |
    (df["total_consult_leads"] > 0) |
    (df["total_plan_leads"] > 0)
].copy()
        return {"data": df.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
@router.post("/analytics/time-to-convert")
def get_time_to_convert_analytics(request: TimeQuery):
    request.validate()
    request.date_range.validate()
    start_date, end_date = request.date_range.convert()

    query = f"""
        WITH first_lead AS (
            SELECT lead, 
                MIN(created_at) AS first_created_at,
                ANY_VALUE(utm_campaign) AS utm_campaign,
                ANY_VALUE(utm_term) AS utm_term,
                ANY_VALUE(utm_source) AS utm_source,
                ANY_VALUE(utm_medium) AS utm_medium
            FROM leads
            GROUP BY lead),
            first_close AS (
                SELECT
                    lead,
                    pipeline_id,
                    MIN(closed_at) AS first_closed_at
                FROM leads
                WHERE status_id = 142
                AND pipeline_id IN (11704932, 11959711)
                AND closed_at IS NOT NULL
                GROUP BY lead, pipeline_id)
            SELECT
                CASE
                    WHEN fc.pipeline_id = 11704932 THEN 'consulta'
                    WHEN fc.pipeline_id = 11959711 THEN 'plano'
                END AS conversion_type,
                fl.utm_campaign,
                fl.utm_source,
                fl.utm_medium,
                fl.utm_term,
                median(DATE_DIFF('day', fl.first_created_at, fc.first_closed_at)) AS median_days,
                avg(DATE_DIFF('day', fl.first_created_at, fc.first_closed_at)) AS average_days,
                COUNT(DISTINCT fc.lead) AS total_conversions
                FROM first_close fc
                JOIN first_lead fl USING (lead)
                WHERE fc.first_closed_at >= fl.first_created_at
                AND fl.utm_campaign IN ({','.join('?' for _ in request.campaigns) if isinstance(request.campaigns, list) else '?'})
                AND fc.first_closed_at BETWEEN ? AND ?
                GROUP BY conversion_type, fl.utm_campaign, fl.utm_source, fl.utm_medium, fl.utm_term
                ORDER BY fl.utm_campaign, conversion_type;"""
    
    params = request.campaigns if isinstance(request.campaigns, list) else [request.campaigns]
    params.extend([start_date, end_date])

    try:
        df = con.execute(query=query, parameters=params).fetch_df()
        return {"data": df.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
@router.get("/analytics/creatives")
def get_creatives_analytics(campaigns: str):
    campaign_names = [name.strip() for name in campaigns.split(",")]
    query = f"""
        SELECT utm_content, COUNT(DISTINCT lead) AS total_leads,
        COALESCE(
            ROUND(
                CAST(
                    COUNT(DISTINCT CASE WHEN pipeline_id = 11704932 AND status_id = 142 THEN lead END) / NULLIF(COUNT(DISTINCT lead), 0) * 100 AS DOUBLE
                ), 2
            ), 0
        ) AS consult_conversion_rate,
        COALESCE(
            ROUND(
                CAST(
                    COUNT(DISTINCT CASE WHEN pipeline_id = 11959711 AND status_id = 142 THEN lead END) / NULLIF(COUNT(DISTINCT lead), 0) * 100 AS DOUBLE
                ), 2
            ), 0
        ) AS plan_conversion_rate
        FROM leads
        WHERE utm_campaign IN ({','.join('?' for _ in campaign_names)})
        GROUP BY utm_campaign, utm_content
        ORDER BY utm_campaign;"""
    
    try:
        df = con.execute(query=query, parameters=campaign_names).fetch_df()
        return {"data": df.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
@router.post("/analytics/kpi")
def get_kpi_analytics(request: KPIQuery):
    request.validate()
    start_date, end_date = request.date_range.convert()
    query = f"""
WITH first_lead AS (
  SELECT
    lead,
    MIN(created_at) AS first_created_at,
    ANY_VALUE(utm_campaign) AS utm_campaign
  FROM leads
  GROUP BY lead
),
first_close AS (
  SELECT
    lead,
    MIN(closed_at) AS first_closed_at,
    ANY_VALUE(pipeline_id) AS pipeline_id
  FROM leads
  WHERE status_id = 142
    AND closed_at IS NOT NULL
  GROUP BY lead
)
SELECT
  fl.utm_campaign,
  COUNT(DISTINCT fl.lead) AS total_leads,

  -- conversões por tipo de pipeline
  COUNT(DISTINCT CASE WHEN fc.pipeline_id = 11704932 THEN fc.lead END) AS consult_converted,
  COUNT(DISTINCT CASE WHEN fc.pipeline_id = 11959711 THEN fc.lead END) AS plan_converted,

  -- taxas relativas ao total
  COALESCE(ROUND(
    COUNT(DISTINCT CASE WHEN fc.pipeline_id = 11704932 THEN fc.lead END) * 100.0 /
    NULLIF(COUNT(DISTINCT fl.lead), 0), 2
  ), 0) AS consult_rate,
  COALESCE(ROUND(
    COUNT(DISTINCT CASE WHEN fc.pipeline_id = 11959711 THEN fc.lead END) * 100.0 /
    NULLIF(COUNT(DISTINCT fl.lead), 0), 2
  ), 0) AS plan_rate,

  -- tempo médio para conversão (geral)
  COALESCE(ROUND(
    AVG(DATE_DIFF('day', fl.first_created_at, fc.first_closed_at)), 2
  ), 0) AS avg_time_to_convert

FROM first_lead fl
LEFT JOIN first_close fc USING (lead)
WHERE fl.first_created_at BETWEEN ? AND ?
  AND fl.utm_campaign IN (
    {','.join('?' for _ in request.campaigns) if isinstance(request.campaigns, list) else '?'}
  )
GROUP BY fl.utm_campaign
ORDER BY total_leads DESC;
"""
    data = request.campaigns if isinstance(request.campaigns, list) else [request.campaigns]
    params = [start_date, end_date]
    params.extend(data)

    try:
        df = con.execute(query=query, parameters=params).fetch_df()
        return {"data": df.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))