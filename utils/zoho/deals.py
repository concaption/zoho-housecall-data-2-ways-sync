import logging
import httpx
from utils.zoho.authenticate import get_access_token

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

BASE_URL = "https://www.zohoapis.com/crm/v6"

def get_deals_by_account_id(account_id):
    url = BASE_URL + "/Deals/search"
    params = {"criteria": f"(Contact_Name.id:equals:{account_id})", "sort_by": "Created_Time", "sort_order": "desc", "fields": "id,Deal_Name,Stage,Amount,Created_Time,Contact_Name,Account_Name,Description"}
    headers = {
        "Authorization": "Bearer " + get_access_token(),
    }
    response = httpx.get(url, headers=headers, params=params)
    if response.status_code != 200:
        logger.error("Error getting deals for %s", account_id)
        return None
    return response.json()["data"]

def update_deal(deal_id, data):
    url = BASE_URL + "/Deals/" + deal_id
    headers = {
        "Authorization": "Bearer " + get_access_token(),
    }
    payload = {
            "data": [
                data
                ]
            }
    response = httpx.put(url, headers=headers, json=payload)
    if response.status_code != 200:
        logger.error("Error updating deal %s", deal_id)
        return response.json()
    return response.json()

def create_deal(data):
    url = BASE_URL + "/Deals"
    headers = {
        "Authorization": "Bearer " + get_access_token(),
    }
    payload = { "data": [ data ] }
    response = httpx.post(url, headers=headers, json=payload)
    print(response.status_code)
    if response.status_code != 201:
        logger.error("Error creating deal")
        return response.json()
    return response.json()
