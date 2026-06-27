export const STATE_COORDS: Record<string, [number, number]> = {
  Maharashtra: [19.7515, 75.7139],
  Punjab: [31.1471, 75.3412],
  "Uttar Pradesh": [26.8467, 80.9462],
  "Madhya Pradesh": [22.9734, 78.6569],
  Rajasthan: [27.0238, 74.2179],
  Gujarat: [22.2587, 71.1924],
  Karnataka: [15.3173, 75.7139],
  "Andhra Pradesh": [15.9129, 79.74],
  "Tamil Nadu": [11.1271, 78.6569],
  Haryana: [29.0588, 76.0856],
};

export const LANGUAGES = [
  { code: "mr-IN", label: "मराठी" },
  { code: "hi-IN", label: "हिंदी" },
  { code: "ta-IN", label: "தமிழ்" },
  { code: "te-IN", label: "తెలుగు" },
  { code: "kn-IN", label: "ಕನ್ನಡ" },
  { code: "bn-IN", label: "বাংলা" },
  { code: "gu-IN", label: "ગુજરાતી" },
  { code: "pa-IN", label: "ਪੰਜਾਬੀ" },
  { code: "en-IN", label: "English" },
];

export const CROPS = ['Wheat', "Rice", "Cotton", "Sugarcane", "Soyabean", "Maize"];

export const QUICK_QUERIES = [
  "My Schemes",
  "PM Kisan",
  "Insurance",
  "Locate CSC",
  "KCC Loan",
  "KUSUM Solar",
];

export const INDIAN_STATES = [
  "Maharashtra",
  "Punjab",
  "Uttar Pradesh",
  "Madhya Pradesh",
  "Rajasthan",
  "Gujarat",
  "Karnataka",
];

export const DEFAULT_PROFILE = {
  name: "Vishal Patil",
  state: "Maharashtra",
  district: "Nashik",
  village: "Yeola",
  land_hectares: 1.2,
  crop_type: "Sugarcane",
  caste_category: "OBC",
  gender: "male",
  age: 42,
  bank_account: true,
  aadhaar_linked: true,
  kisan_credit_card: false,
  pm_kisan_registered: false,
  annual_income: 85000,
  latitude: null,
  longitude: null,
  language_code: "mr-IN",
  tags: [],
};

