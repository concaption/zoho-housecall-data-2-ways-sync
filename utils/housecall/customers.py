import logging
import httpx
from config import settings
from schema.customers import CustomerPayload

logger = logging.getLogger(__name__)

headers = {
        "Accept": "application/json",
        "Authorization": "Token " + settings.HOUSECALL_API_KEY,
    }

BASE_URL = "https://api.housecallpro.com"

def create_customer(data):
    url = BASE_URL + "/customers"
    response = httpx.post(url, headers=headers, json=data)
    if response.status_code == 201:
        logger.info("Created customer %s with response %s", data, response.json())
        return response.json()
    if response.status_code != 200:
        logger.error("Error creating customer %s with response %s", data, response.json())
        return response.json()
    logger.info("Created customer %s with response %s", data, response.json())
    return response.json()


def create_customer_payload(incoming_data):
    incoming_data.mobile_number = incoming_data.mobile_number.replace('-', '')[-10:]
    payload = CustomerPayload(
        first_name=incoming_data.first_name,
        last_name=incoming_data.last_name,
        email=incoming_data.email,
        mobile_number=incoming_data.mobile_number,
        home_number=incoming_data.home_number,
        work_number=incoming_data.work_number,
        lead_source=incoming_data.lead_source,
        notes=incoming_data.notes,
        addresses=[
            {
                "street": incoming_data.address,
                "city": incoming_data.city,
                "state": incoming_data.state,
                "zip": incoming_data.zip_code,
                "country": "US",
            }
        ],
    )
    return payload.model_dump()

def get_cusomter_by_email(email):
    url = BASE_URL + "/customers"
    params = {"q": email}
    response = httpx.get(url, headers=headers, params=params)
    if response.status_code == 204:
        logger.error("No customer found with email %s", email)
        return None
    logger.info("Got HouseCall customer %s with response", email)
    customers = response.json().get("customers")
    return customers[0] if customers else None
