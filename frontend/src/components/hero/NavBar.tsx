"use client";
import { useLanguage } from "@/hooks/useLanguage";
import { LANGUAGES } from "@/lib/constants";

export default function NavBar() {
  const { currentLanguage, setLanguage } = useLanguage();

  return (
    <nav>
      <a className="logo" href="#">
        <div className="logo-icon">🌾</div>
        <div className="logo-text-wrap">
          <span className="logo-hindi">किसान सम्मान</span>
          <span className="logo-eng">Kisan Samman</span>
        </div>
      </a>

      <ul className="nav-links">
        <li><a href="#profile-section">My Profile</a></li>
        <li><a href="#map-section">Locate CSC</a></li>
      </ul>

      <div style={{ display: "flex", alignItems: "center", gap: "0.9rem" }}>
        <div className="online-badge">
          <div className="status-dot"></div>
          AI Online
        </div>
        <select
          id="globalLangSelect"
          className="nav-lang-select"
          value={currentLanguage}
          onChange={(e) => setLanguage(e.target.value)}
        >
          {LANGUAGES.map((l) => (
            <option key={l.code} value={l.code}>{l.label}</option>
          ))}
        </select>
        <a className="nav-cta" href="#profile-section">Check Eligibility</a>
      </div>
    </nav>
  );
}