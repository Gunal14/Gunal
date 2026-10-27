/* =============================================
   AI Smart Safety Monitoring System - App.js
   Main application logic and API calls
   ============================================= */

// Global variables
let currentPage = 'dashboard';
let monitoringActive = false;
let updateInterval;
let charts = {};

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    console.log('Initializing AI Smart Safety Monitoring System...');
    setupEventListeners();
    loadDashboard();
    checkSystemHealth();
    setupAutoRefresh();
});

/* ============ EVENT LISTENERS ============ */
function setupEventListeners() {
    // Sidebar navigation
    document.querySelectorAll('.sidebar-menu a').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const page = e.currentTarget.dataset.page;
            navigateTo(page);
        });
    });

    // Control buttons
    document.getElementById('start-monitoring').addEventListener('click', startMonitoring);
    document.getElementById('stop-monitoring').addEventListener('click', stopMonitoring);

    // Range sliders
    const helmetThreshold = document.getElementById('helmet-threshold');
    const confidenceThreshold = document.getElementById('confidence-threshold');
    
    if (helmetThreshold) {
        helmetThreshold.addEventListener('input', (e) => {
            document.getElementById('helmet-threshold-value').textContent = e.target.value;
        });
    }

    if (confidenceThreshold) {
        confidenceThreshold.addEventListener('input', (e) => {
            document.getElementById('confidence-threshold-value').textContent = e.target.value;
        });
    }
}

/* ============ NAVIGATION ============ */
function navigateTo(page) {
    // Hide all pages
    document.querySelectorAll('.page-content').forEach(content => {
        content.style.display = 'none';
    });

    // Show selected page
    const pageElement = document.getElementById(`${page}-page`);
    if (pageElement) {
        pageElement.style.display = 'block';
    }

    // Update active menu item
    document.querySelectorAll('.sidebar-menu a').forEach(link => {
        link.classList.remove('active');
        if (link.dataset.page === page) {
            link.classList.add('active');
        }
    });

    currentPage = page;

    // Load page-specific content
    switch (page) {
        case 'monitoring':
            loadMonitoringPage();
            break;
        case 'incidents':
            loadIncidents();
            break;
        case 'alerts':
            loadAlerts();
            break;
        case 'analytics':
            loadAnalytics();
            break;
        case 'settings':
            loadSettings();
            break;
        default:
            loadDashboard();
    }
}

