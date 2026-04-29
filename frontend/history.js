class ScanHistory {
    constructor() {
        this.initElements();
        this.loadHistory();
        this.bindEvents();
    }

    initElements() {
        this.totalHistoryEl = document.getElementById('total-history');
        this.historyTableEl = document.getElementById('history-table');
        this.clearBtn = document.getElementById('clear-history');
    }

    bindEvents() {
        this.clearBtn.addEventListener('click', () => {
            if (confirm('Clear all scan history? This cannot be undone.')) {
                localStorage.removeItem('scanHistory');
                this.loadHistory();
            }
        });
    }

    loadHistory() {
        const history = JSON.parse(localStorage.getItem('scanHistory') || '[]');
        
        this.totalHistoryEl.textContent = history.length;
        
        if (history.length === 0) {
            this.historyTableEl.innerHTML = '<p>No scan history available. Start scanning!</p>';
            return;
        }

        const tableHTML = `
            <table>
                <thead>
                    <tr>
                        <th>Date/Time</th>
                        <th>QR Code</th>
                        <th>Status</th>
                        <th>Risk Score</th>
                        <th>Reason</th>
                        <th>Location</th>
                    </tr>
                </thead>
                <tbody>
                    ${history.map(scan => {
                        const result = scan.result;
                        const riskClass = result.riskScore >= 90 ? 'status genuine' : 
                                        result.riskScore >= 70 ? 'status' : 'status fake';
                        
                        return `
                            <tr>
                                <td>${new Date(scan.timestamp).toLocaleString()}</td>
                                <td>${scan.qrCode.slice(0, 20)}${scan.qrCode.length > 20 ? '...' : ''}</td>
                                <td>
                                    <span class="${result.isGenuine === null ? 'status' : 
                                        result.isGenuine ? 'status genuine' : 'status fake'}">
                                        ${result.isGenuine === null ? '💾 Cached' : 
                                          result.isGenuine ? '✅ Genuine' : '❌ Fake'}
                                    </span>
                                </td>
                                <td>${result.riskScore || 0}%</td>
                                <td>${result.reason || 'N/A'}</td>
                                <td>${scan.location ? 
                                    `📍 ${scan.location.lat?.toFixed(4)}, ${scan.location.lng?.toFixed(4)}` : 'N/A'}</td>
                            </tr>
                        `;
                    }).join('')}
                </tbody>
            </table>
        `;
        
        this.historyTableEl.innerHTML = tableHTML;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new ScanHistory();
    
    // Auto-refresh every 10 seconds
    setInterval(() => {
        document.querySelector('.ScanHistory')?.loadHistory();
    }, 10000);
});

