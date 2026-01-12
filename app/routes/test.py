from fastapi import APIRouter

router = APIRouter()

@router.get("/protected")
def protected():
    return {"message": "You accessed a protected API"}
