
import logging
import httpx
from config import settings

BASE_URL = "https://accounts.zoho.com"

def generate_tokens( client_id, client_secret, code, grant_type, redirect_uri=None):
    url = BASE_URL + "/oauth/v2/token"
    if grant_type == "authorization_code":
        payload = {
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }
    elif grant_type == "refresh_token":
        payload = {
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": code,
            "grant_type": "refresh_token",
        }
    response = httpx.post(url, data=payload)
    if response.status_code != 200:
        logging.error("Error: %s", response.json().get("error_description"))
        with open("access_token.txt", "r", encoding="utf-8") as f:
            access_token = f.read()
            logging.info("Using old access token %s", access_token)
        return access_token, code
    logging.info("Generated tokens %s with response %s", payload, response.json())
    access_token = response.json().get("access_token")
    refresh_token = response.json().get("refresh_token")
    logging.info("access_token: %s", access_token)
    return access_token, refresh_token


def get_access_token():
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
    return access_token
