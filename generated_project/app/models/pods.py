from pydantic import BaseModel

class Pod(BaseModel):
    id: str
    name: str
    members: List[str]