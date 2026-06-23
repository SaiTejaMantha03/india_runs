from datetime import date, datetime

REFERENCE_DATE = date(2026, 6, 20) 


PREFERRED_LOCATIONS = {"pune", "noida", "hyderabad", "mumbai", "delhi", "delhi ncr", "gurgaon", "gurugram"}


def _parse_date(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()


def recency_multiplier(last_active_date: str) -> float:
    try:
        last_active = _parse_date(last_active_date)
    except (ValueError, TypeError):
        return 0.85  
    days_inactive = (REFERENCE_DATE - last_active).days
    if days_inactive < 0:
        days_inactive = 0  

    if days_inactive <= 30:
        return 1.0
    elif days_inactive <= 60:
        return 0.92
    elif days_inactive <= 120:
        return 0.78
    elif days_inactive <= 180:  
        return 0.55
    elif days_inactive <= 270:
        return 0.35
    else:
        return 0.18


def responsiveness_multiplier(recruiter_response_rate: float) -> float:
    r = recruiter_response_rate
    if r >= 0.6:
        return 1.0
    elif r >= 0.4:
        return 0.92
    elif r >= 0.2:
        return 0.75
    elif r >= 0.1:
        return 0.55
    else:
        return 0.35  

def open_to_work_multiplier(open_to_work_flag: bool) -> float:

    return 1.0 if open_to_work_flag else 0.8


def notice_period_multiplier(notice_period_days: int) -> float:
    if notice_period_days <= 30:
        return 1.0
    elif notice_period_days <= 60:
        return 0.93
    elif notice_period_days <= 90:
        return 0.85
    else:
        return 0.75


def interview_reliability_multiplier(interview_completion_rate: float, offer_acceptance_rate: float) -> float:
    mult = 1.0
    if interview_completion_rate < 0.5:
        mult *= 0.7
    elif interview_completion_rate < 0.75:
        mult *= 0.9

    if offer_acceptance_rate >= 0:  
        if offer_acceptance_rate < 0.2:
            mult *= 0.85
    return mult


def location_multiplier(location: str, country: str, willing_to_relocate: bool) -> float:
    if country.strip().lower() != "india":

        return 0.25

    loc_lower = location.lower()
    is_preferred_city = any(city in loc_lower for city in PREFERRED_LOCATIONS)

    if is_preferred_city:
        return 1.0
    if willing_to_relocate:
        return 0.9
    return 0.65  

def compute_availability_multiplier(candidate: dict) -> tuple[float, list[str]]:
    sig = candidate["redrob_signals"]
    profile = candidate["profile"]

    flags = []
    mult = 1.0

    m = recency_multiplier(sig["last_active_date"])
    mult *= m
    if m <= 0.55:
        flags.append("inactive_recently")

    m = responsiveness_multiplier(sig["recruiter_response_rate"])
    mult *= m
    if m <= 0.55:
        flags.append("low_recruiter_response_rate")

    m = open_to_work_multiplier(sig["open_to_work_flag"])
    mult *= m
    if m < 1.0:
        flags.append("not_marked_open_to_work")

    m = notice_period_multiplier(sig["notice_period_days"])
    mult *= m
    if m <= 0.85:
        flags.append("long_notice_period")

    m = interview_reliability_multiplier(sig["interview_completion_rate"], sig["offer_acceptance_rate"])
    mult *= m
    if m < 0.85:
        flags.append("interview_or_offer_reliability_concern")

    m = location_multiplier(profile["location"], profile["country"], sig["willing_to_relocate"])
    mult *= m
    if m < 0.7:
        flags.append("location_logistics_concern")

    return mult, flags
