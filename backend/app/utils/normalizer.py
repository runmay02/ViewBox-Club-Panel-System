import re
from datetime import date, datetime
from typing import Optional
from dateutil.relativedelta import relativedelta

def normalize_phone(phone_input: Optional[str]) -> Optional[str]:
    """Normalize Indian phone number to 10 digits."""
    if not phone_input:
        return None
    s = re.sub(r"[^0-9]", "", str(phone_input).strip())
    # Strip country code 91 if 12 digits
    if s.startswith("91") and len(s) == 12:
        s = s[2:]
    # Strip leading 0 if 11 digits
    elif s.startswith("0") and len(s) == 11:
        s = s[1:]

    # Must be 10 digits starting with 6, 7, 8, or 9
    if len(s) == 10 and s[0] in "6789":
        return s
    return None

def mask_phone(phone: Optional[str]) -> str:
    """Mask phone number for respondent privacy (e.g. 98XXXXXX21)."""
    if not phone:
        return "XXXXXXXXXX"
    clean = re.sub(r"[^0-9]", "", phone)
    if len(clean) == 10:
        return f"{clean[:2]}XXXXXX{clean[-2:]}"
    return "XXXXXXXXXX"

CITY_ALIASES = {
    "bombay": "Mumbai",
    "mumbai": "Mumbai",
    "navi mumbai": "Navi Mumbai",
    "navimumbai": "Navi Mumbai",
    "bangalore": "Bengaluru",
    "bengaluru": "Bengaluru",
    "pune": "Pune",
    "nagpur": "Nagpur",
    "ahmedabad": "Ahmedabad",
    "hyderabad": "Hyderabad",
    "delhi": "Delhi",
    "nashik": "Nashik",
    "thane": "Thane",
}

def normalize_city(city_input: Optional[str]) -> Optional[str]:
    if not city_input:
        return None
    cleaned = city_input.strip().lower()
    return CITY_ALIASES.get(cleaned, city_input.strip().title())

GENDER_ALIASES = {
    "m": "Male",
    "male": "Male",
    "f": "Female",
    "female": "Female",
    "other": "Other",
    "non-binary": "Other",
}

def normalize_gender(gender_input: Optional[str]) -> Optional[str]:
    if not gender_input:
        return None
    cleaned = gender_input.strip().lower()
    return GENDER_ALIASES.get(cleaned, "Other")

SOURCE_ALIASES = {
    "insta": "Instagram",
    "ig": "Instagram",
    "instagram": "Instagram",
    "fb": "Facebook",
    "facebook": "Facebook",
    "website": "Website",
    "whatsapp mumbai": "WhatsApp Group - Mumbai",
    "wa grp mumbai": "WhatsApp Group - Mumbai",
    "whatsapp group - mumbai": "WhatsApp Group - Mumbai",
    "whatsapp group - pune": "WhatsApp Group - Pune",
    "staff dm - agent 01": "Staff DM - Agent 01",
    "staff dm - agent 02": "Staff DM - Agent 02",
    "referral": "Referral",
    "meta ads": "Meta Ads",
}

def normalize_source(source_input: Optional[str]) -> str:
    if not source_input:
        return "Website"
    cleaned = source_input.strip().lower()
    return SOURCE_ALIASES.get(cleaned, source_input.strip())

def normalize_income_range(income_input: Optional[str]) -> Optional[str]:
    """Map common assessment CSV income labels to the five canonical brackets."""
    if not income_input:
        return None
    cleaned = re.sub(r"\s+", "", income_input.strip().lower()).replace("₹", "").replace(",", "")
    aliases = {
        "below3l": "Below 3L", "below3lakhs": "Below 3L", "0-3l": "Below 3L", "0-3lakh": "Below 3L", "below300000": "Below 3L",
        "3l-6l": "3L-6L", "3-6l": "3L-6L", "3lakh-6lakh": "3L-6L", "300000-600000": "3L-6L",
        "6l-10l": "6L-10L", "6-10l": "6L-10L", "6lakh-10lakh": "6L-10L", "600000-1000000": "6L-10L",
        "10l-20l": "10L-20L", "10-20l": "10L-20L", "10lakh-20lakh": "10L-20L", "1000000-2000000": "10L-20L",
        "above20l": "Above 20L", "above20lakhs": "Above 20L", ">20l": "Above 20L", "above2000000": "Above 20L",
    }
    return aliases.get(cleaned)

DATE_FORMATS = [
    "%Y-%m-%d",
    "%d/%m/%Y",
    "%d-%m-%Y",
    "%d-%m-%y",
    "%d/%m/%y",
]

def parse_date(date_str: Optional[str]) -> Optional[date]:
    if not date_str or not str(date_str).strip():
        return None
    s = str(date_str).strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None

def calculate_age(dob: date, reference_date: Optional[date] = None) -> int:
    ref = reference_date or date.today()
    return ref.year - dob.year - ((ref.month, ref.day) < (dob.month, dob.day))

def calculate_next_eligible_date(completed_on: date) -> date:
    """Calculates 3-month cool-off date safe from leap-year and month-end drift."""
    return completed_on + relativedelta(months=+3) + relativedelta(days=+1)
