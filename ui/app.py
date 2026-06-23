"""
app.py — Kisan Seva Flask web application.
Serves the UI and REST API endpoints for the React agent pipeline.

Run:
    MOCK_MCP=true MOCK_VOICE=true python app.py
    python app.py  (requires real API keys in .env)
"""
from __future__ import annotations
import base64, json, logging, os, sys
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger("kisan_seva.app")

# Insert both this file's directory AND its parent so imports work whether
# app.py lives at the project root OR inside a ui/ subfolder.
_here = Path(__file__).resolve().parent
sys.path.insert(0, str(_here))           # e.g. kisan-seva/ui/
sys.path.insert(0, str(_here.parent))    # e.g. kisan-seva/  (where agent/ lives)

# Also load .env from the project root (parent) if not found next to app.py
_root_env = _here.parent / ".env"
if not (_here / ".env").exists() and _root_env.exists():
    load_dotenv(_root_env)

from agent.farmer_profile import FarmerProfile, sample_profile
from agent.react_agent import run_pipeline
from location.maps import resolve_location, get_map_embed_url

# ── Flask app — static folder points to the static/ directory ────────────────
app = Flask(__name__, static_folder=str(_here.parent / "static"), static_url_path="/static")
CORS(app)

# ── In-memory profile store (replace with DB in production) ──────────────────
_current_profile: FarmerProfile = sample_profile()


# ── UI Route ──────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Serve the main UI from static/kisan_seva.html"""
    return send_from_directory(str(_here.parent / "static"), "kisan_seva.html")


# ── API Routes ────────────────────────────────────────────────────────────────

@app.route("/api/profile", methods=["GET"])
def get_profile():
    return jsonify(_current_profile.to_dict())


@app.route("/api/profile", methods=["POST"])
def update_profile():
    global _current_profile
    data = request.get_json(force=True)
    try:
        _current_profile = FarmerProfile.from_dict(data)
        return jsonify({"ok": True})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/api/geocode", methods=["POST"])
def geocode():
    data = request.get_json(force=True)
    query = data.get("query", "")
    if not query:
        return jsonify({"error": "No query"}), 400
    try:
        loc = resolve_location(query)
        return jsonify(loc)
    except Exception as exc:
        logger.error("Geocode error: %s", exc)
        return jsonify({"error": str(exc)}), 500


@app.route("/api/query/text", methods=["POST"])
def query_text():
    global _current_profile
    data = request.get_json(force=True)
    text = data.get("text", "").strip()
    language = data.get("language", _current_profile.language_code)
    profile_data = data.get("profile")

    if not text:
        return jsonify({"error": "No text provided"}), 400

    # Use submitted profile if provided
    if profile_data:
        try:
            _current_profile = FarmerProfile.from_dict(profile_data)
        except Exception:
            pass

    _current_profile.language_code = language

    try:
        result = run_pipeline(
            profile=_current_profile,
            query_text=text,
            language=language,
        )
        result = _enrich_with_app_links(result, _current_profile)
        return jsonify(result)
    except Exception as exc:
        logger.exception("Agent error")
        return jsonify({"error": f"Agent error: {exc}"}), 500


@app.route("/api/query/audio", methods=["POST"])
def query_audio():
    global _current_profile
    audio_file = request.files.get("audio")
    language = request.form.get("language", _current_profile.language_code)
    profile_json = request.form.get("profile")

    if not audio_file:
        return jsonify({"error": "No audio file provided"}), 400

    if profile_json:
        try:
            _current_profile = FarmerProfile.from_dict(json.loads(profile_json))
        except Exception:
            pass

    _current_profile.language_code = language
    audio_bytes = audio_file.read()
    mime_type = audio_file.content_type or "audio/webm"

    try:
        result = run_pipeline(
            profile=_current_profile,
            audio_bytes=audio_bytes,
            language=language,
        )
        result = _enrich_with_app_links(result, _current_profile)
        return jsonify(result)
    except Exception as exc:
        logger.exception("Audio agent error")
        return jsonify({"error": f"Agent error: {exc}"}), 500


def _enrich_with_app_links(result: dict, profile: "FarmerProfile") -> dict:
    """
    Fetch portal URLs + CSC for all eligible schemes and attach to result.
    Uses real lat/lng from profile for accurate CSC lookup.
    """
    from mcp.tools.fetch_app_link import fetch_app_link
    from location.maps import find_nearest_csc

    schemes = result.get("schemes", [])
    app_links = {}

    # Try to get a real CSC once using profile coordinates
    csc_info = None
    if profile.latitude and profile.longitude:
        try:
            csc_info = find_nearest_csc(
                lat=profile.latitude,
                lng=profile.longitude,
                district=profile.district,
            )
        except Exception as exc:
            logger.warning("CSC lookup failed: %s", exc)

    for s in schemes:
        sid = s.get("id", "")
        if not sid:
            continue
        try:
            link_data = fetch_app_link(scheme_id=sid, district=profile.district)
            # Override CSC with real GPS-based result if available
            if csc_info:
                link_data["csc_name"]        = csc_info.get("name",        link_data.get("csc_name", ""))
                link_data["csc_address"]     = csc_info.get("address",     link_data.get("csc_address", ""))
                link_data["csc_phone"]       = csc_info.get("phone",       link_data.get("csc_phone", ""))
                link_data["csc_distance_km"] = csc_info.get("distance_km")
            app_links[sid] = link_data
        except Exception as exc:
            logger.warning("fetch_app_link failed for %s: %s", sid, exc)

    result["app_links"] = app_links
    return result


@app.route("/api/scheme/link", methods=["POST"])
def scheme_link():
    """On-demand portal link fetch for a single scheme."""
    from mcp.tools.fetch_app_link import fetch_app_link
    data = request.get_json(force=True)
    scheme_id = data.get("scheme_id", "")
    district = data.get("district", _current_profile.district)
    if not scheme_id:
        return jsonify({"error": "scheme_id required"}), 400
    try:
        result = fetch_app_link(scheme_id=scheme_id, district=district)
        return jsonify(result)
    except Exception as exc:
        logger.error("scheme_link error: %s", exc)
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    port  = int(os.getenv("FLASK_PORT", 8000))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"

    # Sanity-check that the UI file exists before starting
    ui_path = _here / "static" / "kisan_seva.html"
    if not ui_path.exists():
        logger.warning(
            "UI file not found at %s — "
            "place kisan_seva.html inside the static/ folder.", ui_path
        )
    else:
        logger.info("UI file found: %s ✓", ui_path)

    logger.info("Starting Kisan Seva on http://localhost:%d", port)
    logger.info(
        "MOCK_MCP=%s  MOCK_VOICE=%s",
        os.getenv("MOCK_MCP", "false"),
        os.getenv("MOCK_VOICE", "false"),
    )
    app.run(host="0.0.0.0", port=port, debug=debug)