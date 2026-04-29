# Counterfeit Drug Detection System

## 📌 Problem
Fake medicines are a serious issue, especially in India. Many systems only check if a QR code is valid, but counterfeit drugs can reuse valid QR codes. This makes basic verification unreliable.

---

## 💡 Our Idea
Instead of just verifying QR codes, our system checks **how the QR code behaves**.

We detect fake medicines by analyzing:
- Multiple scans of the same QR
- Different locations for the same product
- Unusual scan patterns

So even if the QR is valid, we can still flag it as suspicious.

---

## 🚀 Features

- QR Code Verification  
- Duplicate Scan Detection  
- Location-based Fraud Detection  
- Risk Score (Genuine / Suspicious / Likely Fake)  
- Offline Mode (basic verification without internet)  

---

## 🧠 How It Works

1. User scans a QR code  
2. App sends data to backend (QR + location)  
3. Backend checks:
   - Is QR valid?
   - Has it been scanned before?
   - Is location different?
4. System generates a risk score  
5. Result is shown to user  

---

## ⚙️ Tech Stack

- **Frontend:** React / Basic Web UI  
- **Backend:** FastAPI (Python)  
- **Database:** In-memory / JSON  
- **Offline Support:** Local storage  

---

## 📂 Project Structure
