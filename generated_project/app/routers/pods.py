from fastapi import APIRouter
router = APIRouter()

@router.post('/assign')
def assign_employee_to_pod():
    ...

@router.get('/members')
def get_pod_members():
    ...

@router.post('/recommend')
def recommend_employee_for_pod():
    ...