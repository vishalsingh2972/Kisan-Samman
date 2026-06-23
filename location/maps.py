"""
maps.py - Location services using free OpenStreetMap APIs.
No API key needed. Nominatim for geocoding, Overpass for CSC lookup.
"""
from __future__ import annotations
import logging, math, time, os
import requests

logger = logging.getLogger(__name__)

NOMINATIM_BASE = "https://nominatim.openstreetmap.org"
OVERPASS_BASE  = "https://overpass-api.de/api/interpreter"
USER_AGENT = os.getenv("NOMINATIM_USER_AGENT", "KisanSamman/1.0 (contact@kisansamman.in)")
_HEADERS = {"User-Agent": USER_AGENT, "Accept-Language": "en"}
_last_nominatim_call: float = 0.0

def _rate_limit():
    global _last_nominatim_call
    elapsed = time.time() - _last_nominatim_call
    if elapsed < 1.1:
        time.sleep(1.1 - elapsed)
    _last_nominatim_call = time.time()

def _addr(address: dict, *keys: str) -> str:
    for key in keys:
        val = address.get(key, "")
        if val: return val
    return ""

def resolve_location(query: str) -> dict:
    """Village/address string -> state, district, coords."""
    _rate_limit()
    params = {"q": query, "format": "json", "addressdetails": 1, "limit": 1,
              "countrycodes": "in", "accept-language": "en"}
    try:
        resp = requests.get(f"{NOMINATIM_BASE}/search", params=params, headers=_HEADERS, timeout=10)
        resp.raise_for_status()
        results = resp.json()
    except Exception as exc:
        logger.error("Nominatim search failed: %s", exc)
        return _stub_location(query)
    if not results:
        return _stub_location(query)
    hit = results[0]
    addr = hit.get("address", {})
    return {
        "state":     _addr(addr, "state"),
        "district":  _addr(addr, "district", "county", "state_district"),
        "taluka":    _addr(addr, "village", "suburb", "town"),
        "latitude":  float(hit.get("lat", 0)),
        "longitude": float(hit.get("lon", 0)),
        "formatted": hit.get("display_name", ""),
    }

def _stub_location(query: str) -> dict:
    return {"state":"","district":"","taluka":"","latitude":None,"longitude":None,"formatted":query}

def reverse_geocode(lat: float, lng: float) -> dict:
    _rate_limit()
    try:
        resp = requests.get(f"{NOMINATIM_BASE}/reverse", params={
            "lat":lat,"lon":lng,"format":"json","addressdetails":1,"zoom":10,"accept-language":"en"
        }, headers=_HEADERS, timeout=10)
        resp.raise_for_status()
        result = resp.json()
    except Exception as exc:
        logger.error("Nominatim reverse failed: %s", exc)
        return _stub_location(f"{lat},{lng}")
    addr = result.get("address", {})
    return {
        "state":     _addr(addr, "state"),
        "district":  _addr(addr, "district", "county", "state_district"),
        "taluka":    _addr(addr, "village", "suburb", "town"),
        "latitude":  lat, "longitude": lng,
        "formatted": result.get("display_name", ""),
    }

def find_nearest_csc(lat: float, lng: float, district: str = "") -> dict:
    """Find nearest Common Service Centre via Overpass API."""
    if not lat or not lng or (lat == 0.0 and lng == 0.0):
        return _stub_csc(district)
    template = """[out:json][timeout:15];(
  node["amenity"="government"]["name"~"Common Service|CSC|Samman Kendra|Jan Samman",i](around:{r},{lat},{lon});
  node["office"="government"]["name"~"Common Service|CSC|Samman Kendra",i](around:{r},{lat},{lon});
);out body;"""
    for radius in (5000, 15000, 30000):
        try:
            resp = requests.post(OVERPASS_BASE, data={"data": template.format(r=radius, lat=lat, lon=lng)},
                                 headers={"User-Agent": USER_AGENT}, timeout=20)
            resp.raise_for_status()
            elements = resp.json().get("elements", [])
        except Exception as exc:
            logger.warning("Overpass failed: %s", exc)
            return _stub_csc(district)
        if elements:
            def _dist(el):
                dlat = math.radians(el["lat"] - lat)
                dlng = math.radians(el["lon"] - lng)
                a = math.sin(dlat/2)**2 + math.cos(math.radians(lat))*math.cos(math.radians(el["lat"]))*math.sin(dlng/2)**2
                return 6371 * 2 * math.asin(math.sqrt(a))
            nearest = min(elements, key=_dist)
            tags = nearest.get("tags", {})
            name = tags.get("name") or "Common Service Centre"
            parts = [tags.get("addr:street",""), tags.get("addr:village","") or tags.get("addr:city",""),
                     tags.get("addr:district", district), tags.get("addr:state","")]
            return {"name": name, "address": ", ".join(p for p in parts if p) or f"Near {district}",
                    "distance_km": round(_dist(nearest), 1), "phone": tags.get("phone","1800-115-526")}
    return _stub_csc(district)

def _stub_csc(district: str) -> dict:
    return {"name": f"{district} Common Service Centre" if district else "Common Service Centre",
            "address": f"Visit the District Collector Office in {district or 'your district'}.",
            "distance_km": None, "phone": "1800-115-526"}

def get_map_embed_url(lat: float, lng: float, zoom: int = 13) -> str:
    if not lat or not lng: return ""
    delta = 0.03
    bbox = f"{lng-delta},{lat-delta},{lng+delta},{lat+delta}"
    return f"https://www.openstreetmap.org/export/embed.html?bbox={bbox}&layer=mapnik&marker={lat},{lng}"