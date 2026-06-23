# Kisan Seva — Quick Start

## 1. Install dependencies
```bash
pip install -r requirements.txt
```

## 2. Configure environment
```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY (and optionally SARVAM + GOOGLE_MAPS keys)
```

## 3. Run with mock mode (no API keys needed except Groq)
```bash
MOCK_MCP=true MOCK_VOICE=true python agent/react_agent.py \
  --text "irrigation subsidy for small farmer" \
  --profile profiles/sample_farmer.json
```

## 4. Run MCP server
```bash
python mcp/server.py
```

## 5. Run tests
```bash
# Unit tests — no API keys needed
pytest tests/test_mcp_tools.py -v

# Agent integration tests (needs GROQ_API_KEY)
MOCK_MCP=true pytest tests/test_agent.py -v

# Full voice round-trip (needs SARVAM_API_KEY)
pytest tests/test_voice.py -v
```

## 6. Full pipeline with voice
```bash
python agent/react_agent.py \
  --audio farmer_query.wav \
  --language mr-IN \
  --profile profiles/sample_farmer.json
```
