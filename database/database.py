import sqlite3
from datetime import datetime
from typing import Dict, List, Optional

class MedicineDatabase:
    def __init__(self, db_path: str = "medicines.db"):
        self.db_path = db_path
        self.init_tables()
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_tables(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS medicines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                qr_code TEXT UNIQUE NOT NULL,
                brand_name TEXT NOT NULL,
                generic_name TEXT,
                manufacturer TEXT NOT NULL,
                manufacturing_date DATE,
                expiry_date DATE NOT NULL,
                batch_number TEXT NOT NULL,
                mrp DECIMAL(10,2),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scan_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                qr_code TEXT NOT NULL,
                location_city TEXT NOT NULL,
                location_lat REAL,
                location_long REAL,
                scan_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                device_id TEXT,
                is_offline BOOLEAN DEFAULT FALSE,
                synced BOOLEAN DEFAULT FALSE
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS risk_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                qr_code TEXT NOT NULL,
                risk_score INTEGER NOT NULL,
                risk_level TEXT NOT NULL,
                reason TEXT,
                calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_chain (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                block_index INTEGER UNIQUE NOT NULL,
                block_hash TEXT UNIQUE NOT NULL,
                previous_hash TEXT NOT NULL,
                scan_log_id INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_scan_qr ON scan_logs(qr_code)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_scan_timestamp ON scan_logs(scan_timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_scan_city ON scan_logs(location_city)")
        
        conn.commit()
        conn.close()
        print("Database tables created successfully!")
    
    def add_medicine(self, qr_code, brand_name, manufacturer, expiry_date, batch_number, **kwargs):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO medicines (qr_code, brand_name, manufacturer, expiry_date, batch_number, generic_name, manufacturing_date, mrp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (qr_code, brand_name, manufacturer, expiry_date, batch_number, kwargs.get("generic_name"), kwargs.get("manufacturing_date"), kwargs.get("mrp")))
            conn.commit()
            return {"success": True, "message": "Medicine added"}
        except sqlite3.IntegrityError:
            return {"success": False, "message": "QR code already exists"}
        finally:
            conn.close()
    
    def check_duplicate_scan(self, qr_code, location_city, scan_timestamp=None):
        if scan_timestamp is None:
            scan_timestamp = datetime.now()
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT location_city, scan_timestamp FROM scan_logs 
            WHERE qr_code = ? ORDER BY scan_timestamp DESC LIMIT 20
        """, (qr_code,))
        previous_scans = cursor.fetchall()
        conn.close()
        
        if len(previous_scans) == 0:
            return {"status": "Genuine", "risk_score": 0, "reason": "First scan of this QR code"}
        
        locations = [scan[0] for scan in previous_scans]
        if location_city not in locations:
            latest_scan_time = datetime.strptime(previous_scans[0][1], "%Y-%m-%d %H:%M:%S")
            time_diff_hours = (scan_timestamp - latest_scan_time).total_seconds() / 3600
            if time_diff_hours < 24:
                return {"status": "Suspicious", "risk_score": 70, "reason": f"QR scanned in {locations[0]} {time_diff_hours:.1f}h ago, now in {location_city}. Possible QR cloning!"}
        
        if len(previous_scans) >= 10:
            return {"status": "Likely Fake", "risk_score": 90, "reason": f"QR scanned {len(previous_scans)} times (normal medicines scanned 1-3 times)"}
        
        return {"status": "Genuine", "risk_score": 10, "reason": f"Normal scan pattern ({len(previous_scans)} previous scans)"}
    
    def log_scan(self, qr_code, location_city, lat=None, long=None, device_id=None, is_offline=False):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO scan_logs (qr_code, location_city, location_lat, location_long, device_id, is_offline)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (qr_code, location_city, lat, long, device_id, is_offline))
        conn.commit()
        scan_id = cursor.lastrowid
        conn.close()
        return {"success": True, "scan_id": scan_id}
    
    def get_medicine_by_qr(self, qr_code):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM medicines WHERE qr_code = ?", (qr_code,))
        result = cursor.fetchone()
        conn.close()
        return dict(result) if result else None
    
    def get_scan_history(self, qr_code):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM scan_logs WHERE qr_code = ? ORDER BY scan_timestamp DESC", (qr_code,))
        results = cursor.fetchall()
        conn.close()
        return [dict(row) for row in results]
    
    def seed_demo_data(self):
        print("Seeding demo data...")
        demo_medicines = [
            ("MED001", "Paracetamol 500mg", "Sun Pharma", "2027-01-14", "SP25001", "Paracetamol", "2025-01-15", 25.00),
            ("MED002", "Azithromycin 500mg", "Cipla", "2026-05-31", "CI24002", "Azithromycin", "2024-06-01", 85.00),
            ("MED003", "Metformin 500mg", "Dr. Reddy's", "2027-03-09", "DR25003", "Metformin", "2025-03-10", 45.00),
            ("MED004", "Amoxicillin 250mg", "Lupin", "2026-09-19", "LU24004", "Amoxicillin", "2024-09-20", 60.00),
            ("MED005", "Diclofenac Gel", "Glenmark", "2027-01-31", "GL25005", "Diclofenac", "2025-02-01", 120.00),
        ]
        
        for med in demo_medicines:
            self.add_medicine(med[0], med[1], med[2], med[3], med[4], generic_name=med[5], manufacturing_date=med[6], mrp=med[7])
        
        print(f"Added {len(demo_medicines)} demo medicines")
        
        self.log_scan("MED001", "Chennai", 13.0827, 80.2707, "device_demo_1", False)
        print("Scenario 1 seeded: MED001 first scan in Chennai")
        
        from datetime import timedelta
        now = datetime.now()
        later = now - timedelta(hours=2)
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO scan_logs (qr_code, location_city, scan_timestamp, is_offline) VALUES (?, ?, ?, ?)", ("MED001", "Mumbai", later.strftime("%Y-%m-%d %H:%M:%S"), False))
        conn.commit()
        conn.close()
        print("Scenario 2 seeded: MED001 cloned in Mumbai")
        
        for i in range(15):
            scan_time = now - timedelta(minutes=i*10)
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO scan_logs (qr_code, location_city, scan_timestamp, is_offline) VALUES (?, ?, ?, ?)", ("MED002", "Delhi", scan_time.strftime("%Y-%m-%d %H:%M:%S"), False))
            conn.commit()
            conn.close()
        print("Scenario 3 seeded: MED002 scanned 15 times")

if __name__ == "__main__":
    print("Creating medicine database...")
    db = MedicineDatabase()
    db.seed_demo_data()
    
    print("\n" + "="*50)
    print("TESTING DUPLICATE DETECTION")
    print("="*50)
    
    print("\nTest 1: First scan of MED003")
    print(db.check_duplicate_scan("MED003", "Bangalore", datetime.now()))
    
    print("\nTest 2: MED001 cloned (Mumbai after Chennai)")
    print(db.check_duplicate_scan("MED001", "Mumbai", datetime.now()))
    
    print("\nTest 3: MED002 scanned 15 times")
    print(db.check_duplicate_scan("MED002", "Delhi", datetime.now()))
    
    print("\n" + "="*50)
    print("Database ready for hackathon!")
    print("="*50)