"""
voice/asr.py — Sarvam AI Speech-to-Text wrapper.

Model   : saaras:v3  (current recommended model as per Sarvam docs)
Endpoint: POST https://api.sarvam.ai/speech-to-text
Auth    : api-subscription-key header
Format  : multipart/form-data  — file field + data fields
Mode    : transcribe (returns transcript in spoken language)

Supported languages (23 total — 22 Indian + English):
  hi-IN, bn-IN, kn-IN, ml-IN, mr-IN, od-IN, pa-IN,
  ta-IN, te-IN, en-IN, gu-IN, as-IN, ur-IN, ne-IN,
  kok-IN, ks-IN, sd-IN, sa-IN, sat-IN, mni-IN, brx-IN,
  mai-IN, doi-IN
  Use "unknown" for automatic language detection.

Audio requirements (from Sarvam docs):
  - Formats : WAV or MP3  (browser WebM must be converted first)
  - WAV spec : 16 kHz, mono, 16-bit PCM for best accuracy
  - Max size : 25 MB per request

Conversion:
  Browser MediaRecorder produces audio/webm. This file converts it to
  16 kHz mono WAV using pydub + ffmpeg before uploading.
  Install: pip install pydub
  Windows: also download ffmpeg from https://ffmpeg.org and add to PATH.
  If pydub/ffmpeg are unavailable, raw bytes are sent as fallback.
"""
from __future__ import annotations

import io
import logging
import os

import requests

logger = logging.getLogger("voice.asr")

# ── Constants ──────────────────────────────────────────────────────────────────

SARVAM_ASR_URL = "https://api.sarvam.ai/speech-to-text"
ASR_MODEL      = "saaras:v3"
ASR_MODE       = "transcribe"   # options: transcribe | translate | verbatim | translit | codemix

# All 23 languages supported by saaras:v3
SUPPORTED_LANGUAGES = [
    "hi-IN", "bn-IN", "kn-IN", "ml-IN", "mr-IN", "od-IN", "pa-IN",
    "ta-IN", "te-IN", "en-IN", "gu-IN", "as-IN", "ur-IN", "ne-IN",
    "kok-IN", "ks-IN", "sd-IN", "sa-IN", "sat-IN", "mni-IN", "brx-IN",
    "mai-IN", "doi-IN",
    "unknown",   # triggers automatic language detection
]

# Reject recordings smaller than this — almost certainly empty (just container header)
MIN_AUDIO_BYTES = 5_000   # 5 KB

# MIME type → pydub format string + file extension
_MIME_MAP = {
    "audio/webm":           ("webm", "webm"),
    "audio/webm;codecs=opus": ("webm", "webm"),
    "audio/ogg":            ("ogg",  "ogg"),
    "audio/ogg;codecs=opus": ("ogg",  "ogg"),
    "audio/mp4":            ("mp4",  "mp4"),
    "audio/mpeg":           ("mp3",  "mp3"),
    "audio/mp3":            ("mp3",  "mp3"),
    "audio/wav":            ("wav",  "wav"),
    "audio/wave":           ("wav",  "wav"),
    "audio/x-wav":          ("wav",  "wav"),
    "audio/aac":            ("aac",  "aac"),
    "audio/flac":           ("flac", "flac"),
}


# ── Mock (development / testing without API key) ──────────────────────────────

