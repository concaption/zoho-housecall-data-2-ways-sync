def probability_mapper(picklist_value):
    probability_map = {
        "Deal": "Qualification",
        "Estimate Pending (send)": "Estimate Pending (send)",
        "Estimate Approved": "Negotiation/Review",
        "Won Add Appoitment Schedule": "Close Won/Scheduling",
        "Won Job Completed (PAY)": "Closed Won",
        "Closed-Lost to Competition": "Closed-Lost to Competition",
        "Closed-Lost to Pricing": "Closed-Lost to Pricing",
    }
    reference_value = probability_map.get(picklist_value, "0")
    return reference_value
