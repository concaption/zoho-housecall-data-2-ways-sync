import logging
import httpx
from config import settings
from schema.estimates import EstimatePayload, Address, Option, LineItem, Tax, Schedule, EstimateFields

logger = logging.getLogger(__name__)

headers = {
        "Accept": "application/json",
        "Authorization": "Token " + settings.HOUSECALL_API_KEY,
    }

BASE_URL = "https://api.housecallpro.com"

def create_estimates(data):
    url = BASE_URL + "/estimates"
    response = httpx.post(url, headers=headers, json=data)
    if response.status_code == 201:
        logger.info("Created estimates %s with response %s", data, response.json())
        return response.json()
    if response.status_code != 200:
        logger.error("Error creating estimates %s with response %s", data, response.json())
        return response.json()
    logger.info("Created estimates %s with response %s", data, response.json())
    return response.json()


def create_estimate_payload(incoming_data, **kwargs):
    customer_id = kwargs.get("customer_id", "")
    address_id = kwargs.get("address_id", "")
    # estimate_number = kwargs.get("estimate_number", 999)
    job_type_id = kwargs.get("job_type_id", "")
    assigned_employee_id = kwargs.get("assigned_employee_id", [])
    deal_id = incoming_data.deal_id
    if incoming_data.amount:
        total_cost = int(incoming_data.amount)*100
    else:
        total_cost = 0
    notes = incoming_data.notes + "\n" + "deal_id=" + deal_id
    payload = EstimatePayload(
        note=notes,
        message="message",
        customer_id=customer_id,
        assigned_employee_ids=[assigned_employee_id],
        address_id=address_id,
        lead_source=incoming_data.lead_source,
        address=Address(
            street=incoming_data.address,
            city=incoming_data.city,
            state=incoming_data.state,
            zip=incoming_data.zip_code,
        ),
        options=[
            Option(
                name=incoming_data.deal_name,
                line_items=[
                    LineItem(
                        name=incoming_data.deal_name,
                        description=incoming_data.notes,
                        unit_price=total_cost,
                        quantity=1,
                        unit_cost=total_cost,
                    )
                ]
            )
        ],
        estimate_fields=EstimateFields(
            job_type_id=job_type_id,
        )
    )
    return payload.model_dump()


def get_estimates():
    url = BASE_URL + "/estimates"
    response = httpx.get(url, headers=headers)
    if response.status_code != 200:
        logger.error("Error getting estimates with response %s", response.json())
        return response.json()
    logger.info("Got estimates with response %s", response.json())
    return response.json()

def get_estimates_of_customer(customer_id):
    url = BASE_URL + "/estimates"
    params = {"customer_id": str(customer_id)}
    response = httpx.get(url, headers=headers, params=params)
    if response.status_code != 200:
        logger.error("Error getting estimates with response %s", response.json())
        return response.json()
    estiamtes = response.json().get("estimates", [{"options":[{"name":"a"}]}])
    estimate_names = [estimate.get("options")[0].get("name") for estimate in estiamtes]
    return estimate_names

def get_estimate_with_id(estimate_id):
    url = BASE_URL + "/estimates/" + str(estimate_id)
    response = httpx.get(url, headers=headers)
    print(response.json())
    if response.status_code != 200:
        logger.error("Error getting estimate with id %s.", estimate_id)
        return None
    return response.json()

def get_estimate_with_customer_id(customer_id):
    url = BASE_URL + "/estimates"
    params = {"customer_id": str(customer_id), "page_size": 1000}
    response = httpx.get(url, headers=headers, params=params)
    if response.status_code != 200:
        logger.error("Error getting estimate with customer id %s.", customer_id)
        return None
    return response.json().get("estimates", [])


def create_option_note(estimate_id, option_id, notes):
    url = BASE_URL + "/estimates/" + estimate_id + "/options/" + option_id + "/notes"
    data = {"content": notes}
    response = httpx.post(url, headers=headers, json=data)
    if response.status_code != 201:
        logger.error("Error creating option note with response %s", response.json())
        return response.json()
    return response.json()