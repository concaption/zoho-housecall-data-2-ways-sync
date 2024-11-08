import logging
from fastapi import APIRouter

from config import settings
from utils.zoho.authenticate import generate_tokens



router = APIRouter(prefix="/zoho", tags=["zoho"])

@router.post("/authenticate")
async def authenticate(code: str):
    logging.info("Received code %s", code)
    access_token, refresh_token = generate_tokens(
        settings.ZOHO_CLIENT_ID,
        settings.ZOHO_CLIENT_SECRET,
        code,
        "authorization_code",
        settings.ZOHO_REDIRECT_URI,
    )
    with open("access_token.txt", "w", encoding="utf-8") as f:
        f.write(access_token)
    with open("refresh_token.txt", "w", encoding="utf-8") as f:
        f.write(refresh_token)
    return {"access_token": access_token, "refresh_token": refresh_token}


@router.get("/refresh")
async def refresh():
    with open("refresh_token.txt", "r", encoding="utf-8") as f:
        refresh_token = f.read()
    access_token, _ = generate_tokens(
        settings.ZOHO_CLIENT_ID,
        settings.ZOHO_CLIENT_SECRET,
        refresh_token,
        "refresh_token",
    )
    with open("access_token.txt", "w", encoding="utf-8") as f:
        f.write(access_token)
    return {"access_token": access_token, "refresh_token": refresh_token}
