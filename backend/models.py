from pydantic import BaseModel
from typing import List, Optional

class ScanRequest(BaseModel):
    qr_code: str
    city: str
    offline: bool = False

class MedicineInfo(BaseModel):
    name: str
    manufacturer: str
    batch: str
    expiry: str
    origin_city: str

class ScanResponse(BaseModel):
    status: str
    label: str
    risk_score: int
    reasons: List[str]
    flags: List[str]
    scan_count: int
    cities_detected: List[str]
    medicine: Optional[MedicineInfo] = None
    offline_mode: bool = False