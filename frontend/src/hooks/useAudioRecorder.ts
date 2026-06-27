import { useRef, useState } from "react";
import { useChatStore } from "@/store/chatStore";
import { useProfileStore } from "@/store/profileStore";
import { useUIStore } from "@/store/uiStore";
import { queryAudio } from "@/lib/api";
import { useChat } from "./useChat";

type MicStatus = { msg: string; type: "idle" | "recording" | "processing" | "success" | "error" };

export function useAudioRecorder() {
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const [isRecording, setIsRecording] = useState(false);
  const [micStatus, setMicStatus] = useState<MicStatus>({ msg: "", type: "idle" });

  const { addMessage, setLoading } = useChatStore();
  const { profile } = useProfileStore();
  const { currentLanguage } = useUIStore();
  const { handleQueryResponse } = useChat();

  let msgCounter = 0;
  const uid = () => `audio-msg-${++msgCounter}-${Date.now()}`;

  const sendAudioQuery = async (blob: Blob) => {
    setMicStatus({ msg: "Processing…", type: "processing" });
    setLoading(true);

    const formData = new FormData();
    formData.append("audio", blob, "query.webm");
    formData.append("language", currentLanguage);
    formData.append("profile", JSON.stringify(profile));

    try {
      const data = await queryAudio(formData);
      if (data.transcription) {
        addMessage({ id: uid(), type: "user", text: `🎤 "${data.transcription}"` });
        setMicStatus({ msg: `✓ ${data.transcription}`, type: "success" });
      }
      handleQueryResponse(data);
    } catch {
      addMessage({ id: uid(), type: "error", text: "⚠️ Audio processing failed. Please try again." });
      setMicStatus({ msg: "⚠️ Failed to process audio", type: "error" });
    } finally {
      setLoading(false);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach((t) => t.stop());
    }
    setIsRecording(false);
  };

  const toggleRecording = async () => {
    if (isRecording) {
      stopRecording();
      return;
    }

    const isSecure =
      location.protocol === "https:" || location.hostname === "localhost";
    if (!isSecure) {
      setMicStatus({ msg: "⚠️ Microphone requires HTTPS or localhost", type: "error" });
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioChunksRef.current = [];

      const mimeType = MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
        ? "audio/webm;codecs=opus"
        : "audio/webm";

      const recorder = new MediaRecorder(stream, { mimeType });
      mediaRecorderRef.current = recorder;

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data);
      };

      recorder.onstop = () => {
        const blob = new Blob(audioChunksRef.current, { type: mimeType });
        sendAudioQuery(blob);
      };

      recorder.start(250);
      setIsRecording(true);
      setMicStatus({ msg: "🔴 Recording… tap to stop", type: "recording" });
    } catch {
      setMicStatus({ msg: "⚠️ Microphone access denied", type: "error" });
    }
  };

  return { toggleRecording, isRecording, micStatus };
}