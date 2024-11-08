import logging
from fastapi import APIRouter

from config import settings

from schema.zoho.webhook import IncomingData,CustomerData
from utils.housecall.lead_sources import get_lead_sources, create_lead_source
from utils.housecall.customers import create_customer_payload, create_customer, get_cusomter_by_email
from utils.housecall.estimates import create_estimate_payload, create_estimates, get_estimates_of_customer
from utils.housecall.job_types import get_job_types
from utils.housecall.employees import get_employees

from utils.sheets import SheetsClient



logger = logging.getLogger(__name__)
router = APIRouter(prefix="/housecall", tags=["housecall"])

BASE_URL = "https://api.housecallpro.com"
headers={
            'Accept': 'application/json',
            'Authorization': "Token " + settings.HOUSECALL_API_KEY,
            'Content-Type': 'application/json'
        }

@router.post("/incoming")
async def receive_webhook(incoming_data: IncomingData):
    logger.info("Received data from Zoho %s", incoming_data)
    if incoming_data.lead_source == "":
        incoming_data.lead_source = "Other"
    lead_sources = get_lead_sources()
    if incoming_data.lead_source not in lead_sources:
        create_lead_source(incoming_data.lead_source)
    payload = create_customer_payload(incoming_data)
    old_customer = get_cusomter_by_email(incoming_data.email)
    extra_data = {}
    if old_customer:
        logger.info("Customer already exists %s", old_customer.get("id"))
        extra_data['customer_id'] = old_customer.get("id")
        extra_data['address_id'] = old_customer.get("addresses")[0].get("id")
    else:
        response = create_customer(payload)
        extra_data['customer_id'] = response.get('id')
        extra_data['address_id'] = response.get('addresses')[0].get('id')
    """
    old_estimates = get_estimates_of_customer(extra_data.get('customer_id'))
    print("Previous Estimates: ", old_estimates)
    if incoming_data.deal_name in old_estimates:
        logger.info("Estimate already exists %s. Returned.", incoming_data.deal_name)
        return {"message": "Estimate already exists"}
    else:
        logger.info("Estimate does not exist. Creating estimate.")
    """
    job_type_id = get_job_types().get("diagnostics")
    assigned_employee_id = get_employees().get(incoming_data.employee_email) or "pro_2056f4998a454af39665e718aace8efe"
    extra_data['job_type_id'] = job_type_id
    extra_data['assigned_employee_id'] = assigned_employee_id
    # extra_data['estimate_number'] = "99999"
    payload = create_estimate_payload(incoming_data, **extra_data)
    response = create_estimates(payload)
    sheet_client = SheetsClient(settings.CREDENTIALS_FILE_PATH)
    row_to_append = ["deal_" + incoming_data.deal_id, incoming_data.lead_source, incoming_data.employee_email, incoming_data.deal_name,incoming_data.reffered_by ]
    appended = sheet_client.append_row(settings.SHEET_NAME, settings.SPREADSHEET_NAME, row_to_append)
    if appended:
        logger.info("Successfully appended row to sheet")
    return {"message": "Successfully sent data to HCP"}


@router.post("/customer")
async def receive_webhook_customer(customer_data: CustomerData):
    logger.info("Received data from Zoho for customer %s", customer_data)
    print(customer_data)
    if customer_data.lead_source == "":
        customer_data.lead_source = "Other"
    lead_sources = get_lead_sources()
    if customer_data.lead_source not in lead_sources:
        create_lead_source(customer_data.lead_source)
    payload = create_customer_payload(customer_data)
    old_customer = get_cusomter_by_email(customer_data.email)
    extra_data = {}
    if old_customer:
        logger.info("Customer already exists %s", old_customer.get("id"))
        extra_data['customer_id'] = old_customer.get("id")
        extra_data['address_id'] = old_customer.get("addresses")[0].get("id")
    else:
        response = create_customer(payload)
        extra_data['customer_id'] = response.get('id')
        extra_data['address_id'] = response.get('addresses')[0].get('id')
    sheet_client = SheetsClient(settings.CREDENTIALS_FILE_PATH)
    row_to_append = ["acc_" + customer_data.first_name, customer_data.last_name, customer_data.email, customer_data.home_number,customer_data.address,customer_data.city,customer_data.mobile_number,customer_data.work_number,customer_data.zip_code,customer_data.state,]
    appended = sheet_client.append_row(settings.SHEET_NAME2, settings.SPREADSHEET_NAME, row_to_append)
    if appended:
        logger.info("Successfully appended row to sheet")
    return {"message": "Successfully sent data to HCP"}