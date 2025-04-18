from pydantic import BaseModel

class DashboardTile(BaseModel):
    id: str
    title: str
    content: str