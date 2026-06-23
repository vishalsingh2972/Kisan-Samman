"""
test_agent.py — Integration tests for the ReAct agent loop.
Uses MOCK_MCP=true so no external API calls are made.
Requires a valid GROQ_API_KEY (or set MOCK_AGENT=true to skip).
"""
import os, sys, pytest
from pathlib import Path

os.environ["MOCK_MCP"]   = "true"
os.environ["MOCK_VOICE"] = "true"

sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.farmer_profile import sample_profile, FarmerProfile

SKIP_AGENT = os.getenv("MOCK_AGENT", "false").lower() == "true"


@pytest.mark.skipif(SKIP_AGENT, reason="MOCK_AGENT=true — skipping live agent calls")
class TestReActAgent:
    """Integration tests that call the live Groq API."""

    def test_agent_builds_without_error(self):
        from agent.react_agent import build_agent
        profile = sample_profile()
        executor = build_agent(profile)
        assert executor is not None

    def test_agent_returns_string(self):
        from agent.react_agent import build_agent
        profile = sample_profile()
        executor = build_agent(profile)
        result = executor.invoke({"input": "What irrigation subsidies am I eligible for?"})
        assert isinstance(result.get("output"), str)
        assert len(result["output"]) > 10

    def test_agent_handles_hindi_query(self):
        from agent.react_agent import build_agent
        profile = sample_profile()
        profile.language_code = "hi-IN"
        executor = build_agent(profile)
        result = executor.invoke({"input": "सिंचाई सब्सिडी के बारे में बताएं"})
        assert result.get("output")

    def test_agent_mentions_pm_kisan(self):
        from agent.react_agent import build_agent
        profile = sample_profile()
        executor = build_agent(profile)
        result = executor.invoke({"input": "income support schemes for small farmers"})
        output = result.get("output", "").lower()
        assert "kisan" in output or "6000" in output or "income" in output


class TestFarmerProfile:
    def test_sample_profile_valid(self):
        p = sample_profile()
        assert p.name == "Vishal Patil"
        assert p.land_hectares == 1.2
        assert p.caste_category == "OBC"

    def test_from_dict_roundtrip(self):
        p = sample_profile()
        d = p.to_dict()
        p2 = FarmerProfile.from_dict(d)
        assert p.name == p2.name
        assert p.land_hectares == p2.land_hectares

    def test_summary_string(self):
        p = sample_profile()
        s = p.summary()
        assert "Vishal" in s
        assert "Maharashtra" in s

    def test_save_and_load(self, tmp_path):
        p = sample_profile()
        path = tmp_path / "test_profile.json"
        p.save(path)
        p2 = FarmerProfile.from_json_file(path)
        assert p.name == p2.name
