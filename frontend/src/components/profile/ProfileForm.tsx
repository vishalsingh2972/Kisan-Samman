"use client";
import { useState } from "react";
import { useProfileStore } from "@/store/profileStore";
import { useProfile } from "@/hooks/useProfile";
import CropSelector from "./CropSelector";
import ToggleRow from "./ToggleRow";
import { INDIAN_STATES } from "@/lib/constants";

export default function ProfileForm() {
  const profile = useProfileStore((s) => s.profile);
  const { updateProfile, save } = useProfile();
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    await save();
    setSaving(false);
  };

  return (
    <div>
      <div className="form-group">
        <label className="form-label">Full Name (पूरा नाम)</label>
        <input className="form-input" type="text" placeholder="e.g. Vishal Patil"
          value={profile.name}
          onChange={(e) => updateProfile({ name: e.target.value })} />
      </div>

      <div className="row-group">
        <div className="form-group">
          <label className="form-label">Village (गांव)</label>
          <input className="form-input" type="text" placeholder="e.g. Yeola"
            value={profile.village}
            onChange={(e) => updateProfile({ village: e.target.value })} />
        </div>
        <div className="form-group">
          <label className="form-label">District (जिला)</label>
          <input className="form-input" type="text" placeholder="e.g. Nashik"
            value={profile.district}
            onChange={(e) => updateProfile({ district: e.target.value })} />
        </div>
      </div>

      <div className="row-group">
        <div className="form-group">
          <label className="form-label">State (राज्य)</label>
          <select className="form-select" value={profile.state}
            onChange={(e) => updateProfile({ state: e.target.value })}>
            {INDIAN_STATES.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>
        <div className="form-group">
          <label className="form-label">Category (वर्ग)</label>
          <select className="form-select" value={profile.caste_category}
            onChange={(e) => updateProfile({ caste_category: e.target.value })}>
            <option value="GEN">General</option>
            <option value="OBC">OBC</option>
            <option value="SC">SC</option>
            <option value="ST">ST</option>
          </select>
        </div>
      </div>

      <div className="row-group">
        <div className="form-group">
          <label className="form-label">Land Size (hectares)</label>
          <input className="form-input" type="number" placeholder="0.0" step="0.1" min="0"
            value={profile.land_hectares}
            onChange={(e) => updateProfile({ land_hectares: parseFloat(e.target.value) || 0 })} />
          <small style={{ color: "var(--text-muted)", fontSize: "0.7rem", marginTop: "4px", display: "block" }}>
            PM-KISAN: &lt; 2 ha · KUSUM: ≥ 0.5 ha
          </small>
        </div>
        <div className="form-group">
          <label className="form-label">Annual Income (₹)</label>
          <input className="form-input" type="number" placeholder="e.g. 85000"
            value={profile.annual_income ?? ""}
            onChange={(e) => updateProfile({ annual_income: parseFloat(e.target.value) || null })} />
          <small style={{ color: "var(--text-muted)", fontSize: "0.7rem", marginTop: "4px", display: "block" }}>
            Must be below ₹2,00,000 for most schemes
          </small>
        </div>
      </div>

      <div className="form-group">
        <label className="form-label">Primary Crop (मुख्य फसल)</label>
        <input className="form-input" type="text" placeholder="e.g. sugarcane, wheat, rice"
          value={profile.crop_type}
          onChange={(e) => updateProfile({ crop_type: e.target.value })} />
        <CropSelector
          selected={profile.crop_type}
          onChange={(crop) => updateProfile({ crop_type: crop })}
        />
      </div>

      <div className="form-group">
        <label className="form-label">Account &amp; Documents</label>
        <ToggleRow label="Bank Account"
          checked={profile.bank_account}
          onChange={(v) => updateProfile({ bank_account: v })} />
        <ToggleRow label="Aadhaar Linked to Bank"
          checked={profile.aadhaar_linked}
          onChange={(v) => updateProfile({ aadhaar_linked: v })} />
        <ToggleRow label="Kisan Credit Card (KCC)"
          checked={profile.kisan_credit_card}
          onChange={(v) => updateProfile({ kisan_credit_card: v })} />
        <ToggleRow label="PM-Kisan Already Registered"
          checked={profile.pm_kisan_registered}
          onChange={(v) => updateProfile({ pm_kisan_registered: v })} />
      </div>

      <button className="save-profile-btn" onClick={handleSave} disabled={saving}>
        {saving ? "⏳ Saving…" : "💾 Save Profile & Check Eligibility"}
      </button>
    </div>
  );
}