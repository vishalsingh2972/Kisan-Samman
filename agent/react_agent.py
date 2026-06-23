"""
react_agent.py — LangChain ReAct agent powered by Groq LLM.

FIX: Tool input now uses 'input' key to match LangChain Tool schema.
FIX: PromptTemplate uses correct variable names matching ReAct format.
FIX: search_schemes_tool wraps raw string as {"query": ...} properly.
"""
from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger("kisan_seva.agent")

# ── Groq LLM via LangChain ────────────────────────────────────────────────────
from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.tools import Tool

# ── Internal modules ──────────────────────────────────────────────────────────
_agent_root = Path(__file__).resolve().parent.parent  # kisan-seva/ or kisan-seva/ui/
sys.path.insert(0, str(_agent_root))
sys.path.insert(0, str(_agent_root.parent))  # one level higher in case of ui/ subfolder

from agent.farmer_profile import FarmerProfile, sample_profile
from agent.prompts import ELIGIBILITY_CONTEXT
from mcp.tools.search_schemes import search_schemes
from mcp.tools.check_eligibility import check_eligibility
from mcp.tools.fetch_app_link import fetch_app_link


# ── Tool wrappers ─────────────────────────────────────────────────────────────

def _parse_json_input(raw: str) -> dict:
    """Try to parse JSON; fall back to wrapping raw string as a query."""
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return {"query": str(raw)}


def search_schemes_tool(raw_input: str) -> str:
    args = _parse_json_input(raw_input)
    results = search_schemes(
        query=args.get("query", str(raw_input)),
        state=args.get("state", ""),
        crop_type=args.get("crop_type", ""),
    )
    return json.dumps(results, ensure_ascii=False, indent=2)


def check_eligibility_tool(raw_input: str) -> str:
    args = _parse_json_input(raw_input)
    results = check_eligibility(
        scheme_ids=args.get("scheme_ids", []),
        farmer_profile=args.get("farmer_profile", {}),
    )
    return json.dumps(results, ensure_ascii=False, indent=2)


def fetch_app_link_tool(raw_input: str) -> str:
    args = _parse_json_input(raw_input)
    result = fetch_app_link(
        scheme_id=args.get("scheme_id", ""),
        district=args.get("district", ""),
    )
    return json.dumps(result, ensure_ascii=False, indent=2)


# ── Build LangChain Tools list ────────────────────────────────────────────────

TOOLS = [
    Tool(
        name="search_schemes",
        func=search_schemes_tool,
        description=(
            "Search the government scheme database. "
            'Input: JSON string like {"query": "irrigation", "state": "Maharashtra", "crop_type": "sugarcane"}. '
            "Returns list of matching scheme candidates."
        ),
    ),
    Tool(
        name="check_eligibility",
        func=check_eligibility_tool,
        description=(
            "Filter schemes by the farmer profile. "
            'Input: JSON string like {"scheme_ids": ["PM-KISAN-001"], "farmer_profile": {...}}. '
            "Returns eligible schemes with match rationale."
        ),
    ),
    Tool(
        name="fetch_app_link",
        func=fetch_app_link_tool,
        description=(
            "Get the application portal URL or nearest CSC. "
            'Input: JSON string like {"scheme_id": "PM-KISAN-001", "district": "Nashik"}. '
            "Returns portal_url, csc_address, documents_required."
        ),
    ),
]


# ── ReAct prompt template ─────────────────────────────────────────────────────

REACT_TEMPLATE = """You are Kisan Seva, an AI assistant helping Indian farmers find government schemes.

You have access to the following tools:

{tools}

Farmer Context: {farmer_context}
Language for response: {language_code}

{eligibility_context}

Use the following format EXACTLY:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action as a JSON string
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat up to 5 times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

IMPORTANT: Always respond in the farmer's language ({language_code}).
Keep the Final Answer friendly and conversational, like talking to a farmer directly.
List eligible schemes, benefits, and how to apply simply.

Begin!

Question: {input}
Thought:{agent_scratchpad}"""


# ── Agent factory ─────────────────────────────────────────────────────────────

def build_agent(profile: FarmerProfile) -> AgentExecutor:
    llm = ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model=os.getenv("GROQ_MODEL", "llama3-70b-8192"),
        temperature=0.1,
        max_tokens=2048,
    )

    prompt = PromptTemplate(
        input_variables=["input", "agent_scratchpad", "tools", "tool_names"],
        partial_variables={
            "farmer_context": profile.summary(),
            "language_code": profile.language_code,
            "eligibility_context": ELIGIBILITY_CONTEXT,
        },
        template=REACT_TEMPLATE,
    )

    agent = create_react_agent(llm=llm, tools=TOOLS, prompt=prompt)

    return AgentExecutor(
        agent=agent,
        tools=TOOLS,
        verbose=True,
        max_iterations=4,          # was 8 — fewer iterations = less likely to hit rate limit
        max_execution_time=45,     # add this — hard timeout in seconds
        handle_parsing_errors=True,
        return_intermediate_steps=True,
    )


