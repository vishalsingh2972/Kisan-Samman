"""
farmer_profile.py — Schema and loader for a farmer's profile.
"""
from __future__ import annotations
import json, logging
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class FarmerProfile:
    name: str
    state: str
    district: str
    village: str
    land_hectares: float
    crop_type: str
    caste_category: str             # GEN | OBC | SC | ST
    gender: str = "male"
    age: Optional[int] = None
    bank_account: bool = True
    aadhaar_linked: bool = True
    kisan_credit_card: bool = False
    pm_kisan_registered: bool = False
    annual_income: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    language_code: str = "hi-IN"
    tags: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    def summary(self) -> str:
        return (
            f"{self.name} from {self.village}, {self.district}, {self.state}. "
            f"Land: {self.land_hectares} ha. Crop: {self.crop_type}. "
            f"Category: {self.caste_category}. "
            f"Bank: {'yes' if self.bank_account else 'no'}. "
            f"Aadhaar: {'linked' if self.aadhaar_linked else 'not linked'}."
        )

    @classmethod
    def from_dict(cls, data: dict) -> "FarmerProfile":
        known = {
            "name","state","district","village","land_hectares","crop_type",
            "caste_category","gender","age","bank_account","aadhaar_linked",
            "kisan_credit_card","pm_kisan_registered","annual_income",
            "latitude","longitude","language_code","tags"
        }
        return cls(**{k: v for k, v in data.items() if k in known})

    @classmethod
    def from_json_file(cls, path) -> "FarmerProfile":
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Profile not found: {p}")
        with p.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        profile = cls.from_dict(data)
        logger.info("Loaded profile for '%s'", profile.name)
        return profile

    def save(self, path) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("w", encoding="utf-8") as fh:
            json.dump(self.to_dict(), fh, ensure_ascii=False, indent=2)


def sample_profile() -> FarmerProfile:
    return FarmerProfile(
        name="Ramesh Patil", state="Maharashtra", district="Nashik",
        village="Yeola", land_hectares=1.2, crop_type="sugarcane",
        caste_category="OBC", gender="male", age=42,
        bank_account=True, aadhaar_linked=True,
        kisan_credit_card=False, pm_kisan_registered=False,
        annual_income=85000, language_code="mr-IN",
    )