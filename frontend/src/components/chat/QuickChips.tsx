"use client";
import { useChat } from "@/hooks/useChat";

const CHIPS = [
  { label: "📋 My Schemes",  query: "What schemes am I eligible for?" },
  { label: "🌾 PM Kisan",    query: "PM Kisan Samman Nidhi details" },
  { label: "🛡️ Insurance",   query: "Crop insurance schemes for my crop" },
  { label: "💧 Irrigation",  query: "Irrigation subsidy for farmers" },
  { label: "💳 KCC",         query: "Kisan credit card benefits" },
  { label: "🌱 Soil Card",   query: "Soil health card scheme" },
];

export default function QuickChips() {
  const { quickQuery } = useChat();

  return (
    <div className="quick-chips-area">
      {CHIPS.map(({ label, query }) => (
        <button key={label} className="quick-chip" onClick={() => quickQuery(query)}>
          {label}
        </button>
      ))}
    </div>
  );
}