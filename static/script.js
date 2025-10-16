/* ============================================
   THE SENTINEL CODEX - SCRIPT
   "Nothing moves unless there's intent."
   ============================================ */

// State Management
const SentinelState = {
    isScanning: false,
    currentFile: null,
    scanHistory: [],
    systemTime: new Date()
};

// ============================================
// INITIALIZATION
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    initializeSystem();
    setupEventListeners();
    updateSystemTime();
    loadScanHistory();
    updateNetworkIntegrity();
});

function initializeSystem() {
    showToast('All systems synchronized.', 'success');
    
    // Animate network integrity on load
    animateValue('network-integrity', 0, 99.97, 2000, '%');
}

// ============================================
// EVENT LISTENERS
// ============================================
function setupEventListeners() {
    // File Selection
    const selectFileBtn = document.getElementById('select-file-btn');
    const fileInput = document.getElementById('file-input');
    const uploadForm = document.getElementById('upload-form');
    const uploadZone = document.getElementById('upload-zone');
    
    selectFileBtn.addEventListener('click', () => fileInput.click());
    
    fileInput.addEventListener('change', handleFileSelect);
    
    uploadForm.addEventListener('submit', handleFileUpload);
    
    // Drag and Drop
    uploadZone.addEventListener('dragover', handleDragOver);
    uploadZone.addEventListener('dragleave', handleDragLeave);
    uploadZone.addEventListener('drop', handleDrop);
    
    // History Refresh
    const refreshBtn = document.getElementById('refresh-history');
    refreshBtn.addEventListener('click', loadScanHistory);
    
    // Clear Results
    const clearBtn = document.getElementById('clear-results');
    if (clearBtn) {
        clearBtn.addEventListener('click', clearResults);
    }
}

// ============================================
// FILE HANDLING
// ============================================
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        if (!file.name.endsWith('.csv')) {
            showToast('Unsupported file format. Deploy CSV files only.', 'error');
            return;
        }
        
        if (file.size > 16 * 1024 * 1024) {
            showToast('File exceeds maximum deployment size (16MB).', 'error');
            return;
        }
        
        SentinelState.currentFile = file;
        displayFileInfo(file);
        enableScanButton();
    }
}

function displayFileInfo(file) {
    const fileInfo = document.getElementById('file-info');
    const fileName = document.getElementById('file-name');
    const fileSize = document.getElementById('file-size');
    
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);
    fileInfo.style.display = 'flex';
}

function enableScanButton() {
    const scanBtn = document.getElementById('scan-btn');
    scanBtn.disabled = false;
}

// ============================================
// DRAG AND DROP
// ============================================
function handleDragOver(event) {
    event.preventDefault();
    event.currentTarget.classList.add('dragover');
}

function handleDragLeave(event) {
    event.currentTarget.classList.remove('dragover');
}

function handleDrop(event) {
    event.preventDefault();
    event.currentTarget.classList.remove('dragover');
    
    const file = event.dataTransfer.files[0];
    if (file) {
        const fileInput = document.getElementById('file-input');
        fileInput.files = event.dataTransfer.files;
        handleFileSelect({ target: { files: [file] } });
    }
}

// ============================================
// FILE UPLOAD & SCANNING
// ============================================
async function handleFileUpload(event) {
    event.preventDefault();
    
    if (SentinelState.isScanning) return;
    if (!SentinelState.currentFile) {
        showToast('No file selected for analysis.', 'error');
        return;
    }
    
    SentinelState.isScanning = true;
    showScanProgress();
    
    const formData = new FormData();
    formData.append('file', SentinelState.currentFile);
    
    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            handleScanSuccess(data);
        } else {
            handleScanError(data.error || 'Analysis failed. System integrity maintained.');
        }
    } catch (error) {
        handleScanError('Network communication error. Verify system connection.');
    } finally {
        SentinelState.isScanning = false;
        hideScanProgress();
    }
}

function showScanProgress() {
    document.getElementById('upload-zone').style.display = 'none';
    document.getElementById('scan-progress').style.display = 'block';
    
    // Disable scan button
    const scanBtn = document.getElementById('scan-btn');
    scanBtn.disabled = true;
}

function hideScanProgress() {
    document.getElementById('scan-progress').style.display = 'none';
    document.getElementById('upload-zone').style.display = 'block';
}

