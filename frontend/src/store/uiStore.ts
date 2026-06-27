import { create } from "zustand";

interface UIStore {
  currentLanguage: string;
  toast: string | null;
  mapCoords: [number, number] | null;
  mapCscInfo: string;

  setLanguage: (lang: string) => void;
  showToast: (msg: string) => void;
  clearToast: () => void;
  setMapCoords: (coords: [number, number]) => void;
  setMapCscInfo: (info: string) => void;
}

export const useUIStore = create<UIStore>((set) => ({
  currentLanguage: "mr-IN",
  toast: null,
  mapCoords: null,
  mapCscInfo: "Locate your nearest Common Service Centre for offline assistance.",

  setLanguage: (lang) => set({ currentLanguage: lang }),
  showToast: (msg) => set({ toast: msg }),
  clearToast: () => set({ toast: null }),
  setMapCoords: (coords) => set({ mapCoords: coords }),
  setMapCscInfo: (info) => set({ mapCscInfo: info }),
}))

