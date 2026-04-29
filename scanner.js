class MedicineScanner {
    constructor() {
        this.html5QrCode = null;
        this.currentLocation = null;
        this.initElements();
        this.bindEvents();
        this.checkOfflineStatus();
        this.getCurrentLocation();
    }

    initElements() {
        this.reader = document.getElementById('reader');
        this.result = document.getElementById('result');
        this.status = document.getElementById('status');
        this.medicineName = document.getElementById('medicine-name');
        this.batchInfo = document.getElementById('batch-info');
        this.expiryDate = document.getElementById('expiry-date');
        this.scanAgainBtn = document.getElementById('scan-again');
        this.manualInput = document.getElementById('manual-qr-input');
        this.verifyManualBtn = document.getElementById('verify-manual');
        this.loadingSpinner = document.getElementById('loading-spinner');
        this.locationInfo = document.getElementById('location-info');
        this.riskScoreEl = document.getElementById('risk-score');
        this.reasonEl = document.getElementById('reason');
        this.modal = document.getElementById('alert-modal');
        this.modalMessage = document.getElementById('modal-message');
    }

    bindEvents() {
        this.scanAgainBtn.addEventListener('click', () => this.scanAgain());
        this.verifyManualBtn.addEventListener('click', () => this.verifyManual());
        document.querySelector('.close-modal').addEventListener('click', () => this.closeModal());
        window.addEventListener('click', (e) => {
            if (e.target === this.modal) this.closeModal();
        });
    }

    checkOfflineStatus() {
        if (!navigator.onLine) {
            const banner = document.createElement('div');
            banner.className = 'offline-banner';
            banner.textContent = '⚠️ OFFLINE MODE - Results cached locally';
            document.querySelector('.scanner-card').prepend(banner);
        }
    }

    async getCurrentLocation() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (pos) => {
                    this.currentLocation = {
                        lat: pos.coords.latitude,
                        lng: pos.coords.longitude
                    };
                    this.updateLocationUI();
                },
                () => console.log('Location access denied')
            );
        }
    }

    updateLocationUI() {
        if (this.currentLocation && this.locationInfo) {
            this.locationInfo.textContent = `📍 Lat: ${this.currentLocation.lat.toFixed(4)}, Lng: ${this.currentLocation.lng.toFixed(4)}`;
        }
    }

    async startScanner() {
        try {
            this.html5QrCode = new Html5Qrcode('reader');
            const config = { fps: 10, qrbox: { width: 250, height: 250 } };
            
            await this.html5QrCode.start(
                { facingMode: 'environment' },
                config,
                this.onScanSuccess.bind(this),
                this.onScanError.bind(this)
            );
        } catch (err) {
            console.error('Scanner init failed:', err);
            this.showManualInput();
        }
    }

    showManualInput() {
        this.manualInput.classList.remove('hidden');
    }

    onScanSuccess(decodedText) {
        console.log('QR Code scanned:', decodedText);
        this.verifyMedicine(decodedText, 'camera');
        this.html5QrCode.stop();
    }

    onScanError(error) {
        // Silent error handling
    }

    verifyManual() {
        const qrCode = this.manualInput.value.trim();
        if (qrCode) {
            this.manualInput.value = '';
            this.verifyMedicine(qrCode, 'manual');
        }
    }

    async verifyMedicine(qrData, source) {
        this.showLoading();
        
        try {
            const payload = {
                qrCode: qrData,
                location: this.currentLocation,
                source: source
            };

            const response = await fetch('http://localhost:3000/verify', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const result = await response.json();
            this.hideLoading();
            this.displayResult(result);
            this.saveScanHistory(qrData, result);
            
            if (!result.isGenuine || result.riskScore < 80) {
                this.showSmartAlert(result);
            }
        } catch (error) {
            this.hideLoading();
            this.handleOffline(qrData);
        }
    }

    showLoading() {
        this.loadingSpinner.classList.remove('hidden');
        this.result.classList.add('hidden');
    }

    hideLoading() {
        this.loadingSpinner.classList.add('hidden');
    }

    displayResult(data) {
        const riskClass = this.getRiskClass(data.riskScore || 100);
        
        this.status.textContent = data.isGenuine ? '✅ GENUINE MEDICINE' : '❌ COUNTERFEIT DETECTED';
        this.status.parentElement.className = `result-card ${data.isGenuine ? 'genuine' : 'fake'}`;
        
        this.medicineName.textContent = `Medicine: ${data.medicineName || 'Unknown'}`;
        this.batchInfo.textContent = `Batch: ${data.batchNumber || 'N/A'}`;
        this.expiryDate.textContent = `Expiry: ${data.expiryDate || 'N/A'}`;
        
        // Risk Score
        this.riskScoreEl.textContent = data.riskScore ? `${data.riskScore}%` : 'N/A';
        this.riskScoreEl.className = `risk-badge ${riskClass}`;
        
        // Reason
        this.reasonEl.textContent = data.reason || 'Verification completed';
        
        this.result.classList.remove('hidden');
        this.scanAgainBtn.classList.remove('hidden');
    }

    getRiskClass(score) {
        if (score >= 90) return 'risk-safe';
        if (score >= 70) return 'risk-warning';
        return 'risk-danger';
    }

    showSmartAlert(data) {
        let message = data.isGenuine 
            ? `⚠️ Suspicious Risk Score: ${data.riskScore || 0}%` 
            : '🚨 COUNTERFEIT MEDICINE DETECTED!';
        
        if (data.reason) {
            message += `\\nReason: ${data.reason}`;
        }
        
        this.modalMessage.textContent = message;
        this.modal.style.display = 'block';
    }

    closeModal() {
        this.modal.style.display = 'none';
    }

    handleOffline(qrData) {
        this.displayError('Offline - Check cached results in History');
        this.saveScanHistory(qrData, { isGenuine: null, riskScore: 0, reason: 'Offline verification' });
    }

    displayError(message) {
        this.status.textContent = '⚠️ Verification Failed';
        this.status.parentElement.className = 'result-card fake';
        this.medicineName.textContent = message;
        this.riskScoreEl.textContent = '--';
        this.reasonEl.textContent = 'Check connection';
        this.result.classList.remove('hidden');
        this.scanAgainBtn.classList.remove('hidden');
    }

    saveScanHistory(qrData, result) {
        const history = JSON.parse(localStorage.getItem('scanHistory') || '[]');
        history.unshift({
            qrCode: qrData,
            result: result,
            timestamp: new Date().toISOString(),
            location: this.currentLocation
        });
        localStorage.setItem('scanHistory', JSON.stringify(history.slice(0, 50))); // Keep last 50
    }

    scanAgain() {
        this.result.classList.add('hidden');
        this.scanAgainBtn.classList.add('hidden');
        this.manualInput.classList.add('hidden');
        this.startScanner();
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    new MedicineScanner().startScanner();
});
