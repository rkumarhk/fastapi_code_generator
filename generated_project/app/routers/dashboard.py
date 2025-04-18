from fastapi import APIRouter
router = APIRouter()

@router.get('/tiles')
def get_tiles():
    return {'tiles': [...]}