_MOCK_TRANSCRIPTS = {
    "hi-IN":  "मुझे सिंचाई सब्सिडी के बारे में जानकारी चाहिए।",
    "mr-IN":  "माझ्या शेतासाठी सिंचन अनुदान मिळेल का?",
    "ta-IN":  "என் நிலத்திற்கு நீர்ப்பாசன மானியம் கிடைக்குமா?",
    "te-IN":  "నా పొలానికి నీటిపారుదల సబ్సిడీ వస్తుందా?",
    "kn-IN":  "ನನ್ನ ಜಮೀನಿಗೆ ನೀರಾವರಿ ಸಹಾಯಧನ ದೊರೆಯುತ್ತದೆಯೇ?",
    "bn-IN":  "আমার জমির জন্য সেচ ভর্তুকি পাব কি?",
    "gu-IN":  "મારી જમીન માટે સિંચાઈ સબ્સિડી મળશે?",
    "pa-IN":  "ਮੇਰੀ ਜ਼ਮੀਨ ਲਈ ਸਿੰਚਾਈ ਸਬਸਿਡੀ ਮਿਲੇਗੀ?",
    "ml-IN":  "എന്റെ നിലത്തിന് ജലസേചന സബ്സിഡി ലഭിക്കുമോ?",
    "en-IN":  "What irrigation subsidies am I eligible for?",
    "unknown": "What government schemes am I eligible for?",
}


def _mock_transcribe(language: str) -> str:
    return _MOCK_TRANSCRIPTS.get(language, _MOCK_TRANSCRIPTS["en-IN"])


# ── Audio conversion: browser format → 16 kHz mono WAV ───────────────────────

def _to_wav(audio_bytes: bytes, mime_type: str) -> tuple[bytes, str]:
    """
    Convert audio_bytes to 16 kHz mono 16-bit WAV using pydub.

    Returns:
        (converted_bytes, file_extension)
        Falls back to (original_bytes, original_ext) if pydub / ffmpeg
        is not available — Sarvam may still accept mp3/ogg directly.
    """
    mime_base = mime_type.split(";")[0].strip().lower()
    pydub_fmt, ext = _MIME_MAP.get(mime_base, ("webm", "webm"))

    # Already WAV — check if it needs re-sampling
    if pydub_fmt == "wav":
        logger.debug("Audio already WAV — skipping conversion")
        return audio_bytes, "wav"

    try:
        from pydub import AudioSegment   # type: ignore

        seg = AudioSegment.from_file(io.BytesIO(audio_bytes), format=pydub_fmt)

        # Normalise to 16 kHz mono 16-bit — optimal for Sarvam ASR
        seg = (
            seg
            .set_frame_rate(16_000)
            .set_channels(1)
            .set_sample_width(2)        # 16-bit
        )

        buf = io.BytesIO()
        seg.export(buf, format="wav")
        wav_bytes = buf.getvalue()

        logger.info(
            "Converted %s → WAV 16kHz mono: %d B → %d B",
            mime_type, len(audio_bytes), len(wav_bytes),
        )
        return wav_bytes, "wav"

    except ImportError:
        logger.warning(
            "pydub not installed. Sending raw %s to Sarvam. "
            "For best results: pip install pydub  (+ ffmpeg on PATH).",
            mime_type,
        )
        return audio_bytes, ext

    except Exception as exc:
        logger.warning(
            "Audio conversion failed (%s). Sending raw %s bytes.",
            exc, mime_type,
        )
        return audio_bytes, ext


# ── Main transcribe function ──────────────────────────────────────────────────

