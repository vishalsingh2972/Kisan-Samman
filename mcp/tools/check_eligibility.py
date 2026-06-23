"""
check_eligibility.py — Checks which schemes a farmer is eligible for.

FIX: Added mock fallback (same pattern as search_schemes) so it works
     even when schemes.json is missing — mirrors the mock data from search_schemes.
"""
from __future__ import annotations
import json, logging, os
from pathlib import Path

logger = logging.getLogger(__name__)

# ── Mock eligibility data (mirrors mock data in search_schemes.py) ─────────────
# Used when MOCK_MCP=true OR when schemes.json is missing
_MOCK_ELIGIBILITY = {
    "PM-KISAN-001": {
        "name": "PM-KISAN",
        "sponsor": "Central Government",
        "check": lambda p: (
            p.get("bank_account", p.get("bank_account", True)) and
            p.get("aadhaar_linked", True) and
            float(p.get("land_hectares", p.get("land_size", 0))) <= 2.0
        ),
        "benefit": "Rs.6000 per year (3 instalments of Rs.2000)",
        "rationale_ok": "Small/marginal farmer with Aadhaar-linked bank account — fully eligible.",
        "rationale_fail": "Either land exceeds 2ha, bank account missing, or Aadhaar not linked.",
    },
    "MH-IRRIG-007": {
        "name": "Mukhyamantri Shetakari Yojana",
        "sponsor": "Maharashtra State Government",
        "check": lambda p: (
            p.get("state", "").lower() in ("maharashtra", "mh") and
            p.get("bank_account", True) and
            p.get("aadhaar_linked", True)
        ),
        "benefit": "Up to Rs.50,000 subsidy on drip/sprinkler irrigation",
        "rationale_ok": "Maharashtra farmer with valid bank account and Aadhaar — eligible for irrigation subsidy.",
        "rationale_fail": "Scheme is Maharashtra-specific. Verify state, bank account and Aadhaar.",
    },
    "PM-FASAL-002": {
        "name": "PM Fasal Bima Yojana",
        "sponsor": "Central Government",
        "check": lambda p: p.get("bank_account", True),
        "benefit": "Crop insurance at low premium against natural calamities",
        "rationale_ok": "Bank account present — eligible for crop insurance.",
        "rationale_fail": "Bank account required for premium payment.",
    },
    "KCC-003": {
        "name": "Kisan Credit Card",
        "sponsor": "Central Government",
        "check": lambda p: (
            p.get("bank_account", True) and
            p.get("aadhaar_linked", True)
        ),
        "benefit": "Credit up to Rs.3 lakh at 4% interest for crop cultivation",
        "rationale_ok": "Bank account and Aadhaar linked — eligible for Kisan Credit Card.",
        "rationale_fail": "Bank account and Aadhaar linkage both required.",
    },
    "SOIL-HEALTH-004": {
        "name": "Soil Health Card",
        "sponsor": "Central Government",
        "check": lambda p: p.get("aadhaar_linked", True),
        "benefit": "Free soil health card and fertilizer advice every 2 years",
        "rationale_ok": "Aadhaar linked — eligible for free soil testing.",
        "rationale_fail": "Aadhaar required for soil health card.",
    },
    "PM-KUSUM-005": {
        "name": "PM KUSUM",
        "sponsor": "Central Government",
        "check": lambda p: (
            p.get("bank_account", True) and
            p.get("aadhaar_linked", True)
        ),
        "benefit": "Up to 60% subsidy on solar irrigation pumps",
        "rationale_ok": "Bank account and Aadhaar present — eligible for solar pump subsidy.",
        "rationale_fail": "Bank account and Aadhaar both required.",
    },
}


def _load_schemes_db() -> dict:
    """Load schemes.json if it exists; return empty dict otherwise."""
    db_path = os.getenv(
        "SCHEMES_DB_PATH",
        str(Path(__file__).parent.parent / "mcp" / "data" / "schemes.json"),
    )
    p = Path(db_path)
    if not p.exists():
        logger.warning("schemes.json not found at %s", db_path)
        return {}
    try:
        with p.open("r", encoding="utf-8") as fh:
            schemes = json.load(fh)
        return {s["id"]: s for s in schemes if "id" in s}
    except Exception as exc:
        logger.error("Failed to load schemes.json: %s", exc)
        return {}


def check_eligibility(scheme_ids: list, farmer_profile: dict) -> list:
    """
    Check which of the given scheme_ids the farmer is eligible for.

    Precedence:
      1. Real schemes.json if present
      2. Mock eligibility data (always available as fallback)
    """
    use_mock = os.getenv("MOCK_MCP", "false").lower() == "true"

    # Try loading real DB
    schemes_db = {} if use_mock else _load_schemes_db()

    results = []
    for sid in scheme_ids:
        # ── Real DB path ───────────────────────────────────────────────────────
        if sid in schemes_db:
            scheme = schemes_db[sid]
            eligible, rationale, confidence = _check_real(scheme, farmer_profile)
            results.append({
                "id": sid,
                "name": scheme.get("name", sid),
                "sponsor": scheme.get("sponsor", ""),
                "eligible": eligible,
                "benefit": scheme.get("benefit", ""),
                "rationale": rationale,
                "confidence": confidence,
            })
            continue

        # ── Mock / fallback path ───────────────────────────────────────────────
        if sid in _MOCK_ELIGIBILITY:
            mock = _MOCK_ELIGIBILITY[sid]
            try:
                eligible = bool(mock["check"](farmer_profile))
            except Exception:
                eligible = True  # default to eligible on error

            results.append({
                "id": sid,
                "name": mock["name"],
                "sponsor": mock["sponsor"],
                "eligible": eligible,
                "benefit": mock["benefit"],
                "rationale": mock["rationale_ok"] if eligible else mock["rationale_fail"],
                "confidence": 0.92 if eligible else 0.4,
            })
            continue

        # ── Unknown scheme ─────────────────────────────────────────────────────
        logger.warning("Unknown scheme id: %s", sid)
        results.append({
            "id": sid,
            "name": sid,
            "sponsor": "",
            "eligible": False,
            "benefit": "",
            "rationale": "Scheme not found in database.",
            "confidence": 0.0,
        })

    return results


def _check_real(scheme: dict, profile: dict) -> tuple[bool, str, float]:
    """Run eligibility rules against a real scheme record."""
    reasons = []
    eligible = True

    # Land size check
    max_land = scheme.get("max_land_hectares")
    if max_land is not None:
        land = float(profile.get("land_hectares", profile.get("land_size", 0)))
        if land > max_land:
            eligible = False
            reasons.append(f"Land {land}ha exceeds limit of {max_land}ha")

    # State check
    scheme_state = scheme.get("state", "ALL")
    if scheme_state not in ("ALL", "", None):
        farmer_state = profile.get("state", "")
        if farmer_state.lower() != scheme_state.lower():
            eligible = False
            reasons.append(f"Scheme is {scheme_state}-specific")

    # Bank account
    if scheme.get("requires_bank_account") and not profile.get("bank_account", True):
        eligible = False
        reasons.append("Bank account required")

    # Aadhaar
    if scheme.get("requires_aadhaar") and not profile.get("aadhaar_linked", True):
        eligible = False
        reasons.append("Aadhaar linkage required")

    rationale = "Eligible — all criteria met." if eligible else "Not eligible: " + "; ".join(reasons)
    confidence = 0.92 if eligible else 0.5
    return eligible, rationale, confidence