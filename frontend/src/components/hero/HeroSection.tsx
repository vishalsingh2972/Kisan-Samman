import NavBar from "./NavBar";

export default function HeroSection() {
  return (
    <section className="hero">
      <div className="hero-bg"></div>
      <div className="field-texture"></div>
      <div className="hero-vignette"></div>
      <div className="hero-content">
        <NavBar />
        <div className="hero-body">
          <div className="hero-left">
            <div className="lang-badge">🎙️ Voice-First AI · Multi-Language</div>
            <h1 className="hero-title">Kisaan Schemes</h1>
            <p className="hero-sub">
              Create your profile, let our AI find your eligible government schemes,
              and locate the nearest Common Service Centre — all in your language.
            </p>
            <div className="hero-btns">
              <a className="btn-primary" href="#profile-section">📝 Create Profile</a>
              <a className="btn-primary" href="#map-section" style={{ background: "linear-gradient(135deg, var(--navy), #2a4a6c)" }}>📍 Find CSC</a>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}