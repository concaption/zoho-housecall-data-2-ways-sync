import logging
import httpx
from utils.zoho.authenticate import get_access_token

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

BASE_URL = "https://www.zohoapis.com/crm/v6"

def get_contact_by_email(email):
    url = BASE_URL + "/Contacts/search"
    params = {"email": str(email)}
    headers = {
        "Authorization": "Bearer " + get_access_token(),
    }
    response = httpx.get(url, headers=headers, params=params)
    if response.status_code == 204:
        logger.error("No contact found with email %s", email)
        return None
    if response.status_code != 200:
        logger.error("Error getting contact for %s, %s", email, response.json())
        return None
    contact = response.json()["data"][0]
    contact_id = contact["id"]
    logger.info("Got contact %s with id %s", email, contact_id)
    return contact_id
