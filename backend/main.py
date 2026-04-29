from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from backend.models import ScanRequest, ScanResponse, MedicineInfo
from backend.database import MEDICINES
from backend.logic import calculate_risk, save_log

app = FastAPI(title="MedVerify API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "MedVerify backend running"}

@app.post("/verify", response_model=ScanResponse)
def verify_medicine(req: ScanRequest):
    medicine = MEDICINES.get(req.qr_code, {"registered": False})
    result = calculate_risk(req.qr_code, req.city, medicine)

    save_log({
        "qr_code": req.qr_code,
        "city": req.city,
        "timestamp": datetime.utcnow().isoformat(),
        "status": result["status"],
        "risk_score": result["risk_score"],
        "offline": req.offline,
    })

    med_info = None
    if medicine.get("registered"):
        med_info = MedicineInfo(
            name=medicine["name"],
            manufacturer=medicine["manufacturer"],
            batch=medicine["batch"],
            expiry=medicine["expiry"],
            origin_city=medicine["origin_city"],
        )

    return ScanResponse(**result, medicine=med_info, offline_mode=req.offline)

@app.get("/scans")
def get_scan_history():
    from backend.logic import load_logs
    return {"scans": load_logs()}

@app.delete("/scans/reset")
def reset_logs():
    import json
    with open("scan_logs.json", "w") as f:
        json.dump([], f)
    return {"message": "Scan logs cleared"}