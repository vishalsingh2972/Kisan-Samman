import { useChatStore } from "@/store/chatStore";
import { useProfileStore } from "@/store/profileStore";
import { useUIStore } from "@/store/uiStore";
import { queryText } from "@/lib/api";
import type { ChatMessage, QueryResponse } from "@/types";

let msgCounter = 0;
const uid = () => `msg-${++msgCounter}`;

export function useChat() {
  const { addMessage, setLoading, setOpen, setAudio, setSpeaking } = useChatStore();
  const { profile, setAISchemes } = useProfileStore();
  const { currentLanguage, setMapCscInfo } = useUIStore();

  const playAudio = (b64: string) => {
    try {
      const bytes = Uint8Array.from(atob(b64), (c) => c.charCodeAt(0));
      const blob = new Blob([bytes], { type: "audio/wav" });
      const url = URL.createObjectURL(blob);
      const audio = new Audio(url);
      setSpeaking(true);
      audio.onended = () => {
        setSpeaking(false);
        URL.revokeObjectURL(url);
      };
      audio.play().catch(() => setSpeaking(false));
    } catch {
      setSpeaking(false);
    }
  };

  const handleQueryResponse = (data: QueryResponse) => {
    const botMsg: ChatMessage = {
      id: uid(),
      type: data.error ? "error" : "bot",
      text: data.error ?? data.text,
      schemes: data.schemes?.slice(0, 4),
      appLinks: data.app_links,
      hasAudio: !!data.audio_b64,
    };
    addMessage(botMsg);

    if (data.schemes?.length) {
      setAISchemes(data.schemes, data.app_links ?? {});
    }

    if (data.audio_b64) {
      setAudio(data.audio_b64);
      setTimeout(() => playAudio(data.audio_b64!), 300);
    }

    const firstLink = data.app_links
      ? Object.values(data.app_links)[0]
      : null;
    if (firstLink?.csc_address) {
      setMapCscInfo(`📍 ${firstLink.csc_address} · ${firstLink.csc_distance_km} km`);
    }
  };

  const sendMessage = async (text: string) => {
    addMessage({ id: uid(), type: "user", text });
    setLoading(true);
    try {
      const data = await queryText(text, currentLanguage, profile);
      handleQueryResponse(data);
    } catch {
      addMessage({ id: uid(), type: "error", text: "⚠️ Could not reach the server. Please try again." });
    } finally {
      setLoading(false);
    }
  };

  const quickQuery = (text: string) => {
    setOpen(true);
    sendMessage(text);
  };

  return { sendMessage, quickQuery, playAudio, handleQueryResponse };
}