from pydantic import BaseModel

class CreateCampaign(BaseModel):
    name: str

class Campaign(BaseModel):
    id: int
    name: str