import logging
import httpx
from config import settings

logger = logging.getLogger(__name__)

headers = {
        "Accept": "application/json",
        "Authorization": "Token " + settings.HOUSECALL_API_KEY,
    }

BASE_URL = "https://api.housecallpro.com"

def get_tags():
    url = BASE_URL + "/tags"
    response = httpx.get(url, headers=headers)
    if response.status_code != 200:
        logger.error("Error getting tags with response %s", response.json())
        return response.json()
    tags = response.json().get('tags')
    tags_dict = {tag['name'].lower().strip(): tag['id'] for tag in tags}
    logger.info("Got tags %s", tags_dict)
    return tags_dict
