from datetime import date, datetime
import json, os

SCAN_LOG_FILE = "scan_logs.json"

def load_logs():
    if not os.path.exists(SCAN_LOG_FILE):
        return []
    with open(SCAN_LOG_FILE) as f:
        return json.load(f)

def save_log(entry: dict):
    logs = load_logs()
    logs.append(entry)
    with open(SCAN_LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)

def calculate_risk(qr_code: str, city: str, medicine: dict) -> dict:
    logs = load_logs()
    prev_scans = [s for s in logs if s["qr_code"] == qr_code]

    score = 0
    reasons = []
    flags = []

    if not medicine.get("registered", False):
        score += 90
        reasons.append("QR code not found in manufacturer database")
        flags.append("UNREGISTERED_QR")
        return build_result(score, reasons, flags, len(prev_scans) + 1)

    prev_cities = list({s["city"] for s in prev_scans})
    all_cities = list({*prev_cities, city})
    if len(all_cities) > 1:
        score += 40
        reasons.append(f"Same QR detected in multiple cities: {', '.join(all_cities)}")
        flags.append("MULTI_CITY_DUPLICATE")

    scan_count = len(prev_scans) + 1
    max_allowed = medicine.get("max_scans", 3)
    if scan_count > max_allowed:
        score += 35
        reasons.append(f"Scanned {scan_count} times — limit is {max_allowed}")
        flags.append("OVERSCAN")

    try:
        expiry = datetime.strptime(medicine["expiry"] + "-01", "%Y-%m-%d").date()
        if expiry < date.today():
            score += 20
            reasons.append(f"Medicine expired on {medicine['expiry']}")
            flags.append("EXPIRED")
    except Exception:
        pass

    if city != medicine.get("origin_city") and len(prev_scans) == 0:
        score += 10
        reasons.append(f"Scan location ({city}) differs from registered origin ({medicine['origin_city']})")
        flags.append("ORIGIN_MISMATCH")

    score = min(score, 99)
    return build_result(score, reasons, flags, scan_count, all_cities)

def build_result(score, reasons, flags, scan_count, cities=None):
    if score < 15:
        status, label = "GENUINE", "Genuine"
    elif score < 55:
        status, label = "SUSPICIOUS", "Suspicious"
    else:
        status, label = "FAKE", "Likely Fake"

    return {
        "status": status,
        "label": label,
        "risk_score": score,
        "reasons": reasons,
        "flags": flags,
        "scan_count": scan_count,
        "cities_detected": cities or [],
    }