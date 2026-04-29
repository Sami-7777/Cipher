class Dashboard {
    constructor() {
        this.initElements();
        this.loadStats();
    }

    initElements() {
        this.totalScansEl = document.getElementById('total-scans');
        this.genuineCountEl = document.getElementById('genuine-count');
        this.fakeCountEl = document.getElementById('fake-count');
        this.scansTableEl = document.getElementById('scans-table');
        this.chartCtx = document.getElementById('statsChart').getContext('2d');
        this.chart = null;
    }

    async loadStats() {
        try {
            const response = await fetch('http://localhost:3000/stats');
            const stats = await response.json();
            this.updateStats(stats);
            this.updateChart(stats);
            this.updateScansTable(stats.recentScans);
        } catch (error) {
            console.error('Failed to load stats:', error);
            this.showError('Backend service unavailable');
        }
    }

    updateStats(stats) {
        this.totalScansEl.textContent = stats.totalScans || 0;
        this.genuineCountEl.textContent = stats.genuineCount || 0;
        this.fakeCountEl.textContent = stats.fakeCount || 0;
        // Fixed: Remove map reference from dashboard
        // document.getElementById('fake-count-map').textContent = 
        //     `${stats.fakeCount || 0} fake detections`;
    }

    updateChart(stats) {
        if (this.chart) {
            this.chart.destroy();
        }

        this.chart = new Chart(this.chartCtx, {
            type: 'pie',
            data: {
                labels: ['Genuine', 'Fake'],
                datasets: [{
                    data: [stats.genuineCount || 0, stats.fakeCount || 0],
                    backgroundColor: ['#10b981', '#ef4444']
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    updateScansTable(scans) {
        if (!scans || scans.length === 0) {
            this.scansTableEl.innerHTML = '<p>No scan data available</p>';
            return;
        }

        const tableHTML = `
            <table>
                <thead>
                    <tr>
                        <th>Medicine</th>
                        <th>Status</th>
                        <th>Batch</th>
                        <th>Time</th>
                    </tr>
                </thead>
                <tbody>
                    ${scans.slice(0, 10).map(scan => `
                        <tr>
                            <td>${scan.medicineName || 'Unknown'}</td>
                            <td>
                                ${scan.isGenuine ? 
                                    '<span class="status genuine">✅ Genuine</span>' : 
                                    '<span class="status fake">❌ Fake</span>'}
                            </td>
                            <td>${scan.batchNumber || 'N/A'}</td>
                            <td>${new Date(scan.timestamp).toLocaleString()}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        this.scansTableEl.innerHTML = tableHTML;
    }

    showError(message) {
        this.scansTableEl.innerHTML = `<p style="color: red;">${message}</p>`;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new Dashboard();
    
    // Refresh stats every 30 seconds
    setInterval(() => {
        new Dashboard().loadStats();
    }, 30000);
});
