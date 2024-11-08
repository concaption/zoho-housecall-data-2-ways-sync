import logging
from utils.zoho.contacts import get_contact_by_email
from utils.zoho.deals import get_deals_by_account_id


logger = logging.getLogger(__name__)

def detect_webook_event(data):
    if data ==  {"foo": "bar"}:
        return "test", "test"
    event = data.get("event", "")
    if event:
        event = event.split(".")
        if len(event) == 2:
            return event[0], event[-1]
        if len(event) == 3:
            action = event[-2] + "." + event[-1]
        logger.info("Detected ` %s ` event with ` %s ` action", event[0], action)
        return event[0], action
    else:
        logger.error("No event found in the webhook")
        return "error", "error"

def get_zoho_deal_id(data, job=False):
    if job:
        notes = data.get("notes")
    else:
        notes = data.get("options", [{}])[0].get("notes")
    zoho_deal_id = ""
    if notes:
        notes_content = "\n".join([note.get("content", "") for note in notes])
        if notes_content:
            # split by new line and get the line that starts with deal_id
            split_content = notes_content.split("\n")
            for line in split_content:
                if line.startswith("deal_id"):
                    zoho_deal_id = line.split("=")[-1]
                    break
    logger.info("zoho_deal_id: %s", zoho_deal_id)
    return zoho_deal_id


def get_zoho_deals(data):
    customer = data.get("customer")
    customer_email = customer.get("email")
    zoho_contact_id = get_contact_by_email(customer_email)
    if not zoho_contact_id:
        logger.error("Either no contact found with email %s or authentication issue.", customer_email)
        return [], []
    zoho_deals = get_deals_by_account_id(zoho_contact_id)
    if not zoho_deals:
        logger.info("No deals found for %s in Zoho", zoho_contact_id)
        return [], []
    zoho_deals_names = [deal.get("Deal_Name") for deal in zoho_deals]
    logger.info("zoho_deals_names: %s", zoho_deals_names)
    return zoho_deals_names, zoho_deals

def get_approved_options(options):
    approved_options = [option for option in options if option.get("approval_status") == "pro approved" or option.get("approval_status") == "approved"]
    declined_options = [option for option in options if option.get("approval_status") == "pro declined" or option.get("approval_status") == "declined"]
    return approved_options, declined_options
