"""
fetch_app_link.py — Returns the official application URL or nearest CSC address.
"""
from __future__ import annotations
import logging, os

logger = logging.getLogger(__name__)

_PORTAL_MAP = {
    "PM-KISAN-001":  "https://pmkisan.gov.in/",
    "MH-IRRIG-007":  "https://mahadbt.maharashtra.gov.in/",
    "PM-FASAL-002":  "https://pmfby.gov.in/",
    "KCC-003":       "https://www.pmkisan.gov.in/kcc.aspx",
    "SOIL-HEALTH-004": "https://soilhealth.dac.gov.in/",
    "PM-KUSUM-005":  "https://pmkusum.mnre.gov.in/",
}

_DOCS_MAP = {
    "PM-KISAN-001": ["Aadhaar card", "Bank passbook", "Land records (7/12 extract)"],
    "MH-IRRIG-007": ["Aadhaar card", "Bank passbook", "Land records", "Quotation from supplier"],
    "PM-FASAL-002": ["Aadhaar card", "Bank passbook", "Sowing certificate from Patwari"],
    "KCC-003":       ["Aadhaar card", "PAN card", "Land records", "2 passport photos"],
    "SOIL-HEALTH-004": ["Aadhaar card", "Land records"],
    "PM-KUSUM-005": ["Aadhaar card", "Land records", "Bank passbook", "Electricity connection proof"],
}


def _mock_csc(district: str) -> dict:
    return {
        "name": f"{district} Common Service Centre",
        "address": f"Near Collector Office, {district}",
        "distance_km": 3.2,
        "phone": "1800-XXX-XXXX",
    }


def fetch_app_link(scheme_id: str, district: str = "") -> dict:
    """
    Returns application portal URL, nearest CSC, and required documents.

    Args:
        scheme_id: e.g. "PM-KISAN-001"
        district:  Farmer's district for CSC lookup

    Returns:
        {
          portal_url: str,
          csc_address: str,
          csc_phone: str,
          documents_required: list[str],
          notes: str,
        }
    """
    portal_url = _PORTAL_MAP.get(scheme_id, "https://india.gov.in/topics/agriculture")
    documents  = _DOCS_MAP.get(scheme_id, ["Aadhaar card", "Bank passbook", "Land records"])

    if district and not os.getenv("MOCK_MCP", "false").lower() == "true":
        # In production: call Google Maps Places API via location.maps
        try:
            from location.maps import find_nearest_csc
            # Use placeholder coords — real lookup happens from profile
            csc = find_nearest_csc(lat=0.0, lng=0.0, district=district)
        except Exception as exc:
            logger.warning("CSC lookup failed: %s", exc)
            csc = _mock_csc(district)
    else:
        csc = _mock_csc(district or "your district")

    result = {
        "portal_url": portal_url,
        "csc_name": csc.get("name", ""),
        "csc_address": csc.get("address", ""),
        "csc_phone": csc.get("phone", "1800-115-526"),
        "csc_distance_km": csc.get("distance_km"),
        "documents_required": documents,
        "notes": (
            "You can apply online at the portal URL above, or visit your nearest "
            "Common Service Centre (CSC) for offline assistance."
        ),
    }
    logger.info("fetch_app_link(%r, %r) → %r", scheme_id, district, portal_url)
    return result
