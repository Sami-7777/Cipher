class FakeMedicineMap {
    constructor() {
        this.map = null;
        this.markers = L.layerGroup();
        this.initMap();
        this.loadFakeLocations();
    }

    initMap() {
        // Center on a default location (can be adjusted)
        this.map = L.map('map').setView([20.5937, 78.9629], 5); // India center

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(this.map);

        // Add search control
        this.map.addControl(L.control.zoom({
            zoomInTitle: 'Zoom in',
            zoomOutTitle: 'Zoom out'
        }));
    }

    async loadFakeLocations() {
        try {
            const response = await fetch('http://localhost:3000/fake-locations');
            const locations = await response.json();
            this.addMarkers(locations);
            document.getElementById('fake-count-map').textContent = 
                `${locations.length} fake detections on map`;
        } catch (error) {
            console.error('Failed to load fake locations:', error);
            document.getElementById('fake-count-map').textContent = 
                'Backend service unavailable';
        }
    }

    addMarkers(locations) {
        this.markers.clearLayers();

        locations.forEach(location => {
            if (location.lat && location.lng) {
                const marker = L.marker([location.lat, location.lng])
                    .bindPopup(`
                        <div style="min-width: 200px;">
                            <h4 style="color: #ef4444; margin-bottom: 0.5rem;">🚨 FAKE MEDICINE</h4>
                            <p><strong>Medicine:</strong> ${location.medicineName || 'Unknown'}</p>
                            <p><strong>Batch:</strong> ${location.batchNumber || 'N/A'}</p>
                            <p><strong>Location:</strong> ${location.location || 'Unknown'}</p>
                            <p><strong>Time:</strong> ${new Date(location.timestamp).toLocaleString()}</p>
                        </div>
                    `)
                    .addTo(this.markers);
            }
        });

        this.markers.addTo(this.map);
        
        if (locations.length > 0) {
            this.map.fitBounds(this.markers.getBounds().pad(0.1));
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new FakeMedicineMap();
    
    // Refresh map data every 60 seconds
    setInterval(() => {
        new FakeMedicineMap().loadFakeLocations();
    }, 60000);
});
