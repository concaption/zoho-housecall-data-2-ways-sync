import logging
from fastapi import APIRouter

from utils.zoho.deals import update_deal


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/zoho", tags=["zoho"])
