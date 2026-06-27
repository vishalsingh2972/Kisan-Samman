"use client";
import { useProfileStore } from "@/store/profileStore";
import ProfileForm from "./ProfileForm";
import IDCard from "./IDCard";
import EligibilityPanel from "./EligibilityPanel";
import AISchemesPanel from "./AISchemesPanel";

export default function ProfileSection() {
  const profile = useProfileStore((s) => s.profile);
  const profileSaved = useProfileStore((s) => s.profileSaved);
  const eligibility = useProfileStore((s) => s.eligibility);
  const aiSchemes = useProfileStore((s) => s.aiSchemes);
  const aiAppLinks = useProfileStore((s) => s.aiAppLinks);

  return (
    <section id="profile-section">
      <div className="section-header">
        <div className="section-badge">AI-Powered Eligibility Check</div>
        <h2 className="section-title">Farmer Profile</h2>
        <p className="section-sub">Fill in your details. The AI will find all eligible schemes for you automatically.</p>
      </div>
      <div className="profile-container">
        <div className="profile-form-wrapper">
          <ProfileForm />
        </div>
        <div className="profile-visualizer">
          <IDCard profile={profile} />
          <EligibilityPanel eligibility={eligibility} profileSaved={profileSaved} />
          <AISchemesPanel schemes={aiSchemes} appLinks={aiAppLinks} />
        </div>
      </div>
    </section>
  );
}