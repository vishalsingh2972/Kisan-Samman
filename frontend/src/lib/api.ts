import type { FarmerProfile, QueryResponse, AppLink } from "@/types";

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function getProfile(): Promise<FarmerProfile> {
  const res = await fetch(`${BASE}/api/profile`);
  if (!res.ok) throw new Error("Failed to load profile");
  return res.json();
}

export async function saveProfile(profile: FarmerProfile): Promise<void>{
  await fetch(`${BASE}/api/profile`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(profile),
  });
}

export async function geocode(query: string): Promise<{ latitude: number; longitude: number }> {
  const res = await fetch(`${BASE}/api/geocode`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });
  if (!res.ok) throw new Error("Geocode failed");
  return res.json();
}

export async function queryText(
  text: string,
  language: string,
  profile: FarmerProfile
): Promise<QueryResponse> {
  const res = await fetch(`${BASE}/api/query/text`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, language, profile }),
  });
  if (!res.ok) throw new Error('Query Failed');
  return res.json();
}

export async function queryAudio(formData: FormData): Promise<QueryResponse> {
  const res = await fetch(`${BASE}/api/query/audio`, {
     method: "POST",
     body: formData,
   });
   if (!res.ok) throw new Error("Audio query failed");
   return res.json();
 }
 
 export async function fetchSchemeLink(
   schemeId: string,
   district: string
 ): Promise<{ portal_url: string }> {
   const res = await fetch(`${BASE}/api/scheme/link`, {
     method: "POST",
     headers: { "Content-Type": "application/json" },
     body: JSON.stringify({ scheme_id: schemeId, district }),
   });
   if (!res.ok) throw new Error("Scheme link fetch failed");
   return res.json();
 }