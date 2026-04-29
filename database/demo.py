from database.database import MedicineDatabase
from datetime import datetime

db = MedicineDatabase()

print("\n" + "="*70)
print(" 🏥 COUNTERFEIT MEDICINE DETECTION SYSTEM - LIVE DEMO")
print("="*70)

print("\n[1] ✅ GENUINE MEDICINE")
print("    Scanning Paracetamol 500mg (MED003) for the FIRST time in Chennai...")
result = db.check_duplicate_scan("MED003", "Chennai", datetime.now())
print(f"    Result: {result['status']} ✅")
print(f"    Risk Score: {result['risk_score']}/100")
print(f"    Reason: {result['reason']}")

print("\n[2] ⚠️ CLONED QR CODE (Our Key Feature!)")
print("    Same QR (MED001) already scanned in Chennai & Mumbai.")
print("    Now scanning in KOLKATA (new city)...")
db.log_scan("MED001", "Kolkata", 22.5726, 88.3639, "demo_device")
result = db.check_duplicate_scan("MED001", "Kolkata", datetime.now())
print(f"    Result: {result['status']} ⚠️")
print(f"    Risk Score: {result['risk_score']}/100")
print(f"    Reason: {result['reason']}")

print("\n[3] ❌ LIKELY FAKE (Over-scanned)")
print("    Scanning Azithromycin 500mg (MED002) which has 15+ scans already...")
result = db.check_duplicate_scan("MED002", "Delhi", datetime.now())
print(f"    Result: {result['status']} ❌")
print(f"    Risk Score: {result['risk_score']}/100")
print(f"    Reason: {result['reason']}")

print("\n" + "="*70)
print(" ✅ System detects counterfeit medicines EVEN WITH VALID QR CODES!")
print("    by analyzing scan behavior across locations and time.")
print("    Works OFFLINE for rural areas!")
print("="*70 + "\n")