/* AI Safety Monitoring System - Main JavaScript */

document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ Initializing dashboard...');
    
    // Initialize sidebar menu
    initializeSidebar();
    
    // Load dashboard by default
    loadPage('dashboard');
});

// Initialize sidebar navigation
function initializeSidebar() {
    const sidebarLinks = document.querySelectorAll('.sidebar-menu a');
    
    sidebarLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const page = this.getAttribute('data-page');
            
            // Update active state
            sidebarLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
            
            // Load page
            loadPage(page);
        });
    });
}

// Load page content
function loadPage(page) {
    // Hide all pages
    document.querySelectorAll('[id$="-page"]').forEach(p => {
        p.classList.remove('active');
    });
    
    // Show selected page
    const pageElement = document.getElementById(`${page}-page`);
    if (pageElement) {
        pageElement.classList.add('active');
        
        // Call page-specific function
        if (typeof window[`load${capitalizeFirstLetter(page)}Page`] === 'function') {
            window[`load${capitalizeFirstLetter(page)}Page`]();
        }
    }
}

// Load dashboard page
function loadDashboardPage() {
    console.log('📊 Loading dashboard...');
    loadDashboardStats();
}

// Load dashboard statistics
function loadDashboardStats() {
    // Fetch monitoring status (no auth required in development)
    fetch('/api/monitoring/status')
    .then(response => {
        if (!response.ok) throw new Error('Network response was not ok');
        return response.json();
    })
    .then(data => {
        console.log('✅ Dashboard data:', data);
        if (data.monitoring_status) {
            updateDashboardUI(data.monitoring_status);
        }
    })
    .catch(error => console.error('❌ Error loading dashboard:', error));
}

// Update dashboard UI with data
function updateDashboardUI(data) {
    try {
        // Update monitoring status
        const statusElement = document.getElementById('monitoring-status-text');
        if (statusElement) {
            if (data.monitoring_enabled) {
                statusElement.textContent = 'Active';
                statusElement.classList.remove('badge-danger');
                statusElement.classList.add('badge-success');
                document.getElementById('btn-start').style.display = 'none';
                document.getElementById('btn-stop').style.display = 'inline-block';
            } else {
                statusElement.textContent = 'Inactive';
                statusElement.classList.remove('badge-success');
                statusElement.classList.add('badge-danger');
                document.getElementById('btn-start').style.display = 'inline-block';
                document.getElementById('btn-stop').style.display = 'none';
            }
        }
        
        // Update incident count
        const incidentElement = document.querySelector('[data-stat="total-incidents"]');
        if (incidentElement) {
            incidentElement.textContent = data.total_incidents || 0;
        }
        
        // Update detection count
        const detectionElement = document.querySelector('[data-stat="total-detections"]');
        if (detectionElement) {
            detectionElement.textContent = data.total_detections || 0;
        }
        
        // Update camera count
        const cameraElement = document.getElementById('active-cameras');
        if (cameraElement) {
            cameraElement.textContent = data.connected_cameras || 0;
        }
        
        // Update frame count
        const frameElement = document.getElementById('total-frames');
        if (frameElement) {
            frameElement.textContent = data.total_frames_captured || 0;
        }
        
        // Update last update time
        const updateElement = document.getElementById('last-update');
        if (updateElement) {
            updateElement.textContent = new Date().toLocaleTimeString();
        }
    } catch (error) {
        console.error('❌ Error updating dashboard UI:', error);
    }
}

// Load monitoring page
function loadMonitoringPage() {
    console.log('🎥 Loading live monitoring...');
    loadCameraFeeds();
}

// Load camera feeds
function loadCameraFeeds() {
    fetch('/api/monitoring/cameras')
    .then(response => response.json())
    .then(data => {
        console.log('✅ Cameras:', data);
        if (data.cameras) {
            displayCameras(data.cameras);
        }
    })
    .catch(error => console.error('❌ Error loading cameras:', error));
}

