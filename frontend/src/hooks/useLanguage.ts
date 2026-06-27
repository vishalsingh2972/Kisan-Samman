import { useUIStore } from "@/store/uiStore";
import { useProfileStore } from "@/store/profileStore";

export function useLanguage() {
  const currentLanguage = useUIStore((s) => s.currentLanguage);
  const storeSetLanguage = useUIStore((s) => s.setLanguage);
  const setProfile = useProfileStore((s) => s.setProfile);

  const setLanguage = (lang: string) => {
    storeSetLanguage(lang);
    setProfile({ language_code: lang });
  };

  return { currentLanguage, setLanguage };
}