"""
test_mcp_tools.py — Unit tests for all three MCP tools.
Runs entirely in MOCK mode — no API keys required.
"""
import os, sys, json, pytest
from pathlib import Path

# Mock flags
os.environ["MOCK_MCP"]   = "true"
os.environ["MOCK_VOICE"] = "true"
os.environ["SCHEMES_DB_PATH"] = str(Path(__file__).parent.parent / "mcp/data/schemes.json")

sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.tools.search_schemes import search_schemes
from mcp.tools.check_eligibility import check_eligibility
from mcp.tools.fetch_app_link import fetch_app_link


class TestSearchSchemes:
    def test_returns_list(self):
        results = search_schemes(query="irrigation", state="Maharashtra", crop_type="sugarcane")
        assert isinstance(results, list)
        assert len(results) > 0

    def test_result_has_required_keys(self):
        results = search_schemes(query="PM KISAN", state="", crop_type="")
        for r in results:
            assert "id" in r
            assert "name" in r
            assert "description" in r

    def test_relevance_score_present(self):
        results = search_schemes(query="subsidy", state="Maharashtra")
        for r in results:
            assert "relevance_score" in r
            assert 0.0 <= r["relevance_score"] <= 1.0

    def test_empty_query_returns_results(self):
        results = search_schemes(query="")
        assert isinstance(results, list)


class TestCheckEligibility:
    def test_pm_kisan_eligible(self):
        profile = {
            "state": "Maharashtra", "land_hectares": 1.2,
            "caste_category": "OBC", "bank_account": True, "aadhaar_linked": True,
        }
        results = check_eligibility(["PM-KISAN-001"], profile)
        assert len(results) == 1
        assert results[0]["eligible"] is True

    def test_irrigation_scheme_eligible_for_mh(self):
        profile = {
            "state": "Maharashtra", "land_hectares": 1.2,
            "caste_category": "OBC", "bank_account": True, "aadhaar_linked": True,
        }
        results = check_eligibility(["MH-IRRIG-007"], profile)
        assert any(r["id"] == "MH-IRRIG-007" and r["eligible"] for r in results)

    def test_multiple_scheme_ids(self):
        profile = {
            "state": "Maharashtra", "land_hectares": 1.5,
            "caste_category": "OBC", "bank_account": True, "aadhaar_linked": True,
        }
        results = check_eligibility(["PM-KISAN-001", "MH-IRRIG-007", "PM-FASAL-002"], profile)
        assert len(results) == 3

    def test_result_structure(self):
        profile = {"state": "Maharashtra", "land_hectares": 1.0,
                   "caste_category": "GEN", "bank_account": True, "aadhaar_linked": True}
        results = check_eligibility(["PM-KISAN-001"], profile)
        r = results[0]
        assert "eligible" in r
        assert "rationale" in r
        assert "benefit" in r
        assert "confidence" in r


class TestFetchAppLink:
    def test_returns_portal_url(self):
        result = fetch_app_link("PM-KISAN-001", district="Nashik")
        assert "portal_url" in result
        assert result["portal_url"].startswith("http")

    def test_returns_documents(self):
        result = fetch_app_link("PM-KISAN-001", district="Nashik")
        assert "documents_required" in result
        assert isinstance(result["documents_required"], list)
        assert len(result["documents_required"]) > 0

    def test_returns_csc_info(self):
        result = fetch_app_link("MH-IRRIG-007", district="Nashik")
        assert "csc_address" in result
        assert "csc_phone" in result

    def test_unknown_scheme_id_gets_default(self):
        result = fetch_app_link("UNKNOWN-999", district="Pune")
        assert "portal_url" in result
        assert "documents_required" in result