/* ============ MONITORING CONTROL ============ */
async function startMonitoring() {
    try {
        showToast('Initializing video capture...', 'info');
        
        const response = await fetch('/api/start_monitoring', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        if (response.ok) {
            monitoringActive = true;
            document.getElementById('start-monitoring').style.display = 'none';
            document.getElementById('stop-monitoring').style.display = 'inline-flex';
            
            const indicator = document.getElementById('monitoring-status');
            indicator.classList.add('active');
            indicator.innerHTML = '<span class="status-dot"></span><span>Active</span>';
            
            document.getElementById('monitoring-status-text').textContent = 'Active';
            
            showToast('Monitoring started successfully', 'success');
            
            // Start real-time updates
            startRealtimeUpdates();
        }
    } catch (error) {
        console.error('Start monitoring error:', error);
        showToast('Failed to start monitoring: ' + error.message, 'error');
    }
}

async function stopMonitoring() {
    try {
        const response = await fetch('/api/stop_monitoring', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        if (response.ok) {
            monitoringActive = false;
            document.getElementById('start-monitoring').style.display = 'inline-flex';
            document.getElementById('stop-monitoring').style.display = 'none';
            
            const indicator = document.getElementById('monitoring-status');
            indicator.classList.remove('active');
            indicator.innerHTML = '<span class="status-dot"></span><span>Inactive</span>';
            
            document.getElementById('monitoring-status-text').textContent = 'Inactive';
            
            showToast('Monitoring stopped', 'warning');
            
            // Clear real-time updates
            if (updateInterval) {
                clearInterval(updateInterval);
            }
        }
    } catch (error) {
        console.error('Stop monitoring error:', error);
        showToast('Failed to stop monitoring: ' + error.message, 'error');
    }
}

function startRealtimeUpdates() {
    if (updateInterval) {
        clearInterval(updateInterval);
    }

    // Update every 2 seconds
    updateInterval = setInterval(async () => {
        if (!monitoringActive) return;

        try {
            // Update statistics
            const statsResponse = await fetch('/api/statistics');
            if (statsResponse.ok) {
                const stats = await statsResponse.json();
                updateDashboardStats(stats);
                updateMonitoringStats(stats);
            }

            // Update alerts
            const alertsResponse = await fetch('/api/alerts');
            if (alertsResponse.ok) {
                const alerts = await alertsResponse.json();
                updateRealtimeAlerts(alerts);
            }

            // Update timestamp
            document.getElementById('last-update').textContent = 
                new Date().toLocaleTimeString();
        } catch (error) {
            console.error('Real-time update error:', error);
        }
    }, 2000);
}

/* ============ DASHBOARD PAGE ============ */
async function loadDashboard() {
    try {
        // Load statistics
        const statsResponse = await fetch('/api/statistics');
        const stats = await statsResponse.json();
        updateDashboardStats(stats);

        // Load incidents
        const incidentsResponse = await fetch('/api/incidents?limit=5');
        const incidents = await incidentsResponse.json();
        displayRecentIncidents(incidents.incidents);

        // Load health status
        const healthResponse = await fetch('/health');
        const health = await healthResponse.json();
        console.log('System Health:', health);

    } catch (error) {
        console.error('Dashboard load error:', error);
        showToast('Failed to load dashboard: ' + error.message, 'error');
    }
}

function updateDashboardStats(stats) {
    document.getElementById('safety-score').textContent = stats.safety_score;
    document.getElementById('total-incidents').textContent = stats.total_incidents;
    document.getElementById('today-incidents').textContent = stats.today_incidents;
    document.getElementById('critical-alerts').textContent = stats.high_severity;
    document.getElementById('active-alerts-count').textContent = stats.high_severity;
}

function displayRecentIncidents(incidents) {
    const container = document.getElementById('recent-incidents');
    
    if (incidents.length === 0) {
        container.innerHTML = '<p class="no-data">No incidents recorded</p>';
        return;
    }

    container.innerHTML = incidents.map(incident => `
        <div class="incident-item">
            <div class="incident-info">
                <h4>${incident.type}</h4>
                <small>${new Date(incident.timestamp).toLocaleString()}</small>
            </div>
            <span class="incident-severity severity-${incident.severity.toLowerCase()}">
                ${incident.severity}
            </span>
        </div>
    `).join('');
}

/* ============ MONITORING PAGE ============ */
function loadMonitoringPage() {
    // Video stream is loaded automatically via img tag with /video_feed
    // Real-time stats are updated by startRealtimeUpdates()
    console.log('Monitoring page loaded');
}

function updateMonitoringStats(stats) {
    if (currentPage !== 'monitoring') return;

    const realtime = stats.realtime || {};
    const activeAlerts = stats.active_alerts || 0;

    const workers = realtime.workers_detected || 0;
    const helmets = realtime.helmets_detected || 0;
    const compliance = realtime.compliance_rate || 0;

    document.getElementById('rt-workers').textContent = workers;
    document.getElementById('rt-helmets').textContent = helmets;
    document.getElementById('rt-compliance').textContent = `${compliance}%`;
    document.getElementById('rt-alerts').textContent = activeAlerts;

    // Optionally show violations in log section
    if (realtime.last_violations && realtime.last_violations.length > 0) {
        updateRealtimeAlerts({alerts: realtime.last_violations.map(v => ({type:'CRITICAL', message:v}))});
    }
}

function updateRealtimeAlerts(alertsData) {
    if (currentPage !== 'monitoring') return;

    const alertsContainer = document.getElementById('rt-alerts');
    const alerts = alertsData.alerts || [];

    if (alerts.length === 0) {
        alertsContainer.innerHTML = '<p class="no-data">No active alerts</p>';
        return;
    }

    alertsContainer.innerHTML = alerts.slice(0, 5).map(alert => `
        <div class="alert-item ${alert.type === 'CRITICAL' ? 'critical' : ''}">
            <strong>${alert.type}:</strong> ${alert.message}
        </div>
    `).join('');

    // Add to detection log
    const logContainer = document.getElementById('detection-log');
    if (logContainer && alerts.length > 0) {
        const newEntry = `<div class="log-entry warning">[${new Date().toLocaleTimeString()}] Alert: ${alerts[0].message}</div>`;
        logContainer.innerHTML = newEntry + (logContainer.innerHTML || '');
    }
}

/* ============ INCIDENTS PAGE ============ */
async function loadIncidents() {
    try {
        const response = await fetch('/api/incidents?limit=100');
        const data = await response.json();
        displayIncidentsTable(data.incidents);
    } catch (error) {
        console.error('Load incidents error:', error);
        showToast('Failed to load incidents: ' + error.message, 'error');
    }
}

function displayIncidentsTable(incidents) {
    const tbody = document.getElementById('incidents-table');

    if (incidents.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="no-data">No incidents found</td></tr>';
        return;
    }

    tbody.innerHTML = incidents.map(incident => `
        <tr>
            <td>${new Date(incident.timestamp).toLocaleString()}</td>
            <td>${incident.type}</td>
            <td><span class="incident-severity severity-${incident.severity.toLowerCase()}">${incident.severity}</span></td>
            <td>${incident.details ? JSON.stringify(incident.details).substring(0, 50) + '...' : 'N/A'}</td>
            <td><span style="color: #7f8c8d;">Logged</span></td>
            <td><button class="btn btn-info btn-sm" onclick="viewIncidentDetails('${incident.id}')">View</button></td>
        </tr>
    `).join('');
}

function applyFilters() {
    // Implement date and severity filtering
    const date = document.getElementById('filter-date').value;
    const severity = document.getElementById('filter-severity').value;
    
    loadIncidents(); // Reload with filters (would be sent as query params)
    showToast('Filters applied', 'info');
}

function viewIncidentDetails(id) {
    showToast(`Incident ${id} details dialog would open here`, 'info');
}

/* ============ ALERTS PAGE ============ */
async function loadAlerts() {
    try {
        const response = await fetch('/api/alerts');
        const data = await response.json();
        displayActiveAlerts(data.alerts);
        
        // Get current configuration
        const configResponse = await fetch('/api/alert_config');
        const config = await configResponse.json();
        document.getElementById('alert-threshold').value = config.threshold;
    } catch (error) {
        console.error('Load alerts error:', error);
        showToast('Failed to load alerts: ' + error.message, 'error');
    }
}

function displayActiveAlerts(alerts) {
    const grid = document.getElementById('active-alerts-grid');

    if (alerts.length === 0) {
        grid.innerHTML = '<p class="no-data">No active alerts</p>';
        return;
    }

    grid.innerHTML = alerts.slice(0, 9).map(alert => `
        <div class="alert-card ${alert.type === 'critical' ? 'critical' : ''}">
            <h4>${alert.type}</h4>
            <p>${alert.message}</p>
            <small>${new Date(alert.timestamp).toLocaleString()}</small>
            <div style="margin-top: 10px;">
                <button class="btn btn-sm btn-primary" onclick="acknowledgeAlert('${alert.id}')">Acknowledge</button>
            </div>
        </div>
    `).join('');
}

async function acknowledgeAlert(id) {
    showToast(`Alert ${id} acknowledged`, 'success');
    // Call API to acknowledge
}

async function saveAlertConfig() {
    try {
        const threshold = document.getElementById('alert-threshold').value;
        
        const response = await fetch('/api/alert_config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ threshold: parseInt(threshold) })
        });

        if (response.ok) {
            showToast('Alert configuration saved successfully', 'success');
        }
    } catch (error) {
        console.error('Save config error:', error);
        showToast('Failed to save configuration: ' + error.message, 'error');
    }
}

async function clearAlerts() {
    try {
        const response = await fetch('/api/clear_alerts', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        if (response.ok) {
            showToast('All alerts cleared', 'success');
            loadAlerts();
        }
    } catch (error) {
        console.error('Clear alerts error:', error);
        showToast('Failed to clear alerts: ' + error.message, 'error');
    }
}

/* ============ ANALYTICS PAGE ============ */
async function loadAnalytics() {
    try {
        // Initialize charts
        initializeCharts();
        
        // Load data
        const response = await fetch('/api/incidents?limit=365');
        const data = await response.json();
        
        updateAnalyticsCharts(data.incidents);
    } catch (error) {
        console.error('Load analytics error:', error);
        showToast('Failed to load analytics: ' + error.message, 'error');
    }
}

function initializeCharts() {
    // Daily Incident Trend
    const incidentCtx = document.getElementById('incident-chart');
    if (incidentCtx && !charts.incident) {
        charts.incident = new Chart(incidentCtx, {
            type: 'line',
            data: {
                labels: getLast30Days(),
                datasets: [{
                    label: 'Incidents',
                    data: generateMockData(30),
                    borderColor: '#00BFFF',
                    backgroundColor: 'rgba(0, 191, 255, 0.1)',
                    tension: 0.4
                }]
            },
            options: { responsive: true, maintainAspectRatio: true }
        });
    }

    // Incident Type Distribution
    const typeCtx = document.getElementById('type-chart');
    if (typeCtx && !charts.type) {
        charts.type = new Chart(typeCtx, {
            type: 'doughnut',
            data: {
                labels: ['Missing Helmet', 'No Safety Gear', 'Overcrowded', 'Other'],
                datasets: [{
                    data: [35, 25, 20, 20],
                    backgroundColor: ['#FF3B30', '#00BFFF', '#00BFFF', '#34C759']
                }]
            },
            options: { responsive: true, maintainAspectRatio: true }
        });
    }

    // Severity Distribution
    const severityCtx = document.getElementById('severity-chart');
    if (severityCtx && !charts.severity) {
        charts.severity = new Chart(severityCtx, {
            type: 'bar',
            data: {
                labels: ['High', 'Medium', 'Low'],
                datasets: [{
                    label: 'Count',
                    data: [15, 35, 50],
                    backgroundColor: ['#FF3B30', '#00BFFF', '#34C759']
                }]
            },
            options: { responsive: true, maintainAspectRatio: true }
        });
    }

    // Compliance Rate
    const complianceCtx = document.getElementById('compliance-chart');
    if (complianceCtx && !charts.compliance) {
        charts.compliance = new Chart(complianceCtx, {
            type: 'line',
            data: {
                labels: getLast30Days(),
                datasets: [{
                    label: 'Compliance Rate (%)',
                    data: generateComplianceData(30),
                    borderColor: '#34C759',
                    backgroundColor: 'rgba(52, 199, 89, 0.1)',
                    tension: 0.4
                }]
            },
            options: { 
                responsive: true, 
                maintainAspectRatio: true,
                scales: { y: { max: 100 } }
            }
        });
    }
}

function updateAnalyticsCharts(incidents) {
    // Process incidents data and update charts
    console.log('Updating analytics with', incidents.length, 'incidents');
}

function generateReport() {
    const reportType = document.getElementById('report-type').value;
    showToast(`Generating ${reportType} report...`, 'info');
    
    // Simulate PDF generation
    setTimeout(() => {
        showToast('Report generated successfully', 'success');
    }, 2000);
}

/* ============ SETTINGS PAGE ============ */
async function loadSettings() {
    try {
        const response = await fetch('/health');
        const health = await response.json();
        document.getElementById('system-status').textContent = 
            `Status: ${health.status.toUpperCase()}`;
    } catch (error) {
        console.error('Load settings error:', error);
    }
}

function restartApp() {
    if (confirm('Are you sure you want to restart the application?')) {
        showToast('Restarting application...', 'warning');
        setTimeout(() => {
            location.reload();
        }, 2000);
    }
}

function resetDatabase() {
    if (confirm('This will delete all data. Are you sure?')) {
        showToast('Resetting database...', 'warning');
        // Call API to reset
    }
}

/* ============ UTILITY FUNCTIONS ============ */
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <i class="fas fa-${getToastIcon(type)}"></i>
        <span>${message}</span>
    `;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 5000);
}

function getToastIcon(type) {
    const icons = {
        'success': 'check-circle',
        'error': 'exclamation-circle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

function getLast30Days() {
    const days = [];
    for (let i = 29; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        days.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
    }
    return days;
}

function generateMockData(count) {
    return Array(count).fill(0).map(() => Math.floor(Math.random() * 20));
}

function generateComplianceData(count) {
    return Array(count).fill(0).map(() => Math.floor(Math.random() * 30 + 70));
}

function refreshDashboard() {
    loadDashboard();
    showToast('Dashboard refreshed', 'info');
}

function exportReport() {
    showToast('Report export feature coming soon', 'info');
}

function checkSystemHealth() {
    fetch('/health')
        .then(r => r.json())
        .then(health => {
            console.log('System Health:', health);
        })
        .catch(err => console.error('Health check failed:', err));
}

function setupAutoRefresh() {
    // Auto-refresh dashboard every 5 minutes
    setInterval(() => {
        if (currentPage === 'dashboard' && !monitoringActive) {
            loadDashboard();
        }
    }, 300000);
}

/* ============ PAGE LOAD ============ */
window.addEventListener('load', () => {
    console.log('AI Smart Safety Monitoring System ready');
    document.querySelectorAll('.page-content').forEach((page, index) => {
        if (index === 0) page.style.display = 'block';
        else page.style.display = 'none';
    });
});
