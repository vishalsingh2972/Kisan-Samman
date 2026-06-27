import { create } from "zustand";

import type { FarmerProfile, EligibilityResult, Scheme, AppLink } from "@/types";
import { DEFAULT_PROFILE } from "@/lib/constants";

interface ProfileStore {
  profile: FarmerProfile;
  profileSaved: boolean;
  eligibility: EligibilityResult | null;
  aiSchemes: Scheme[];
  aiAppLinks: Record<string, AppLink>;

  setProfile: (patch: Partial<FarmerProfile>) => void;
  setProfileSaved: (saved: boolean) => void;
  setEligibility: (e: EligibilityResult) => void;
  setAISchemes: (schemes: Scheme[], links: Record<string, AppLink>) => void;
}

export const useProfileStore = create<ProfileStore>((set) => ({
  profile: DEFAULT_PROFILE as FarmerProfile,
  profileSaved: false,
  eligibility: null,
  aiSchemes: [],
  aiAppLinks: {},

  setProfile: (patch) =>
    set((state) => ({ profile: { ...state.profile, ...patch } })),
  setProfileSaved: (saved) => set({ profileSaved: saved }),
  setEligibility: (e) => set({ eligibility: e }),
  setAISchemes: (schemes, links) =>
    set({ aiSchemes: schemes, aiAppLinks: links }),
}));