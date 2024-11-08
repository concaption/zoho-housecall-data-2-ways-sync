import logging
import httpx
from config import settings

logger = logging.getLogger(__name__)

headers = {
        "Accept": "application/json",
        "Authorization": "Token " + settings.HOUSECALL_API_KEY,
    }

BASE_URL = "https://api.housecallpro.com"

def get_lead_sources():
    url = BASE_URL + "/lead_sources"
    response = httpx.get(url, headers=headers)
    lead_sources = response.json()
    lead_sources = {lead_source["name"]: lead_source["id"] for lead_source in lead_sources["lead_sources"]}
    logger.info("Got lead sources %s", lead_sources)
    return lead_sources

def create_lead_source(name):
    url = BASE_URL + "/lead_sources"
    data = {"name": name}
    response = httpx.post(url, headers=headers, json=data)
    logger.info("Created lead source %s with response %s", name, response.json())
    return response.json()
