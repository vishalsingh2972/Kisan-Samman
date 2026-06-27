"use client";
import { useChatStore } from "@/store/chatStore";
import ChatHeader from "./ChatHeader";
import QuickChips from "./QuickChips";
import MessageList from "./MessageList";
import ChatInputArea from "./ChatInputArea";

export default function ChatWindow() {
  const isOpen = useChatStore((s) => s.isOpen);

  return (
    <div id="chat-window" className={isOpen ? "open" : ""}>
      <ChatHeader />
      <QuickChips />
      <MessageList />
      <ChatInputArea />
    </div>
  );
}