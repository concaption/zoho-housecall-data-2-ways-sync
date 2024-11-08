from typing import List, Optional
from pydantic import BaseModel

class Address(BaseModel):
    street: Optional[str] = None
    street_line_2: Optional[str] = None 
    city: str
    state: str
    zip: str

class LineItem(BaseModel):
    name: str
    description: str
    unit_price: float
    quantity: int
    unit_cost: float

class Option(BaseModel):
    name: str
    tags: Optional[List[str]] = None
    line_items: List[LineItem]

class Tax(BaseModel):
    taxable: bool
    tax_rate: float
    tax_name: str

class Schedule(BaseModel):
    start_time: str
    end_time: str
    arrival_window_in_minutes: int
    notify_customer: bool

class EstimateFields(BaseModel):
    job_type_id: str
    business_unit_id: Optional[str] = None

class EstimatePayload(BaseModel):
    note: str
    message: str
    customer_id: str
    assigned_employee_ids: List[str]
    address_id: str
    lead_source: str
    address: Address
    options: List[Option]
    tax: Optional[Tax] = None
    schedule: Optional[Schedule] = None
    estimate_fields: Optional[EstimateFields] = None
