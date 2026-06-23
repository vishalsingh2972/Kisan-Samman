"""
search_schemes.py - Full-text search over scheme database.
"""
from __future__ import annotations
import json, logging, os
from pathlib import Path

logger = logging.getLogger(__name__)
_DB_PATH = Path(os.getenv("SCHEMES_DB_PATH", "./mcp/data/schemes.json"))
_CACHE = None

def _load_db() -> list:
    global _CACHE
    if _CACHE is not None: return _CACHE
    if not _DB_PATH.exists():
        logger.warning("schemes.json not found at %s", _DB_PATH)
        _CACHE = []
        return _CACHE
    with _DB_PATH.open("r", encoding="utf-8") as fh:
        _CACHE = json.load(fh)
    logger.info("Loaded %d schemes", len(_CACHE))
    return _CACHE

def _mock_results(query: str, state: str, crop_type: str) -> list:
    return [
        {"id":"PM-KISAN-001","name":"PM-KISAN","full_name":"Pradhan Mantri Kisan Samman Nidhi",
         "sponsor":"Central Government","description":"Rs.6000/year income support in 3 instalments.",
         "state":"ALL","crop_type":"ALL","benefit":"Rs.6000 per year","relevance_score":0.92,
         "requires_bank_account":True,"requires_aadhaar":True,"max_land_hectares":2.0},
        {"id":"MH-IRRIG-007","name":"Mukhyamantri Shetakari Yojana",
         "full_name":"Maharashtra Chief Minister Farmer Scheme","sponsor":"Maharashtra State Government",
         "description":"Subsidy up to Rs.50,000 for drip/sprinkler irrigation equipment.",
         "state":"Maharashtra","crop_type":"sugarcane","benefit":"Up to Rs.50,000 subsidy",
         "relevance_score":0.88,"requires_bank_account":True,"requires_aadhaar":True},
        {"id":"PM-FASAL-002","name":"PM Fasal Bima Yojana",
         "full_name":"Pradhan Mantri Fasal Bima Yojana","sponsor":"Central Government",
         "description":"Crop insurance covering losses due to natural calamities.",
         "state":"ALL","crop_type":"ALL","benefit":"Crop insurance at low premium",
         "relevance_score":0.75,"requires_bank_account":True,"requires_aadhaar":False},
        {"id":"KCC-003","name":"Kisan Credit Card","full_name":"Kisan Credit Card Scheme",
         "sponsor":"Central Government","description":"Short-term credit for crop cultivation needs.",
         "state":"ALL","crop_type":"ALL","benefit":"Credit up to Rs.3 lakh at 4% interest",
         "relevance_score":0.70,"requires_bank_account":True,"requires_aadhaar":True},
        {"id":"SOIL-HEALTH-004","name":"Soil Health Card","full_name":"Soil Health Card Scheme",
         "sponsor":"Central Government","description":"Free soil testing and crop-wise fertilizer advice.",
         "state":"ALL","crop_type":"ALL","benefit":"Free soil health card every 2 years",
         "relevance_score":0.60,"requires_bank_account":False,"requires_aadhaar":True},
        {"id":"PM-KUSUM-005","name":"PM KUSUM","full_name":"Pradhan Mantri Kisan Urja Suraksha evam Uttham Mahabhiyan",
         "sponsor":"Central Government","description":"Solar pump subsidy for irrigation.",
         "state":"ALL","crop_type":"ALL","benefit":"Up to 60% subsidy on solar pumps",
         "relevance_score":0.65,"requires_bank_account":True,"requires_aadhaar":True},
    ]

def search_schemes(query: str, state: str = "", crop_type: str = "") -> list:
    if os.getenv("MOCK_MCP", "false").lower() == "true":
        return _mock_results(query, state, crop_type)
    db = _load_db()
    if not db:
        logger.warning("DB empty, using mock results")
        return _mock_results(query, state, crop_type)
    query_lower = query.lower()
    results = []
    for scheme in db:
        searchable = " ".join([scheme.get("name",""), scheme.get("full_name",""),
                                scheme.get("description",""), scheme.get("keywords","")]).lower()
        if query_lower and query_lower not in searchable: continue
        s_state = scheme.get("state","ALL").upper()
        if state and s_state not in ("ALL", state.upper()): continue
        s_crop = scheme.get("crop_type","ALL").lower()
        if crop_type and s_crop not in ("all", crop_type.lower()): continue
        score = 0.5
        if query_lower in scheme.get("name","").lower(): score += 0.4
        if scheme.get("state","ALL").upper() == (state.upper() if state else "ALL"): score += 0.1
        scheme["relevance_score"] = round(score, 2)
        results.append(scheme)
    results.sort(key=lambda x: x.get("relevance_score",0), reverse=True)
    logger.info("search_schemes(%r,%r,%r) -> %d results", query, state, crop_type, len(results))
    return results