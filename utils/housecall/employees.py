import logging
import httpx
from config import settings

logger = logging.getLogger(__name__)

headers = {
        "Accept": "application/json",
        "Authorization": "Token " + settings.HOUSECALL_API_KEY,
    }

BASE_URL = "https://api.housecallpro.com"

def get_employees():
    url = BASE_URL + "/employees"
    response = httpx.get(url, headers=headers)
    if response.status_code != 200:
        logger.error("Error getting employees with response %s", response.json())
        return response.json()
    employees = response.json()
    employee_dict = {employee['email'].lower(): employee['id'] for employee in employees['employees']}
    logger.info("Got employees %s", employee_dict)
    return employee_dict
