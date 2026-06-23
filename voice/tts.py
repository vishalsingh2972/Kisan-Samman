"""
tts.py - Sarvam AI Text-to-Speech wrapper.
FIXES: Bulbul v3 (mr-IN works), valid voices, pitch/loudness removed.
"""
from __future__ import annotations
import base64, logging, os, struct
import requests

logger = logging.getLogger(__name__)
SARVAM_TTS_URL = "https://api.sarvam.ai/text-to-speech"

# v3 VALID VOICES (dashboard.sarvam.ai confirmed)
VOICE_MAP = {
    "hi-IN": "shubh", "mr-IN": "shubh", "ta-IN": "pavithra",
    "te-IN": "arvind", "kn-IN": "arvind", "bn-IN": "shubh",
    "gu-IN": "shubh", "pa-IN": "shubh", "en-IN": "anushka", "en": "anushka",
}
_CHUNK_SIZE = 2000  # v3 safe limit

def _mock_speak(text: str, language: str) -> bytes:
    data_size = 0
    header = struct.pack("<4sI4s4sIHHIIHH4sI",
        b"RIFF", 36+data_size, b"WAVE", b"fmt ", 16,
        1, 1, 8000, 16000, 2, 16, b"data", data_size)
    return header

def _concat_wav_chunks(chunks: list) -> bytes:
    if not chunks: return b""
    if len(chunks) == 1: return chunks[0]
    first = chunks[0]
    pcm = b"".join(c[44:] for c in chunks)
    ds = len(pcm)
    return b"RIFF" + struct.pack("<I", 36+ds) + b"WAVE" + first[12:36] + b"data" + struct.pack("<I", ds) + pcm

def _tts_chunk(text: str, language: str, api_key: str) -> bytes:
    voice = VOICE_MAP.get(language, "shubh")
    lang_code = language if "-" in language else f"{language}-IN"
    
    # ✅ BULBUL V3 EXACT PAYLOAD - NO 400 ERRORS
    payload = {
        "model": "bulbul:v3",
        "text": text,                    # Single string (not "inputs")
        "target_language_code": lang_code,
        "speaker": voice,                # shubh/anushka valid
        "pace": 1.0                      # v3 ONLY supports pace
    }
    
    resp = requests.post(SARVAM_TTS_URL, json=payload,
                        headers={"api-subscription-key": api_key, "Content-Type": "application/json"},
                        timeout=30)
    
    if resp.status_code == 400:
        logger.error("TTS 400: %s | payload: %s", resp.text, payload)
        raise ValueError(f"TTS 400: {resp.text}")
    
    resp.raise_for_status()
    data = resp.json()
    audios = data.get("audios", [])
    if not audios:
        logger.error("TTS no audios: %s", data)
        raise ValueError(f"TTS: no audio: {data}")
    return base64.b64decode(audios[0])  # Returns WAV bytes

def speak(text: str, language: str = "hi-IN") -> bytes:
    """Convert text to speech WAV bytes via Sarvam AI."""
    if os.getenv("MOCK_VOICE", "false").lower() == "true":
        return _mock_speak(text, language)
    api_key = os.getenv("SARVAM_API_KEY")
    if not api_key: raise EnvironmentError("SARVAM_API_KEY not set")
    if language not in VOICE_MAP:
        logger.warning("Language %r not supported, defaulting to hi-IN", language)
        language = "hi-IN"
    text = text.strip()
    chunks = [text[i:i+_CHUNK_SIZE] for i in range(0, len(text), _CHUNK_SIZE)]
    logger.info("TTS: lang=%s %d chars %d chunks", language, len(text), len(chunks))
    return _concat_wav_chunks([_tts_chunk(c, language, api_key) for c in chunks])

text_to_speech = speak