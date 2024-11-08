import logging
import httpx
from config import settings

logger = logging.getLogger(__name__)

headers = {
        "Accept": "application/json",
        "Authorization": "Token " + settings.HOUSECALL_API_KEY,
    }

BASE_URL = "https://api.housecallpro.com"

def get_job_types():
    url = BASE_URL + "/job_fields/job_types"
    response = httpx.get(url, headers=headers)
    if response.status_code != 200:
        logger.error("Error getting job types with response %s", response.json())
        return response.json()
    job_types = response.json().get('job_types')
    job_dict = {job['name'].lower().strip(): job['id'] for job in job_types}
    logger.info("Got job types %s", job_dict,)
    return job_dict
