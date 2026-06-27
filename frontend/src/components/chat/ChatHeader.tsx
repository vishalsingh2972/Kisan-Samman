"use client";
import { useChatStore } from "@/store/chatStore";
import { useLanguage } from "@/hooks/useLanguage";
import { LANGUAGES } from "@/lib/constants";

export default function ChatHeader() {
  const setOpen = useChatStore((s) => s.setOpen);
  const isSpeaking = useChatStore((s) => s.isSpeaking);
  const { currentLanguage, setLanguage } = useLanguage();

  return (
    <div className="chat-header">
      <div className="chat-avatar">🌾</div>
      <div className="chat-header-info">
        <div className="chat-header-name">Kisan Samman AI</div>
        <div className="chat-header-status" id="chatStatus">
          <span style={{ width: "6px", height: "6px", background: "#4caf50", borderRadius: "50%", display: "inline-block" }}></span>
          {" "}Online · Ask in your language
        </div>
      </div>
      <span className={`speaking-badge${isSpeaking ? "" : " hidden"}`} id="speakingBadge">🔊 Speaking…</span>
      <select
        id="chatLangSelect"
        className="chat-lang-select"
        value={currentLanguage}
        onChange={(e) => setLanguage(e.target.value)}
        style={{ marginLeft: "4px" }}
      >
        {LANGUAGES.map((l) => (
          <option key={l.code} value={l.code}>{l.label}</option>
        ))}
      </select>
      <button className="chat-close" onClick={() => setOpen(false)}>✕</button>
    </div>
  );
}