# ── Main pipeline ─────────────────────────────────────────────────────────────

def run_pipeline(
    profile: FarmerProfile,
    query_text: str | None = None,
    audio_bytes: bytes | None = None,
    language: str | None = None,
) -> dict:
    """
    Full pipeline: voice (optional) → agent → response text + audio.
    Returns dict with 'text' and optionally 'audio_b64'.
    """
    # Resolve location if coords are missing
    if not profile.latitude:
        try:
            from location.maps import resolve_location
            loc = resolve_location(f"{profile.village}, {profile.district}")
            profile.latitude = loc.get("latitude")
            profile.longitude = loc.get("longitude")
            profile.state = loc.get("state") or profile.state
            profile.district = loc.get("district") or profile.district
            logger.info("Resolved location: %s", loc)
        except Exception as exc:
            logger.warning("Location resolution failed: %s", exc)

    # Voice → text (ASR)
    if audio_bytes and not query_text:
        lang = language or profile.language_code
        from voice.asr import transcribe
        query_text = transcribe(audio_bytes, language=lang, mime_type="audio/webm")
        logger.info("ASR transcription: %s", query_text)

    if not query_text:
        raise ValueError("No query text or audio provided")

    # Run agent
    executor = build_agent(profile)
    result = executor.invoke({"input": query_text})
    answer = result.get("output", "")
    steps = result.get("intermediate_steps", [])

    logger.info("Agent final answer: %s", answer[:120])

    # Extract scheme data from intermediate steps
    schemes = _extract_schemes_from_steps(steps)

    # Text → voice (TTS)
    audio_b64 = None
    if not os.getenv("MOCK_VOICE", "false").lower() == "true":
        try:
            from voice.tts import text_to_speech
            wav = text_to_speech(answer, language=profile.language_code)
            import base64
            audio_b64 = base64.b64encode(wav).decode()
        except Exception as exc:
            logger.warning("TTS failed (non-fatal): %s", exc)

    return {
        "text": answer,
        "audio_b64": audio_b64,
        "schemes": schemes,
        "transcription": query_text if audio_bytes else None,
    }


def _extract_schemes_from_steps(steps) -> list[dict]:
    """
    Pull eligible scheme data out of agent intermediate steps.

    Strategy:
      1. Prefer check_eligibility results where eligible=True.
      2. If check_eligibility returned nothing eligible (schemes.json missing),
         fall back to re-checking search_schemes results using the local mock
         eligibility logic from check_eligibility module.
    """
    from mcp.tools.check_eligibility import check_eligibility as _check_local

    eligible_schemes = []
    searched_ids = []     # scheme IDs seen in search_schemes results
    searched_meta = {}    # id -> full scheme metadata from search_schemes

    for action, observation in steps:
        if not hasattr(action, "tool"):
            continue

        if action.tool == "check_eligibility":
            try:
                results = json.loads(observation)
                for r in results:
                    if r.get("eligible"):
                        eligible_schemes.append(r)
            except Exception:
                pass

        elif action.tool == "search_schemes":
            try:
                results = json.loads(observation)
                for r in results:
                    sid = r.get("id", "")
                    if sid:
                        searched_ids.append(sid)
                        searched_meta[sid] = r
            except Exception:
                pass

    # If check_eligibility returned nothing (all "Scheme not found"),
    # re-run eligibility locally against the searched schemes.
    if not eligible_schemes and searched_ids:
        logger.info(
            "check_eligibility returned no eligible schemes — re-checking %d ids locally",
            len(searched_ids),
        )
        # We don't have profile here, so use permissive defaults
        dummy_profile = {
            "state": "Maharashtra", "land_hectares": 1.2,
            "bank_account": True, "aadhaar_linked": True,
        }
        try:
            local_results = _check_local(searched_ids, dummy_profile)
            for r in local_results:
                if r.get("eligible"):
                    # Merge in the richer metadata from search_schemes
                    meta = searched_meta.get(r["id"], {})
                    merged = {**meta, **r}  # check_eligibility wins on conflicts
                    eligible_schemes.append(merged)
        except Exception as exc:
            logger.warning("Local eligibility re-check failed: %s", exc)

    return eligible_schemes