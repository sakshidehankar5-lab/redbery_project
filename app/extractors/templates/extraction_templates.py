"""
Template-Based Extraction
--------------------------
Each document type has:
  - A list of expected output fields (with description)
  - A system prompt fragment
  - An optional validation function

Templates follow the Factory Method pattern.
"""
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class FieldDefinition:
    name: str
    description: str
    required: bool = True
    example: Optional[str] = None


@dataclass
class ExtractionTemplate:
    document_type: str
    display_name: str
    fields: List[FieldDefinition]
    system_instructions: str
    validator: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None


# ─────────────────────────────────────────────────────────────────────────────
# AADHAAR CARD
# ─────────────────────────────────────────────────────────────────────────────

AADHAAR_TEMPLATE = ExtractionTemplate(
    document_type="aadhaar",
    display_name="Aadhaar Card",
    fields=[
        FieldDefinition("name", "Full name of the cardholder", required=True, example="Ramesh Kumar"),
        FieldDefinition("aadhaar_number", "12-digit Aadhaar UID (may be masked)", required=True, example="XXXX XXXX 1234"),
        FieldDefinition("date_of_birth", "Date of birth in DD/MM/YYYY format", required=False, example="15/08/1990"),
        FieldDefinition("gender", "Gender: Male/Female/Transgender", required=False, example="Male"),
        FieldDefinition("address", "Full address including PIN code", required=False, example="123 MG Road, Pune 411001"),
        FieldDefinition("phone_number", "Mobile number if present (last 3 digits may be masked)", required=False),
        FieldDefinition("vid", "Virtual ID if present", required=False),
    ],
    system_instructions=(
        "You are extracting data from an Indian Aadhaar Card. "
        "The Aadhaar number is 12 digits and may appear masked as XXXX XXXX XXXX. "
        "The address on Aadhaar is in Indian regional format — capture it completely. "
        "Do NOT invent data; if a field is unclear use null."
    ),
)

# ─────────────────────────────────────────────────────────────────────────────
# DRIVING LICENCE
# ─────────────────────────────────────────────────────────────────────────────

DRIVING_LICENCE_TEMPLATE = ExtractionTemplate(
    document_type="driving_licence",
    display_name="Driving Licence",
    fields=[
        FieldDefinition("licence_number", "DL number (state code + digits)", required=True, example="MH0120120012345"),
        FieldDefinition("name", "Full name of holder", required=True),
        FieldDefinition("father_or_husband_name", "Father's or husband's name", required=False),
        FieldDefinition("date_of_birth", "DOB in DD/MM/YYYY", required=True),
        FieldDefinition("address", "Full residential address", required=False),
        FieldDefinition("issue_date", "Date of issue DD/MM/YYYY", required=False),
        FieldDefinition("expiry_date", "Date of expiry DD/MM/YYYY", required=False),
        FieldDefinition("vehicle_classes", "List of vehicle classes authorised (e.g. LMV, MCWG)", required=False),
        FieldDefinition("issuing_rto", "Issuing RTO name/code", required=False),
        FieldDefinition("blood_group", "Blood group if printed", required=False),
    ],
    system_instructions=(
        "You are extracting data from an Indian Driving Licence. "
        "Licence numbers follow the pattern: 2-letter state code + 2-digit RTO + year + serial. "
        "Vehicle classes may include: LMV, MCWG, MCWOG, Transport, HMV, etc. "
        "Dates are typically in DD/MM/YYYY format."
    ),
)

# ─────────────────────────────────────────────────────────────────────────────
# PASSPORT
# ─────────────────────────────────────────────────────────────────────────────

