from fastapi import APIRouter
router = APIRouter()

@router.post('/apply')
def apply_for_leave():
    ...

@router.get('/status')
def get_leave_status():
    ...

@router.patch('/approve/{id}')
def approve_leave():
    ...