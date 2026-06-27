import type { FarmerProfile, EligibilityResult } from "@/types";

const NOTIFIED_CROPS = new Set([
  "wheat", "rice", "sugarcane", "cotton", "soybean", "maize",
  "groundnut", "sunflower", "mustard", "gram", "tur", "moong",
  "urad", "bajra", "jowar", "ragi", "barley", "linseed",
  "sesame", "castor", "jute",
]);

export function computeEligibility(profile: FarmerProfile): EligibilityResult {
  const income = profile.annual_income ?? Infinity;

  const pmkisan =
    profile.land_hectares <= 2 &&
    profile.bank_account &&
    profile.aadhaar_linked &&
    !profile.pm_kisan_registered &&
    income < 200000;

  const kcc =
    !profile.kisan_credit_card &&
    profile.land_hectares >= 0.1 &&
    profile.bank_account;

  const kusum =
    profile.land_hectares >= 0.5 &&
    profile.bank_account &&
    profile.aadhaar_linked;

  const bima =
    NOTIFIED_CROPS.has(profile.crop_type.toLocaleLowerCase()) &&
    profile.bank_account &&
    profile.aadhaar_linked;
  return { pmkisan, kcc, kusum, bima };
}