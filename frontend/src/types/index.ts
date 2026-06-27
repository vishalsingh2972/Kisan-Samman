export interface FarmerProfile {
  name: string;
  state: string;
  district: string;
  village: string;
  land_hectares: number;
  crop_type: string;
  caste_category: string;  // "GEN" | "OBC" | "SC" | "ST"
  gender: string;
  age: number | null;
  bank_account: boolean;
  aadhaar_linked: boolean;
  kisan_credit_card: boolean;
  pm_kisan_registered: boolean;
  annual_income: number | null;
  latitude: number | null;
  longitude: number | null;
  language_code: string;
  tags: string[];
}

export interface Scheme {
  id: string;
  name: string;
  full_name: string;
  benefit: string;
  sponsor: string;
  documents_required: string[];
  portal_url: string;
  confidence: number;
  caste_category: string;
}

export interface AppLink {
  portal_url: string;
  documents_required?: string[];
  csc_name?: string;
  csc_address?: string;
  csc_phone?: string;
  csc_distance_km?: number;
}

export interface ChatMessage {
  id: string;
  type: "user" | "bot" | "error";
  text: string;
  schemes?: Scheme[];
  appLinks?: Record<string, AppLink>;
  hasAudio?: boolean;
}

export interface EligibilityResult {
  pmkisan: boolean;
  kcc: boolean;
  kusum: boolean;
  bima: boolean;
}

export interface QueryResponse {
  text: string;
  transcription?: string;
  schemes: Scheme[];
  app_links: Record<string, AppLink>;
  audio_b64: string | null;
  error: string | null;
}
