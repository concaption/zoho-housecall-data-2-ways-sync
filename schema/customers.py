from pydantic import BaseModel

class CustomerPayload(BaseModel):
    first_name: str
    last_name: str
    email: str
    mobile_number: str
    home_number: str
    work_number: str
    lead_source: str
    notes: str
    addresses: list
