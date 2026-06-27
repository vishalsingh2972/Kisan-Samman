"use client";
import { useRef } from "react";
import { useChat } from "@/hooks/useChat";
import { useAudioRecorder } from "@/hooks/useAudioRecorder";
import { useChatStore } from "@/store/chatStore";

export default function ChatInputArea() {
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const isLoading = useChatStore((s) => s.isLoading);
  const { sendMessage } = useChat();
  const { toggleRecording, isRecording, micStatus } = useAudioRecorder();

  const handleSend = () => {
    const text = inputRef.current?.value.trim();
    if (!text || isLoading) return;
    inputRef.current!.value = "";
    sendMessage(text);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const micClass = isRecording ? "recording" : micStatus.type === "processing" ? "processing" : "";

  return (
    <>
      <div className="chat-input-area">
        <button
          id="mic-btn"
          className={micClass}
          onClick={toggleRecording}
          title="Voice Input"
        >
          {isRecording ? "⏹️" : micStatus.type === "processing" ? "⏳" : "🎤"}
        </button>
        <textarea
          ref={inputRef}
          id="chat-input"
          placeholder="Ask about schemes, subsidies…"
          rows={1}
          onKeyDown={handleKeyDown}
        />
        <button id="send-btn" onClick={handleSend} disabled={isLoading}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>
          </svg>
        </button>
      </div>
      <div className={`mic-status-bar${micStatus.type === "success" ? " ok" : micStatus.type === "error" ? " error" : ""}`} id="micStatusBar">
        {micStatus.msg || "Tap mic to speak in your language"}
      </div>
    </>
  );
}