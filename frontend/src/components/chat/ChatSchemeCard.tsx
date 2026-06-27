"use client";
import { useState } from "react";
import type { Scheme, AppLink } from "@/types";
import { fetchSchemeLink } from "@/lib/api";
import { useProfileStore } from "@/store/profileStore";

interface Props {
  scheme: Scheme;
  appLink?: AppLink;
}

export default function ChatSchemeCard({ scheme, appLink }: Props) {
  const profile = useProfileStore((s) => s.profile);
  const [btnText, setBtnText] = useState("📋 Apply Link");
  const [btnDisabled, setBtnDisabled] = useState(false);
  const [portalUrl, setPortalUrl] = useState(appLink?.portal_url ?? scheme.portal_url);

  const handleApplyLink = async () => {
    if (portalUrl) {
      window.open(portalUrl, "_blank");
      return;
    }
    setBtnDisabled(true);
    setBtnText("⏳ Fetching…");
    try {
      const data = await fetchSchemeLink(scheme.id, profile.district);
      if (data.portal_url) {
        setPortalUrl(data.portal_url);
        window.open(data.portal_url, "_blank");
        setBtnText("🌐 Apply Now");
      }
    } catch {
      setBtnText("📋 Apply Link");
    } finally {
      setBtnDisabled(false);
    }
  };

  const confidence = Math.round((scheme.confidence ?? 0) * 100);

  return (
    <div className="chat-scheme-card">
      <div className="csc-header">
        <span className="csc-name">{scheme.name}</span>
        <span className="match-badge">{confidence}% match</span>
      </div>
      <div className="csc-benefit">{scheme.benefit}</div>
      {appLink?.csc_address && (
        <div className="csc-location">
          📍 {appLink.csc_address}
          {appLink.csc_distance_km ? ` · ${appLink.csc_distance_km} km` : ""}
        </div>
      )}
      <button
        className="apply-btn"
        onClick={handleApplyLink}
        disabled={btnDisabled}
      >
        {btnText}
      </button>
    </div>
  );
}