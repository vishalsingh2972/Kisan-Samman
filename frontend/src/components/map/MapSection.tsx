"use client";
import dynamic from "next/dynamic";
import { useUIStore } from "@/store/uiStore";
import { useProfileStore } from "@/store/profileStore";

const CSCMap = dynamic(() => import("./CSCMap"), { ssr: false });

export default function MapSection() {
  const mapCoords = useUIStore((s) => s.mapCoords);
  const mapCscInfo = useUIStore((s) => s.mapCscInfo);
  const profile = useProfileStore((s) => s.profile);

  return (
    <section id="map-section">
      <div className="section-header" style={{ position: "relative", transform: "none", left: "auto", marginBottom: "3rem", textAlign: "center" }}>
        <div className="section-badge">Locator Tool</div>
        <h2 className="section-title">Find Nearest CSC</h2>
      </div>

      <div className="map-wrapper" style={{ position: "relative" }}>
        <div className="map-overlay-info">
          <div className="map-overlay-title">🗺️ Service Centers</div>
          <div className="map-overlay-desc" id="mapDesc">Map shows your profile location.</div>
          <div className="map-overlay-csc" id="mapCscInfo">{mapCscInfo !== "Locate your nearest Common Service Centre for offline assistance." ? mapCscInfo : ""}</div>
        </div>
        <CSCMap
          lat={mapCoords?.[0] ?? profile.latitude}
          lng={mapCoords?.[1] ?? profile.longitude}
          state={profile.state}
          profileName={profile.name}
          village={profile.village}
        />
      </div>
    </section>
  );
}