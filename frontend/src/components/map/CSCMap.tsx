"use client";
import { useEffect, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { STATE_COORDS } from "@/lib/constants";

// Leaflet's default icon resolution uses _getIconUrl() which relies on require() at runtime.
// Webpack/Next.js rewrites asset URLs during bundling, breaking that lookup — so we delete
// the method and point the icons at the unpkg CDN instead.
delete (L.Icon.Default.prototype as unknown as Record<string, unknown>)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

interface Props {
  lat?: number | null;
  lng?: number | null;
  state?: string;
  profileName?: string;
  village?: string;
}

function makeEmojiIcon(emoji: string, size: number) {
  return L.divIcon({
    html: `<span style="font-size:${size}px;line-height:1">${emoji}</span>`,
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
    className: "",
  });
}

function addCSCMarkers(map: L.Map, center: [number, number]) {
  for (let i = 0; i < 5; i++) {
    const lat = center[0] + (Math.random() - 0.5) * 1.2;
    const lng = center[1] + (Math.random() - 0.5) * 1.2;
    const dist = (0.5 + Math.random() * 8).toFixed(1);
    L.marker([lat, lng], { icon: makeEmojiIcon("🏢", 28) })
      .addTo(map)
      .bindPopup(`<b>CSC Centre #10${i + 1}</b><br>📍 ${dist} km from you<br><span style="color:green">● Open</span>`);
  }
}

export default function CSCMap({ lat, lng, state, profileName, village }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<L.Map | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    // Determine center
    const stateCenter: [number, number] =
      STATE_COORDS[state ?? ""] ?? [20.5937, 78.9629];
    const center: [number, number] =
      lat && lng ? [lat, lng] : stateCenter;
    const zoom = lat && lng ? 12 : 7;

    // Init map once
    if (!mapRef.current) {
      mapRef.current = L.map(containerRef.current).setView(center, zoom);
      L.tileLayer(
        "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
        {
          attribution:
            '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors © <a href="https://carto.com/attributions">CARTO</a>',
          maxZoom: 19,
        }
      ).addTo(mapRef.current);
      addCSCMarkers(mapRef.current, center);
    } else {
      // Update existing map
      mapRef.current.flyTo(center, zoom, { duration: 1.5 });
    }

    // Farmer marker
    if (lat && lng) {
      L.marker([lat, lng], { icon: makeEmojiIcon("👨‍🌾", 32) })
        .addTo(mapRef.current)
        .bindPopup(`<b>${profileName ?? "Farmer"}</b><br>${village ?? ""}`);
    }

    return () => {
      // Cleanup only on unmount
    };
  }, [lat, lng, state, profileName, village]);

  // Cleanup on component unmount
  useEffect(() => {
    return () => {
      mapRef.current?.remove();
      mapRef.current = null;
    };
  }, []);

  return <div ref={containerRef} id="map" style={{ height: "100%", width: "100%" }} />;
}