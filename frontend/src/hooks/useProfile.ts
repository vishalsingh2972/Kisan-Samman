import { useProfileStore } from "@/store/profileStore";
import { useUIStore } from "@/store/uiStore";
import { getProfile, saveProfile, geocode } from "@/lib/api";
import { computeEligibility } from "@/lib/eligibility";
import type { FarmerProfile } from "@/types";

export function useProfile() {
  const { profile, profileSaved, setProfile, setProfileSaved, setEligibility } =
    useProfileStore();
  const { setMapCoords, showToast } = useUIStore();

  const loadProfile = async () => {
    try {
      const saved = await getProfile();
      setProfile(saved);
      if (saved.name) {
        setProfileSaved(true);
        setEligibility(computeEligibility(saved as FarmerProfile));
      }
    } catch {
      // Fall back to default profile silently
    }
  };

  const updateProfile = (patch: Partial<FarmerProfile>) => {
    setProfile(patch);
    if (profileSaved) {
      const updated = { ...profile, ...patch };
      setEligibility(computeEligibility(updated));
    }
  };

  const save = async () => {
    setProfileSaved(true);
    setEligibility(computeEligibility(profile));

    try {
      await saveProfile(profile);
    } catch {
      // Save failure is non-critical
    }

    try {
      const { latitude, longitude } = await geocode(
        `${profile.village}, ${profile.district}, ${profile.state}`
      );
      setProfile({ latitude, longitude });
      setMapCoords([latitude, longitude]);
    } catch {
      // Fall back to state-level map zoom
    }

    showToast("✅ Profile saved!");
  };

  return { loadProfile, updateProfile, save };
}