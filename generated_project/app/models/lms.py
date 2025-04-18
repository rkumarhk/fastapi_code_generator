from pydantic import BaseModel

class LeaveRequest(BaseModel):
    id: str
    employee_id: str
    start_date: str
    end_date: str
    reason: str