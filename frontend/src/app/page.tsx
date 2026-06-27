"use client";
import { useEffect } from "react";
import { useProfile } from "@/hooks/useProfile";
import HeroSection from "@/components/hero/HeroSection";
import ProfileSection from "@/components/profile/ProfileSection";
import MapSection from "@/components/map/MapSection";
import ChatToggle from "@/components/chat/ChatToggle";
import ChatWindow from "@/components/chat/ChatWindow";
import Toast from "@/components/ui/Toast";

export default function Page() {
  const { loadProfile } = useProfile();

  useEffect(() => {
    loadProfile();
  }, []);

  return (
    <main>
      <HeroSection />
      <ProfileSection />
      <MapSection />
      <ChatToggle />
      <ChatWindow />
      <Toast />
    </main>
  );
}