def transcribe(
    audio_bytes: bytes,
    language: str = "hi-IN",
    mime_type: str = "audio/webm",
) -> str:
    """
    Transcribe audio using Sarvam AI saaras:v3.

    Args:
        audio_bytes : Raw audio bytes from browser MediaRecorder or file.
        language    : BCP-47 language code from SUPPORTED_LANGUAGES,
                      or "unknown" to let Sarvam auto-detect the language.
        mime_type   : MIME type reported by the browser / file source.
                      Used to choose the right conversion path.

    Returns:
        Transcribed text string (in the spoken language).

    Raises:
        ValueError          : Audio too short — empty / accidental recording.
        EnvironmentError    : SARVAM_API_KEY missing from environment.
        requests.HTTPError  : Sarvam API returned a non-2xx status.
    """

    # ── 1. Mock mode (no API call) ────────────────────────────────────────────
    if os.getenv("MOCK_VOICE", "false").lower() == "true":
        logger.debug("MOCK_VOICE=true — returning canned transcript for %s", language)
        return _mock_transcribe(language)

    # ── 2. Size guard (catches empty / accidental recordings) ─────────────────
    if len(audio_bytes) < MIN_AUDIO_BYTES:
        raise ValueError(
            f"Recording is too short ({len(audio_bytes):,} bytes). "
            "Please hold the microphone and speak clearly for at least 2–3 seconds."
        )

    # ── 3. API key ────────────────────────────────────────────────────────────
    api_key = os.getenv("SARVAM_API_KEY", "").strip()
    if not api_key:
        raise EnvironmentError(
            "SARVAM_API_KEY is not set. Add it to your .env file."
        )

    # ── 4. Validate language code ─────────────────────────────────────────────
    if language not in SUPPORTED_LANGUAGES:
        logger.warning(
            "Language code %r is not in saaras:v3 supported list. "
            "Falling back to 'unknown' (auto-detect).",
            language,
        )
        language = "unknown"

    # ── 5. Convert audio to WAV ───────────────────────────────────────────────
    upload_bytes, ext = _to_wav(audio_bytes, mime_type)
    upload_mime = "audio/wav" if ext == "wav" else f"audio/{ext}"

    # ── 6. Build multipart request ────────────────────────────────────────────
    #
    #  From Sarvam docs (cURL example):
    #    -H "api-subscription-key: <KEY>"
    #    -F model="saaras:v3"
    #    -F language_code="hi-IN"
    #    -F mode="transcribe"
    #    -F file=@"audio.wav;type=audio/wav"
    #
    headers = {
        "api-subscription-key": api_key,
        # Do NOT set Content-Type here — requests sets it automatically
        # with the correct multipart boundary when using files=
    }

    files = {
        "file": (f"audio.{ext}", io.BytesIO(upload_bytes), upload_mime),
    }

    data = {
        "model":         ASR_MODEL,
        "language_code": language,
        "mode":          ASR_MODE,
    }

    logger.info(
        "Sarvam ASR request → model=%s mode=%s lang=%s file=audio.%s size=%d B",
        ASR_MODEL, ASR_MODE, language, ext, len(upload_bytes),
    )

    # ── 7. HTTP POST ──────────────────────────────────────────────────────────
    try:
        resp = requests.post(
            SARVAM_ASR_URL,
            headers=headers,
            files=files,
            data=data,
            timeout=30,
        )
    except requests.exceptions.ConnectionError as exc:
        raise ConnectionError(
            "Could not reach Sarvam API. Check your internet connection."
        ) from exc
    except requests.exceptions.Timeout:
        raise TimeoutError(
            "Sarvam API timed out after 30 seconds. Try a shorter recording."
        )

    # ── 8. Handle errors with helpful messages ────────────────────────────────
    if not resp.ok:
        try:
            err_body = resp.json()
            err_msg  = err_body.get("message") or err_body.get("detail") or str(err_body)
        except Exception:
            err_msg = resp.text[:300]

        logger.error(
            "Sarvam ASR error %d: %s", resp.status_code, err_msg
        )
        resp.raise_for_status()   # raises requests.HTTPError

    # ── 9. Parse response ─────────────────────────────────────────────────────
    #
    #  Sarvam response schema (saaras:v3 transcribe mode):
    #  {
    #    "request_id":    "20250430_...",
    #    "transcript":    "transcribed text here",
    #    "language_code": "mr-IN"
    #  }
    #
    result     = resp.json()
    transcript = (result.get("transcript") or result.get("text") or "").strip()
    detected   = result.get("language_code", language)

    if not transcript:
        logger.warning("Sarvam ASR returned empty transcript. Full response: %s", result)

    logger.info(
        "Transcript OK — lang=%s chars=%d: %s",
        detected, len(transcript), transcript[:120],
    )

    return transcript