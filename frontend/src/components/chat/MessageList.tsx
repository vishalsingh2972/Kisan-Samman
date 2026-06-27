"use client";
import { useEffect, useRef } from "react";
import { useChatStore } from "@/store/chatStore";
import ChatMessage from "./ChatMessage";

export default function MessageList() {
  const messages = useChatStore((s) => s.messages);
  const isLoading = useChatStore((s) => s.isLoading);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  return (
    <div id="chat-messages">
      {messages.map((msg) => (
        <ChatMessage key={msg.id} message={msg} />
      ))}
      {isLoading && <ChatMessage message={{ id: "loading", type: "bot", text: "" }} isLoading />}
      <div ref={bottomRef} />
    </div>
  );
}