// Display camera feeds
function displayCameras(cameras) {
    const monitoringGrid = document.querySelector('.monitoring-grid');
    if (!monitoringGrid) return;
    
    if (cameras.length === 0) {
        monitoringGrid.innerHTML = '<p>No cameras connected</p>';
        return;
    }
    
    monitoringGrid.innerHTML = cameras.map(camera => `
        <div class="camera-card">
            <div class="camera-stream">
                <span>Camera ${camera.id}: ${camera.location || 'Loading...'}</span>
            </div>
            <div class="camera-info">
                <div class="camera-title">${camera.location || 'Camera ' + camera.id}</div>
                <div class="camera-status">
                    <span class="status-indicator online"></span>
                    Active
                </div>
            </div>
        </div>
    `).join('');
}

// Load incidents page
function loadIncidentsPage() {
    console.log('📋 Loading incidents...');
    loadIncidents();
}

// Load incidents list
function loadIncidents() {
    fetch('/api/incidents')
    .then(response => response.json())
    .then(data => {
        console.log('📋 Incidents:', data);
    })
    .catch(error => console.error('❌ Error loading incidents:', error));
}

// Load analytics page
function loadAnalyticsPage() {
    console.log('📈 Loading analytics...');
    loadAnalytics();
}

// Load analytics data
function loadAnalytics() {
    fetch('/api/analytics/dashboard')
    .then(response => response.json())
    .then(data => {
        console.log('📈 Analytics:', data);
    })
    .catch(error => console.error('❌ Error loading analytics:', error));
}

// Load settings page
function loadSettingsPage() {
    console.log('⚙️  Loading settings...');
}

// Control monitoring
function startMonitoring() {
    fetch('/api/monitoring/start', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        console.log('✅ Monitoring started:', data);
        loadDashboardStats();
    })
    .catch(error => console.error('❌ Error starting monitoring:', error));
}

function stopMonitoring() {
    fetch('/api/monitoring/stop', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        console.log('⏹️  Monitoring stopped:', data);
        loadDashboardStats();
    })
    .catch(error => console.error('❌ Error stopping monitoring:', error));
}

// Refresh page content
function refreshPage() {
    const activePage = document.querySelector('[id$="-page"].active');
    if (activePage) {
        const page = activePage.id.replace('-page', '');
        loadPage(page);
    }
}

// Utility function to capitalize first letter
function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

// Export monitoring data
function exportReport() {
    alert('Report export feature coming soon!');
}

// Clear alerts
function clearAlerts() {
    alert('Clearing alerts...');
}

// Save settings
function saveSettings() {
    const frameRate = document.getElementById('frame-rate').value;
    const resolution = document.getElementById('resolution').value;
    alert(`Settings saved!\nFrame Rate: ${frameRate} FPS\nResolution: ${resolution}`);
}

// Save detection settings
function saveDetectionSettings() {
    const helmetThreshold = document.getElementById('helmet-threshold').value;
    const confidenceThreshold = document.getElementById('confidence-threshold').value;
    
    document.getElementById('helmet-threshold-value').textContent = helmetThreshold;
    document.getElementById('confidence-threshold-value').textContent = confidenceThreshold;
    
    alert(`Detection settings saved!\nHelmet Threshold: ${helmetThreshold}\nConfidence: ${confidenceThreshold}`);
}

// Save alert configuration
function saveAlertConfig() {
    const threshold = document.getElementById('alert-threshold').value;
    const soundAlert = document.getElementById('sound-alert').checked;
    const emailAlert = document.getElementById('email-alert').checked;
    alert(`Alert config saved!\nThreshold: ${threshold}s\nSound: ${soundAlert ? 'Enabled' : 'Disabled'}\nEmail: ${emailAlert ? 'Enabled' : 'Disabled'}`);
}

// Generate report
function generateReport() {
    alert('Report generation coming soon!');
}

// Periodic data refresh
setInterval(() => {
    const activePage = document.querySelector('[id$="-page"].active');
    if (activePage && activePage.id === 'dashboard-page') {
        loadDashboardStats();
    }
}, 10000); // Refresh every 10 seconds
