from fastapi import APIRouter
from app.auth import create_token

router = APIRouter()

@router.post("/login")
def login():
    # Demo login — no DB yet
    token = create_token("user123")
    return {"token": token}
