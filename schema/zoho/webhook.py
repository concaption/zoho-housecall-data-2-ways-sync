from typing import Optional
from pydantic import BaseModel, Field

class IncomingData(BaseModel):
    """Class representing a Deal info from ZOHO"""
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    mobile_number: Optional[str] = Field(alias='mobile_number')
    home_number: Optional[str] = Field(alias='home_number')
    work_number: Optional[str] = Field(alias='work_number')
    lead_source: Optional[str] = Field(alias='lead_source')
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zip_code: Optional[str] = Field(alias='zip_code')
    notes: Optional[str] = Field(alias='notes')
    acquired_date: Optional[str] = Field(alias='acquired_date')
    stage: Optional[str]
    deal_name: Optional[str] = Field(alias='deal_name')
    amount: Optional[str]
    employee_email: Optional[str] = Field(alias='employee_email')
    deal_id: Optional[str] = Field(alias='deal_id')
    reffered_by: Optional[str] = Field(alias='reffered_by')


class CustomerData(BaseModel):
    """Class representing a contact from ZOHO"""
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    mobile_number: Optional[str] = Field(alias='mobile_number')
    home_number: Optional[str] = Field(alias='home_number')
    work_number: Optional[str] = Field(alias='work_number')
    lead_source: Optional[str] = Field(alias='lead_source')
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zip_code: Optional[str] = Field(alias='zip_code')
    notes: Optional[str] = Field(alias='notes')
    # End-of-file (EOF)
