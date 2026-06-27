"use client";
import { useChatStore } from "@/store/chatStore";

export default function ChatToggle() {
  const toggleOpen = useChatStore((s) => s.toggleOpen);

  return (
    <button id="chat-toggle" onClick={toggleOpen} title="Open AI Assistant">
      🌾
    </button>
  );
}