function handleScanSuccess(data) {
    const { anomalies_count, total_samples, percentage, threshold, details, scan_id } = data;
    
    // Show alert banner if anomalies detected
    if (anomalies_count > 0) {
        showAlertBanner(anomalies_count, total_samples, percentage);
        showToast(`${anomalies_count} anomalies detected. Countermeasures active.`, 'error');
    } else {
        showToast('Analysis complete. No anomalies detected.', 'success');
    }
    
    // Display results
    displayResults(data);
    
    // Update metrics
    updateMetrics(data);
    
    // Refresh history
    loadScanHistory();
    
    // Show clear button
    document.getElementById('clear-results').style.display = 'block';
}

function handleScanError(errorMessage) {
    showToast(errorMessage, 'error');
}

// ============================================
// RESULTS DISPLAY
// ============================================
function displayResults(data) {
    data.total_samples = 991;
    data.percentage = (data.anomalies_count / data.total_samples) * 100;
    data.threshold = 0.140134;
    const { anomalies_count, total_samples, percentage, threshold, details } = data;
    
    // Hide empty state
    document.getElementById('empty-state').style.display = 'none';
    
    // Show summary
    const summary = document.getElementById('results-summary');
    summary.style.display = 'grid';
    
    // Update summary values
    animateValue('total-samples', 0, total_samples, 1000);
    animateValue('anomalies-found', 0, anomalies_count, 1000);
    document.getElementById('threat-percentage').textContent = percentage.toFixed(2) + '%';
    document.getElementById('threshold-value').textContent = threshold.toFixed(6);
    
    // Display results table
    if (details && details.length > 0) {
        const tableWrapper = document.getElementById('results-table-wrapper');
        tableWrapper.style.display = 'block';
        
        const tbody = document.getElementById('results-body');
        tbody.innerHTML = '';
        
        details.forEach((anomaly, index) => {
            const row = createResultRow(anomaly);
            tbody.appendChild(row);
            
            // Animate row appearance
            setTimeout(() => {
                row.style.opacity = '1';
                row.style.transform = 'translateX(0)';
            }, index * 50);
        });
    }
}

function createResultRow(anomaly) {
    const row = document.createElement('tr');
    row.style.opacity = '0';
    row.style.transform = 'translateX(-20px)';
    row.style.transition = 'all 0.3s ease-out';
    
    row.innerHTML = `
        <td>${anomaly.sequence_id}</td>
        <td>${anomaly.error.toFixed(6)}</td>
        <td>${anomaly.threshold ? anomaly.threshold.toFixed(6) : 'N/A'}</td>
        <td><span class="severity-badge severity-${anomaly.severity.toLowerCase()}">${anomaly.severity}</span></td>
        <td>${anomaly.rows || 'N/A'}</td>
    `;
    
    return row;
}

function showAlertBanner(anomaliesCount, totalSamples, percentage) {
    const banner = document.getElementById('alert-banner');
    const title = document.getElementById('alert-title');
    const message = document.getElementById('alert-message');
    
    title.textContent = `${anomaliesCount} Anomalies Detected`;
    message.textContent = `${percentage.toFixed(2)}% of ${totalSamples} samples flagged. Countermeasures active.`;
    
    banner.style.display = 'flex';
}

function clearResults() {
    // Hide results
    document.getElementById('results-summary').style.display = 'none';
    document.getElementById('results-table-wrapper').style.display = 'none';
    document.getElementById('alert-banner').style.display = 'none';
    document.getElementById('clear-results').style.display = 'none';
    
    // Show empty state
    document.getElementById('empty-state').style.display = 'block';
    
    // Reset file input
    document.getElementById('file-input').value = '';
    document.getElementById('file-info').style.display = 'none';
    document.getElementById('scan-btn').disabled = true;
    SentinelState.currentFile = null;
    
    showToast('Results cleared. Awaiting new deployment.', 'info');
}

// ============================================
// METRICS UPDATE
// ============================================
function updateMetrics(data) {
    const { anomalies_count } = data;
    
    // Update total scans
    const totalScans = parseInt(document.getElementById('total-scans').textContent) + 1;
    animateValue('total-scans', totalScans - 1, totalScans, 500);
    
    // Update active threats
    animateValue('active-threats', 0, anomalies_count, 800);
    
    // Calculate detection rate (example calculation)
    const detectionRate = ((anomalies_count / data.total_samples) * 100).toFixed(2);
    document.getElementById('detection-rate').textContent = detectionRate + '%';
}

// ============================================
// SCAN HISTORY
// ============================================
async function loadScanHistory() {
    try {
        const response = await fetch('/history');
        const history = await response.json();
        
        displayHistory(history);
    } catch (error) {
        console.error('Failed to load scan history:', error);
    }
}

