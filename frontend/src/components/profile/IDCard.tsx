import type { FarmerProfile } from "@/types";

interface Props {
  profile: FarmerProfile;
}

export default function IDCard({ profile }: Props) {
  const crop = profile.crop_type
    ? profile.crop_type.charAt(0).toUpperCase() + profile.crop_type.slice(1)
    : "—";
  const location = `${profile.village}, ${profile.district}, ${profile.state?.slice(0, 2).toUpperCase() ?? ""}`;

  return (
    <div className="id-card">
      <div className="id-header">
        <div className="id-logo">🇮🇳 GOVERNMENT OF INDIA</div>
        <div style={{ display: "flex", gap: "1rem", alignItems: "center" }}>
          <div className="id-photo">👨‍🌾</div>
          <div>
            <div className="id-name">{profile.name || "—"}</div>
            <div className="id-id-num">ID: KIS-2023-8842</div>
          </div>
        </div>
      </div>
      <div className="id-body">
        <div className="id-row">
          <span className="id-label">Location</span>
          <span className="id-value">{location}</span>
        </div>
        <div className="id-row">
          <span className="id-label">Land Holding</span>
          <span className="id-value">{profile.land_hectares} Ha</span>
        </div>
        <div className="id-row">
          <span className="id-label">Crop</span>
          <span className="id-value">{crop}</span>
        </div>
        <div className="id-row">
          <span className="id-label">Category</span>
          <span className="id-value">{profile.caste_category || "—"}</span>
        </div>
        <div className="id-row">
          <span className="id-label">Aadhaar</span>
          <span className={`id-value ${profile.aadhaar_linked ? "aadhaar-linked" : "aadhaar-unlinked"}`}>
            {profile.aadhaar_linked ? "✓ Linked" : "✗ Not Linked"}
          </span>
        </div>
      </div>
    </div>
  );
}