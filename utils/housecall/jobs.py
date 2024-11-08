import logging
import httpx
from config import settings

logger = logging.getLogger(__name__)

headers = {
        "Accept": "application/json",
        "Authorization": "Token " + settings.HOUSECALL_API_KEY,
    }

BASE_URL = "https://api.housecallpro.com"

def get_job_with_id(job_id):
    url = BASE_URL + "/jobs/" + str(job_id)
    response = httpx.get(url, headers=headers)
    if response.status_code != 200:
        logger.error("Error getting job with id %s.", job_id)
        return None
    return response.json()

def list_all_line_items_for_a_job(job_id, amount_only=False):
    url = BASE_URL + "/jobs/" + str(job_id) + "/line_items"
    response = httpx.get(url, headers=headers)
    if response.status_code != 200:
        logger.error("Error getting job items for job with id %s.", job_id)
        return None
    line_items = response.json().get("data")
    if not line_items:
        logger.error("No line items found for job with id %s.", job_id)
        return None
    if amount_only:
        service_items = [item.get("amount") for item in line_items if item.get("kind") == "labor"]
        material_items = [item.get("amount") for item in line_items if item.get("kind") == "materials"]
        service_items_total = float(sum(service_items))/100
        material_items_total = float(sum(material_items))/100
        return service_items_total, material_items_total
    service_items = [item for item in line_items if item.get("kind") == "labor"]
    material_items = [item for item in line_items if item.get("kind") == "materials"]
    return service_items, material_items
