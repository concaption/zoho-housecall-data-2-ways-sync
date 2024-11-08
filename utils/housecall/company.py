import logging
import httpx
from config import settings

logger = logging.getLogger(__name__)

headers = {
        "Accept": "application/json",
        "Authorization": "Token " + settings.HOUSECALL_API_KEY,
    }

BASE_URL = "https://api.housecallpro.com"

def get_company():
    url = BASE_URL + "/company"
    response = httpx.get(url, headers=headers)
    if response.status_code != 200:
        logger.error("Error getting company with response %s", response.json())
        return response.json()
    company = response.json()
    logger.info("Got company %s", company)
    return company