PASSPORT_TEMPLATE = ExtractionTemplate(
    document_type="passport",
    display_name="Passport",
    fields=[
        FieldDefinition("passport_number", "Passport number (letter + 7 digits)", required=True, example="A1234567"),
        FieldDefinition("surname", "Surname / family name", required=True),
        FieldDefinition("given_names", "Given names", required=True),
        FieldDefinition("nationality", "Nationality", required=True, example="Indian"),
        FieldDefinition("date_of_birth", "DOB in DD/MM/YYYY", required=True),
        FieldDefinition("gender", "Sex: M/F/X", required=True),
        FieldDefinition("place_of_birth", "Place of birth", required=False),
        FieldDefinition("issue_date", "Date of issue DD/MM/YYYY", required=False),
        FieldDefinition("expiry_date", "Date of expiry DD/MM/YYYY", required=True),
        FieldDefinition("place_of_issue", "Place of issue / issuing authority", required=False),
        FieldDefinition("mrz_line1", "First MRZ line (44 chars)", required=False),
        FieldDefinition("mrz_line2", "Second MRZ line (44 chars)", required=False),
        FieldDefinition("file_number", "File number if visible", required=False),
    ],
    system_instructions=(
        "You are extracting data from a passport. "
        "Capture the MRZ (Machine Readable Zone) lines exactly as they appear — "
        "they are at the bottom of the photo page and use '<' as filler. "
        "Indian passports have a file number starting with letters. "
        "Do not confuse surname with given name."
    ),
)

# ─────────────────────────────────────────────────────────────────────────────
# INVOICE
# ─────────────────────────────────────────────────────────────────────────────

INVOICE_TEMPLATE = ExtractionTemplate(
    document_type="invoice",
    display_name="Invoice",
    fields=[
        FieldDefinition("invoice_number", "Invoice / bill number", required=True),
        FieldDefinition("invoice_date", "Invoice date", required=True),
        FieldDefinition("due_date", "Payment due date if stated", required=False),
        FieldDefinition("vendor_name", "Seller / vendor company name", required=True),
        FieldDefinition("vendor_gstin", "Vendor GSTIN (15-char alphanumeric)", required=False),
        FieldDefinition("vendor_address", "Vendor address", required=False),
        FieldDefinition("customer_name", "Buyer / customer name", required=True),
        FieldDefinition("customer_gstin", "Customer GSTIN", required=False),
        FieldDefinition("customer_address", "Customer billing/shipping address", required=False),
        FieldDefinition("line_items", "List of {description, quantity, unit_price, amount}", required=False),
        FieldDefinition("subtotal", "Subtotal before tax (numeric)", required=False),
        FieldDefinition("cgst_amount", "CGST amount (numeric)", required=False),
        FieldDefinition("sgst_amount", "SGST amount (numeric)", required=False),
        FieldDefinition("igst_amount", "IGST amount (numeric)", required=False),
        FieldDefinition("total_amount", "Final total amount payable (numeric)", required=True),
        FieldDefinition("currency", "Currency code e.g. INR, USD", required=False, example="INR"),
        FieldDefinition("payment_terms", "Payment terms if stated", required=False),
        FieldDefinition("bank_details", "Bank account details for payment if present", required=False),
    ],
    system_instructions=(
        "You are extracting data from a business invoice. "
        "Line items should be a JSON array. "
        "For monetary amounts, extract the numeric value only (no currency symbols). "
        "GSTIN is 15 characters: 2-digit state code + 10-char PAN + 1 char + 1 char + Z/checksum."
    ),
)

# ─────────────────────────────────────────────────────────────────────────────
# Template Registry — Factory Method
# ─────────────────────────────────────────────────────────────────────────────

_REGISTRY: Dict[str, ExtractionTemplate] = {
    "aadhaar": AADHAAR_TEMPLATE,
    "driving_licence": DRIVING_LICENCE_TEMPLATE,
    "passport": PASSPORT_TEMPLATE,
    "invoice": INVOICE_TEMPLATE,
}


def get_template(document_type: str) -> ExtractionTemplate:
    """Factory — returns template for a given document type."""
    from app.core.exceptions import TemplateNotFoundException
    template = _REGISTRY.get(document_type.lower())
    if not template:
        raise TemplateNotFoundException(
            f"No extraction template for document type: '{document_type}'",
            details={"available_types": list(_REGISTRY.keys())},
        )
    return template


def list_templates() -> List[ExtractionTemplate]:
    return list(_REGISTRY.values())