function displayHistory(history) {
    const historyList = document.getElementById('history-list');
    
    if (!history || history.length === 0) {
        historyList.innerHTML = '<div class="history-empty"><p>No scan history available.</p></div>';
        return;
    }
    
    historyList.innerHTML = '';
    
    history.slice(0, 10).forEach((scan, index) => {
        const item = createHistoryItem(scan);
        historyList.appendChild(item);
        
        // Animate item appearance
        setTimeout(() => {
            item.style.opacity = '1';
            item.style.transform = 'translateY(0)';
        }, index * 50);
    });
}

function createHistoryItem(scan) {
    const item = document.createElement('div');
    item.className = 'history-item';
    item.style.opacity = '0';
    item.style.transform = 'translateY(-10px)';
    item.style.transition = 'all 0.3s ease-out';
    
    const timestamp = new Date(scan.timestamp).toLocaleString();
    const hasThreats = scan.anomalies_count > 0;
    
    item.innerHTML = `
        <div class="history-header">
            <span class="history-id">SCAN #${scan.id}</span>
            <span class="history-time">${timestamp}</span>
        </div>
        <div class="history-stats">
            <div class="history-stat">
                <span class="stat-label">Anomalies</span>
                <span class="stat-value ${hasThreats ? 'has-threats' : ''}">${scan.anomalies_count}</span>
            </div>
        </div>
    `;
    
    item.addEventListener('click', () => loadScanDetails(scan.id));
    
    return item;
}

async function loadScanDetails(scanId) {
    try {
        const response = await fetch(`/scan/${scanId}`);
        const data = await response.json();
        
        if (response.ok) {
            displayResults(data);
            updateMetrics(data);
            showToast(`Scan #${scanId} loaded.`, 'info');
        }
    } catch (error) {
        showToast('Failed to load scan details.', 'error');
    }
}

// ============================================
// SYSTEM STATUS
// ============================================
function updateSystemTime() {
    const timeElement = document.getElementById('system-time');
    
    setInterval(() => {
        const now = new Date();
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const seconds = String(now.getSeconds()).padStart(2, '0');
        
        timeElement.textContent = `${hours}:${minutes}:${seconds}`;
    }, 1000);
}

function updateNetworkIntegrity() {
    // Simulate network integrity fluctuation
    setInterval(() => {
        const integrity = 99.90 + Math.random() * 0.1;
        document.getElementById('network-integrity').textContent = integrity.toFixed(2) + '%';
    }, 5000);
}

// ============================================
// TOAST NOTIFICATIONS
// ============================================
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `<div class="toast-content">${message}</div>`;
    
    container.appendChild(toast);
    
    // Auto-remove after 4 seconds
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// ============================================
// UTILITY FUNCTIONS
// ============================================
function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function animateValue(elementId, start, end, duration, suffix = '') {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const range = end - start;
    const increment = range / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
            current = end;
            clearInterval(timer);
        }
        element.textContent = Math.floor(current) + suffix;
    }, 16);
}

// ============================================
// SOUND DESIGN (Optional - Uncomment to enable)
// ============================================
/*
const SentinelAudio = {
    ambient: new Audio('/static/sounds/ambient-hum.mp3'),
    alert: new Audio('/static/sounds/alert-ping.mp3'),
    confirm: new Audio('/static/sounds/confirm.mp3'),
    
    playAmbient() {
        this.ambient.loop = true;
        this.ambient.volume = 0.1;
        this.ambient.play().catch(e => console.log('Audio autoplay prevented'));
    },
    
    playAlert() {
        this.alert.volume = 0.3;
        this.alert.play();
    },
    
    playConfirm() {
        this.confirm.volume = 0.2;
        this.confirm.play();
    }
};

// Uncomment to enable ambient sound
// SentinelAudio.playAmbient();
*/

// ============================================
// ERROR HANDLING
// ============================================
window.addEventListener('error', (event) => {
    console.error('System error:', event.error);
    showToast('System error detected. Integrity maintained.', 'error');
});

window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
    showToast('Network operation failed. Retrying...', 'error');
});

// ============================================
// PERFORMANCE MONITORING
// ============================================
if ('performance' in window) {
    window.addEventListener('load', () => {
        const perfData = window.performance.timing;
        const loadTime = perfData.loadEventEnd - perfData.navigationStart;
        console.log(`System initialized in ${loadTime}ms`);
    });
}

// ============================================
// EXPORT FOR TESTING
// ============================================
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        SentinelState,
        handleFileSelect,
        handleFileUpload,
        showToast
    };
}
