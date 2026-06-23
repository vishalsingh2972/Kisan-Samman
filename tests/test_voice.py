"""
test_voice.py — ASR and TTS round-trip tests.
In MOCK_VOICE mode: validates interface contracts without Sarvam API.
With real SARVAM_API_KEY: performs live transcription and synthesis.
"""
import os, sys, pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

MOCK_VOICE = os.getenv("MOCK_VOICE", "true").lower() == "true"


class TestASR:
    def test_mock_transcribe_returns_string(self):
        os.environ["MOCK_VOICE"] = "true"
        from voice.asr import transcribe
        result = transcribe(b"fake_audio_data", language="mr-IN")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_mock_hindi_transcription(self):
        os.environ["MOCK_VOICE"] = "true"
        from voice.asr import transcribe
        result = transcribe(b"fake", language="hi-IN")
        assert isinstance(result, str)

    @pytest.mark.skipif(MOCK_VOICE, reason="Requires real SARVAM_API_KEY")
    def test_live_asr(self):
        from voice.asr import transcribe
        # Load a real test WAV file if available
        test_wav = Path("tests/fixtures/sample_mr.wav")
        if not test_wav.exists():
            pytest.skip("No test WAV fixture found")
        audio_bytes = test_wav.read_bytes()
        result = transcribe(audio_bytes, language="mr-IN")
        assert isinstance(result, str)
        assert len(result) > 0


class TestTTS:
    def test_mock_speak_returns_bytes(self):
        os.environ["MOCK_VOICE"] = "true"
        from voice.tts import speak
        audio = speak("PM-KISAN योजना", language="mr-IN")
        assert isinstance(audio, bytes)
        assert len(audio) > 0

    def test_mock_speak_all_languages(self):
        os.environ["MOCK_VOICE"] = "true"
        from voice.tts import speak
        for lang in ["hi-IN", "mr-IN", "ta-IN", "te-IN"]:
            audio = speak("test", language=lang)
            assert isinstance(audio, bytes)

    @pytest.mark.skipif(MOCK_VOICE, reason="Requires real SARVAM_API_KEY")
    def test_live_tts(self):
        from voice.tts import speak
        audio = speak("PM-KISAN योजनेसाठी तुम्ही पात्र आहात।", language="mr-IN")
        assert isinstance(audio, bytes)
        assert len(audio) > 1000  # real audio should be substantial
