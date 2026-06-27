"use client";
import { useState } from "react";
import type { Scheme, AppLink } from "@/types";
import { fetchSchemeLink } from "@/lib/api";
import { useProfileStore } from "@/store/profileStore";

interface Props {
  schemes: Scheme[];
  appLinks: Record<string, AppLink>;
}

function AISchemeCard({ scheme, appLink, district }: { scheme: Scheme; appLink?: AppLink; district: string }) {
  const [portalUrl, setPortalUrl] = useState(appLink?.portal_url ?? scheme.portal_url);
  const [btnText, setBtnText] = useState("📋 Get Apply Link");
  const [btnDisabled, setBtnDisabled] = useState(false);

  const handleApply = async () => {
    if (portalUrl) { window.open(portalUrl, "_blank"); return; }
    setBtnDisabled(true);
    setBtnText("⏳ Fetching…");
    try {
      const data = await fetchSchemeLink(scheme.id, district);
      if (data.portal_url) {
        setPortalUrl(data.portal_url);
        window.open(data.portal_url, "_blank");
        setBtnText("🌐 Apply Now");
      }
    } catch {
      setBtnText("📋 Get Apply Link");
    } finally {
      setBtnDisabled(false);
    }
  };

  const confidence = Math.round((scheme.confidence ?? 0) * 100);

  return (
    <div className="ai-scheme-card">
      <div className="ai-scheme-header">
        <div>
          <div className="ai-scheme-name">{scheme.name}</div>
          <div className="ai-scheme-sponsor">{scheme.sponsor}</div>
        </div>
        <span className="match-badge">{confidence}% match</span>
      </div>
      <div className="ai-scheme-benefit">{scheme.benefit}</div>
      {scheme.documents_required?.length > 0 && (
        <div className="ai-scheme-docs">
          📄 {scheme.documents_required.join(", ")}
        </div>
      )}
      {appLink?.csc_address && (
        <div className="ai-scheme-csc">
          🏢 {appLink.csc_address}
          {appLink.csc_phone ? ` · ${appLink.csc_phone}` : ""}
        </div>
      )}
      <div className="ai-scheme-actions">
        {portalUrl ? (
          <a href={portalUrl} target="_blank" rel="noreferrer" className="apply-online-btn">
            Apply Online ↗
          </a>
        ) : (
          <button className="apply-link-btn" onClick={handleApply} disabled={btnDisabled}>
            {btnText}
          </button>
        )}
      </div>
    </div>
  );
}

export default function AISchemesPanel({ schemes, appLinks }: Props) {
  const district = useProfileStore((s) => s.profile.district);

  if (!schemes.length) {
    return (
      <div className="ai-schemes-section">
        <div className="ai-schemes-title">🤖 AI-Found Schemes</div>
        <div className="ai-empty-state">
          Ask the AI assistant about schemes — results appear here
        </div>
      </div>
    );
  }

  return (
    <div className="ai-schemes-section">
      <div className="ai-schemes-title">🤖 AI-Found Schemes ({schemes.length})</div>
      {schemes.map((scheme) => (
        <AISchemeCard
          key={scheme.id}
          scheme={scheme}
          appLink={appLinks[scheme.id]}
          district={district}
        />
      ))}
    </div>
  );
}