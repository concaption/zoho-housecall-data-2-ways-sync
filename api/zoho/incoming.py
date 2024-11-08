import logging
from datetime import datetime
from fastapi import APIRouter
import pandas as pd

from utils.zoho.deals import get_deals_by_account_id
from utils.zoho.contacts import get_contact_by_email
from utils.zoho.deals import update_deal, create_deal

from utils.housecall.jobs import get_job_with_id, list_all_line_items_for_a_job
from utils.housecall.estimates import get_estimate_with_id, get_estimate_with_customer_id, create_option_note

from utils.housecall.webhook import detect_webook_event, get_zoho_deals, get_zoho_deal_id, get_approved_options
from utils.misc import probability_mapper
from utils.sheets import SheetsClient
from config import settings


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/zoho", tags=["zoho"])


@router.post("/incoming")
async def receive_webhook(data:dict):
    print(data)

    event, action = detect_webook_event(data)




    ## TEST EVENT
    if event == "test":
        return data
    

    
    ## ESTIMATE EVENT
    if event == "estimate":
        if action == "option.created":
            estimate = data.get("estimate")
            options = estimate.get("options")
            estimate_id = estimate.get('id')
            last_option = options[-1]
            option_id = last_option.get("id")
            zoho_deal_id = get_zoho_deal_id(estimate)
            if not zoho_deal_id:
                logger.info("Zoho deal id not found")
                return {"message": "Option created. Doing nothing."}
            notes_to_create = "deal_id=" + zoho_deal_id
            notes_created = create_option_note(estimate_id, option_id, notes_to_create)
            if notes_created:
                logger.info("Option note created")
                return {"message": "Option note created."}
            logger.info("Just an Option created. Notes not created.")
            return {"message": "Option created. Doing nothing."}
        data = data.get("estimate")
        options = data.get("options")
        zoho_deal_id = get_zoho_deal_id(data)
        """
        option_names = [option.get("name") for option in options]
        zoho_deals_names, zoho_deals = get_zoho_deals(data)
        if action == "created":
            if zoho_deal_id:
                logger.info(f"Not creating deal. Deal with zoho id {zoho_deal_id} already created by Zoho.")
                return {"message": f"Deal {zoho_deal_id} already created by Zoho"}
            if option_names[0] in zoho_deals_names:
                logger.info("Not creating deal. Deal already exists.")
                return {"message": "Deal already exists."}
            logger.info("No deal found. Creating deal.")
            logger.info("Functionality not implemented yet.")
        """
        sheet_client = SheetsClient(settings.CREDENTIALS_FILE_PATH)
        assigned_employees = ",".join([employee.get("email") for employee in data.get("assigned_employees")]) or ""
        if action == "option.approval_status_changed":
            if not zoho_deal_id:
                logger.info("No deal found for this estimate in Zoho. Trying to create one.")
                return {"message": "No deal found for this estimate"}
            approved_options, declined_options = get_approved_options(options)
            if not approved_options:
                logger.info("No approved options found. Checking for declined options.")
                if declined_options:
                    logger.info("Declined options found. Updating deal stage to Closed-Lost to Pricing")
                    option_amount = float(declined_options[-1].get("total_amount"))/100
                    deal_stage = probability_mapper("Closed-Lost to Pricing")
                    data = {
                        "Amount": option_amount,
                        "Stage": deal_stage,
                    }
                    response = update_deal(zoho_deal_id, data)
                    logger.info("Updated the lost deal in Zoho: %s", response)
                    deal_dict = {
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "deal_id": "deal_" + zoho_deal_id,
                        "assigned_employees": assigned_employees,
                        "total_cost": option_amount,
                        "status": "declined"
                    }
                    appended = sheet_client.add_deal("HCP Estimates", settings.SPREADSHEET_NAME, deal_dict)
                    if appended:
                        logger.info("Successfully appended row to sheet")
                    return {"message": "Updated the lost deal in Zoho"}
                logger.info("No declined options found. Doing nothing.")
                return {"message": "No declined options found. Doing nothing."}
            last_approved_option = approved_options[-1]
            deal_stage = probability_mapper("Estimate Approved")
            option_amount = float(last_approved_option.get("total_amount"))/100
            data = {
                "Amount": option_amount,
                "Stage": deal_stage,
            }
            response = update_deal(zoho_deal_id, data)
            logger.info("Updated estimate status changed in Zoho: %s", response)
            deal_dict = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "deal_id": "deal_" + zoho_deal_id,
                "assigned_employees": assigned_employees,
                "total_cost": option_amount,
                "status": "approved"
            }
            appended = sheet_client.add_deal("HCP Estimates", settings.SPREADSHEET_NAME, deal_dict)
            if appended:
                logger.info("Successfully appended row to sheet")
            return {"message": "Updated estimate status changed in Zoho"}
        if action == "sent":
            if not zoho_deal_id:
                logger.info("No deal found for this estimate in Zoho. Try creating one.")
                return {"message": "No deal found for this estimate"}
            deal_stage = probability_mapper("Estimate Pending (send)")
            sent_options = [option for option in options if option.get("status") == "submitted for signoff"]
            if not sent_options:
                logger.info("No sent options found. Updating deal stage to Estimate Pending (send)")
                return {"message": "No sent options found"}
            first_sent_option = sent_options[-1]
            option_amount = float(first_sent_option.get("total_amount"))/100
            data = {
                "Amount": option_amount,
                "Stage": deal_stage,
            }
            response = update_deal(zoho_deal_id, data)
            logger.info("Updated `Estimate Pending (send)` in Zoho: %s", response)
            deal_dict = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "deal_id": "deal_" + zoho_deal_id,
                "assigned_employees": assigned_employees,
                "total_cost": option_amount,
                "status": "sent"
            }
            appended = sheet_client.add_deal("HCP Estimates", settings.SPREADSHEET_NAME, deal_dict)
            if appended:
                logger.info("Successfully appended row to sheet")
            return {"message": "Updated estimate sent in Zoho"}
    


    ## JOB EVENT
    if event == "job":
        if action == "appointment.scheduled":
            data = data.get("appointment")
            job_id = data.get("job_id")
            job = get_job_with_id(job_id)
            if not job:
                logger.error("No job found with id %s", job_id)
                return {"message": "No job found with id"}
            zoho_deal_id = get_zoho_deal_id(job, job=True)
            if not zoho_deal_id:
                logger.info("No deal found for this estimate in Zoho. Try creating one.")
                return {"message": "No deal found for this estimate"}
            total_amount = float(job.get("total_amount"))/100
            deal_stage = probability_mapper("Won Add Appoitment Schedule")
            update_data = {
                "Amount": total_amount,
                "Stage": deal_stage,
            }
            response = update_deal(zoho_deal_id, update_data)
            logger.info("Updated `Won Add Appoitment Schedule` in Zoho: %s", response)

            sheet_client = SheetsClient(settings.CREDENTIALS_FILE_PATH)
            dispatched_employees = data.get("dispatched_employees") or [{"email": ""}]
            assigned_employees = ",".join([employee.get("email") for employee in dispatched_employees])
            # original_estimate_id = job.get("original_estimate_id")
            # logger.info("Original estimate id: %s", original_estimate_id)
            # customer_id = job.get("customer").get("id")
            # estimates = get_estimate_with_customer_id(customer_id)
            # option = None
            # hcp_estimate_id = None
            # for estimate in estimates:
            #     estimate_options_ids = [option.get("id") for option in estimate.get("options")]
            #     estimate_id = estimate.get("id")
            #     for option_id in estimate_options_ids:
            #         if option_id == original_estimate_id:
            #             logger.info("Found estimate with id %s", estimate_id)
            #             option = [option for option in estimate.get("options") if option.get("id") == original_estimate_id][0]
            #             hcp_estimate_id = estimate_id
            #             break
            service_items_total, material_items_total = list_all_line_items_for_a_job(job_id, amount_only=True)
            total_amount = float(job.get("total_amount"))/100
            started_at = job.get('work_timestamps').get('started_at')
            completed_at = job.get('work_timestamps').get('completed_at')
            on_my_way_at = job.get('work_timestamps').get('on_my_way_at')
            scheduled_start=job.get('schedule').get('scheduled_start')
            scheduled_end=job.get('schedule').get('scheduled_end')
            deal_dict = {
                "deal_id": "deal_" + zoho_deal_id,
                "assigned_employees": assigned_employees,
                "total_cost": total_amount,
                "service_cost": service_items_total,
                "material_cost": material_items_total,
                "scheduled_start": scheduled_start,
                "scheduled_end": scheduled_end,
                "started_at": started_at,
                "completed_at": completed_at,
                "on_my_way_at": on_my_way_at,
            }
            appended = sheet_client.add_deal("HCP Appointments", settings.SPREADSHEET_NAME, deal_dict)
            if appended:
                logger.info("Successfully appended row to sheet")
            return {"message": "Updated `Won Add Appoitment Schedule` in Zoho"}



        if action == "paid":
            data = data.get("job")
            # estimate_id = data.get("original_estimate_id")
            # if not estimate_id:
            #     logger.info("No estimate id found in job. Doing nothing.")
            #     return {"message": "No estimate id found in job. Doing nothing."}
            # estimate = get_estimate_with_id(estimate_id)
            # if not estimate:
            #     logger.info("No estimate found with id %s", estimate_id)
            #     return {"message": "No estimate found with id"}
            zoho_deal_id = get_zoho_deal_id(data, job=True)
            if not zoho_deal_id:
                logger.info("No deal found for this estimate in Zoho. Try creating one.")
                return {"message": "No deal found for this estimate"}
            total_amount = float(data.get("total_amount"))/100
            outstanding_balance = float(data.get("outstanding_balance", 0))/100
            # if half payment is done, then stage is "Won Job Completed (PAY)"
            if outstanding_balance == total_amount/2:
                deal_stage = probability_mapper("Won Add Appoitment Schedule")
                data = {
                    "Amount": total_amount,
                    "Stage": deal_stage,
                }
                response = update_deal(zoho_deal_id, data)
                logger.info("Updated `Won Add Appoitment Schedule` in Zoho: %s", response)
                return {"message": "Updated `Won Add Appoitment Schedule` in Zoho"}
            elif outstanding_balance == 0:
                deal_stage = probability_mapper("Won Job Completed (PAY)")
                data = {
                    "Amount": total_amount,
                    "Stage": deal_stage,
                }
                response = update_deal(zoho_deal_id, data)
                logger.info("Updated `Won Job Completed (PAY)` in Zoho: %s", response)
                return {"message": "Updated `Won Job Completed (PAY)` in Zoho"}
            else:
                logger.info("Outstanding amount is not half or zero. Doing nothing.")
                return {"message": "Outstanding amount is not half or zero. Doing nothing."}
            
        if action == "completed" or action == "started" or action == "on_my_way":
            job = data.get("job")
            job_id = job.get("id")
            job = get_job_with_id(job_id)
            if not job:
                logger.error("No job found with id %s", job_id)
                return {"message": "No job found with id"}
            zoho_deal_id = get_zoho_deal_id(job, job=True)
            if not zoho_deal_id:
                logger.info("No deal found for this estimate in Zoho. Try creating one.")
                return {"message": "No deal found for this estimate"}
            
            sheet_client = SheetsClient(settings.CREDENTIALS_FILE_PATH)
            total_amount = float(job.get("total_amount"))/100
            assigned_employees = ",".join([employee.get("email") for employee in job.get("assigned_employees")])
            service_items_total, material_items_total = list_all_line_items_for_a_job(job_id, amount_only=True)
            started_at = job.get('work_timestamps').get('started_at')
            completed_at = job.get('work_timestamps').get('completed_at')
            on_my_way_at = job.get('work_timestamps').get('on_my_way_at')
            scheduled_start=job.get('schedule').get('scheduled_start')
            scheduled_end=job.get('schedule').get('scheduled_end')
            deal_dict = {
                "deal_id": "deal_" + zoho_deal_id,
                "assigned_employees": assigned_employees,
                "total_cost": total_amount,
                "service_cost": service_items_total,
                "material_cost": material_items_total,
                "scheduled_start": scheduled_start,
                "scheduled_end": scheduled_end,
                "started_at": started_at,
                "completed_at": completed_at,
                "on_my_way_at": on_my_way_at,
            }
            appended = sheet_client.add_deal("HCP Appointments", settings.SPREADSHEET_NAME, deal_dict)
            if appended:
                logger.info("Successfully appended row to sheet")
