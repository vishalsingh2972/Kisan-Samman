import type { EligibilityResult } from "@/types";

interface SchemeCheckItem {
  key: keyof EligibilityResult;
  name: string;
  description: string;
}

const SCHEME_ITEMS: SchemeCheckItem[] = [
  { key: "pmkisan", name: "PM-KISAN Samman Nidhi", description: "₹6,000 / year · land ≤ 2 ha · income < ₹2L" },
  { key: "kcc", name: "Kisan Credit Card (KCC)", description: "Credit up to ₹3 Lakh @ 4% · no existing KCC" },
  { key: "kusum", name: "PM KUSUM Yojana", description: "Solar Pump subsidy · land ≥ 0.5 ha" },
  { key: "bima", name: "PM Fasal Bima Yojana", description: "Crop Insurance · notified crops only" },
];

interface Props {
  eligibility: EligibilityResult | null;
  profileSaved: boolean;
}

const SCHEME_ICONS: Record<string, string> = {
  pmkisan: "💰",
  kcc: "💳",
  kusum: "☀️",
  bima: "🛡️",
};

export default function EligibilityPanel({ eligibility, profileSaved }: Props) {
  return (
    <div className="status-section">
      <div className="status-title">🛡️ Quick Eligibility Check</div>

      <div className={`elig-hint${!profileSaved ? " show" : ""}`} id="eligHint">
        Fill in your details and click <strong>Save Profile</strong> to see your eligibility.
      </div>

      {SCHEME_ITEMS.map(({ key, name, description }) => {
        const eligible = eligibility?.[key];
        const itemClass = !profileSaved ? "pending" : eligible ? "eligible" : "not-eligible";
        const badgeClass = !profileSaved ? "state-pending" : eligible ? "state-yes" : "state-no";
        const badgeText = !profileSaved ? "—" : eligible ? "ELIGIBLE" : "NOT ELIGIBLE";

        return (
          <div key={key} className={`scheme-check-item ${itemClass}`}>
            <div className="scheme-left">
              <div className="scheme-icon">{SCHEME_ICONS[key]}</div>
              <div className="scheme-info">
                <h4>{name}</h4>
                <p>{description}</p>
              </div>
            </div>
            <span className={`elig-badge ${badgeClass}`}>{badgeText}</span>
          </div>
        );
      })}
    </div>
  );
}