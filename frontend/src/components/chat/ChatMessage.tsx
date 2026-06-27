"use client";
import type { ChatMessage as ChatMessageType } from "@/types";
import ChatSchemeCard from "./ChatSchemeCard";
import LoadingDots from "@/components/ui/LoadingDots";
import { useChatStore } from "@/store/chatStore";
import { useChat } from "@/hooks/useChat";

interface Props {
  message: ChatMessageType;
  isLoading?: boolean;
}

export default function ChatMessage({ message, isLoading }: Props) {
  const currentAudioB64 = useChatStore((s) => s.currentAudioB64);
  const { playAudio } = useChat();

  if (isLoading) {
    return (
      <div className="msg bot">
        <LoadingDots />
      </div>
    );
  }

  return (
    <div className={`msg ${message.type}`}>
      <p>{message.text}</p>

      {message.schemes?.map((scheme) => (
        <ChatSchemeCard
          key={scheme.id}
          scheme={scheme}
          appLink={message.appLinks?.[scheme.id]}
        />
      ))}

      {message.hasAudio && currentAudioB64 && (
        <button
          className="play-audio-btn"
          onClick={() => playAudio(currentAudioB64)}
        >
          🔊 Play Response
        </button>
      )}
    </div>
  );
}