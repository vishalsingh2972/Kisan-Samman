import { create } from "zustand";
import type { ChatMessage } from "@/types";

interface ChatStore {
  messages: ChatMessage[];
  isOpen: boolean;
  isLoading: boolean;
  currentAudioB64: string | null;
  isSpeaking: boolean;

  addMessage: (msg: ChatMessage) => void;
  setLoading: (v: boolean) => void;
  toggleOpen: () => void;
  setOpen: (v: boolean) => void;
  setAudio: (b64: string | null) => void;
  setSpeaking: (v: boolean) => void;
  clearMessages: () => void;
}

const GREETING: ChatMessage = {
  id: "greeting",
  type: "bot",
  text: "Namaste! 🙏 I'm your AI welfare assistant. Ask me about government schemes, subsidies, or benefits — in any language you prefer.",
};

export const useChatStore = create<ChatStore>((set) => ({
  messages: [GREETING],
  isOpen: false,
  isLoading: false,
  currentAudioB64: null,
  isSpeaking: false,

  addMessage: (msg) =>
    set((state) => ({ messages: [...state.messages, msg] })),
  setLoading: (v) => set({ isLoading: v }),
  toggleOpen: () => set((state) => ({ isOpen: !state.isOpen })),
  setOpen: (v) => set({ isOpen: v }),
  setAudio: (b64) => set({ currentAudioB64: b64 }),
  setSpeaking: (v) => set({ isSpeaking: v }),
  clearMessages: () => set({ messages: [GREETING] }),
}));
