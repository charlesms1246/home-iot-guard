// Home IoT Guardian - Frontend JavaScript

// Global variables
let currentScanId = null;

// DOM Content Loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Home IoT Guardian Dashboard Loaded');
    
    // Initialize
    checkSystemStatus();
    loadHistory();
    
    // Event Listeners
    document.getElementById('upload-form').addEventListener('submit', handleUpload);
    document.getElementById('refresh-history-btn').addEventListener('click', loadHistory);
});

/**
 * Check system status
 */
async function checkSystemStatus() {
    try {
        const response = await fetch('/status');
        const data = await response.json();
        
        const statusBanner = document.getElementById('status-banner');
        const statusText = document.getElementById('system-status');
        
        if (data.status === 'operational' && data.model_loaded) {
            statusBanner.classList.remove('alert-info', 'alert-danger');
            statusBanner.classList.add('alert-success');
            statusText.innerHTML = `✓ Operational | Model: Loaded | Threshold: ${data.threshold.toFixed(6)} | Total Scans: ${data.total_scans}`;
            statusBanner.querySelector('.spinner-border').style.display = 'none';
        } else {
            statusBanner.classList.remove('alert-info', 'alert-success');
            statusBanner.classList.add('alert-warning');
            statusText.innerHTML = '⚠ Model not loaded. Please train the model first.';
            statusBanner.querySelector('.spinner-border').style.display = 'none';
        }
    } catch (error) {
        console.error('Failed to check status:', error);
        const statusBanner = document.getElementById('status-banner');
        statusBanner.classList.remove('alert-info', 'alert-success');
        statusBanner.classList.add('alert-danger');
        document.getElementById('system-status').innerHTML = '✗ Error connecting to server';
    }
}

/**
 * Handle file upload and scanning
 */
async function handleUpload(event) {
    event.preventDefault();
    
    const fileInput = document.getElementById('file-input');
    const file = fileInput.files[0];
    
    if (!file) {
        showAlert('Please select a file', 'danger');
        return;
    }
    
    // Validate file size (max 16MB)
    if (file.size > 16 * 1024 * 1024) {
        showAlert('File size exceeds 16MB limit', 'danger');
        return;
    }
    
    // Show progress
    document.getElementById('upload-progress').style.display = 'block';
    document.getElementById('scan-btn').disabled = true;
    document.getElementById('scan-btn').innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Scanning...';
    
    // Hide previous results
    document.getElementById('results-section').style.display = 'none';
    
    // Create FormData
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Upload failed');
        }
        
        // Display results
        displayResults(data);
        
        // Reload history
        loadHistory();
        
        // Show success message with alert for anomalies
        if (data.anomalies_count > 0) {
            showAlert(`⚠️ WARNING: ${data.anomalies_count} anomalies detected out of ${data.total_samples} samples!`, 'warning');
            showToast('Anomalies Detected!', `Found ${data.anomalies_count} potential threats. Check your email for details.`, 'warning');
        } else {
            showAlert(`✓ Scan completed! No anomalies detected in ${data.total_samples} samples.`, 'success');
            showToast('Scan Complete', 'All traffic appears normal.', 'success');
        }
        
        // Scroll to results
        document.getElementById('results-section').scrollIntoView({ behavior: 'smooth' });
        
    } catch (error) {
        console.error('Upload error:', error);
        showAlert(`Error: ${error.message}`, 'danger');
    } finally {
        // Hide progress and reset button
        document.getElementById('upload-progress').style.display = 'none';
        document.getElementById('scan-btn').disabled = false;
        document.getElementById('scan-btn').innerHTML = '<i class="bi bi-search"></i> Upload & Scan for Anomalies';
        
        // Clear file input
        fileInput.value = '';
    }
}

/**
 * Display scan results
 */
function displayResults(data) {
    // Show results section
    document.getElementById('results-section').style.display = 'block';
    
    // Update summary statistics
    document.getElementById('total-samples').textContent = data.total_samples;
    document.getElementById('anomalies-count').textContent = data.anomalies_count;
    document.getElementById('anomaly-percentage').textContent = data.percentage.toFixed(2) + '%';
    document.getElementById('threshold-value').textContent = data.threshold.toFixed(6);
    
    // Update results table
    const tbody = document.getElementById('results-tbody');
    tbody.innerHTML = '';
    
    if (data.details.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">No anomalies detected</td></tr>';
        return;
    }
    
    data.details.forEach((detail, index) => {
        const row = document.createElement('tr');
        row.classList.add('fade-in');
        
        // Severity badge
        const severityClass = detail.severity === 'High' ? 'severity-high' : 
                            detail.severity === 'Medium' ? 'severity-medium' : 'severity-low';
        
        // Sample data summary
        let sampleDataHtml = '';
        if (detail.sample_data) {
            const sampleKeys = Object.keys(detail.sample_data).slice(0, 3);
            sampleDataHtml = sampleKeys.map(key => 
                `${key}: ${detail.sample_data[key]}`
            ).join('<br>');
        }
        
        row.innerHTML = `
            <td>${detail.sequence_id}</td>
            <td>${detail.rows}</td>
            <td>${detail.error.toFixed(6)}</td>
            <td><span class="${severityClass}">${detail.severity}</span></td>
            <td class="sample-data" title="${JSON.stringify(detail.sample_data, null, 2)}">${sampleDataHtml || 'N/A'}</td>
        `;
        
        tbody.appendChild(row);
    });
}

/**
 * Load scan history
 */
async function loadHistory() {
    const tbody = document.getElementById('history-tbody');
    
    // Show loading
    tbody.innerHTML = '<tr><td colspan="4" class="text-center"><div class="spinner-border" role="status"></div></td></tr>';
    
    try {
        const response = await fetch('/history');
        const data = await response.json();
        
        tbody.innerHTML = '';
        
        if (data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="text-center text-muted">No scan history available</td></tr>';
            return;
        }
        
        data.forEach(scan => {
            const row = document.createElement('tr');
            
            row.innerHTML = `
                <td>${scan.id}</td>
                <td>${scan.timestamp}</td>
                <td><span class="badge bg-${scan.anomalies_count > 0 ? 'danger' : 'success'}">${scan.anomalies_count}</span></td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="viewScanDetails(${scan.id})">
                        <i class="bi bi-eye"></i> View
                    </button>
                </td>
            `;
            
            tbody.appendChild(row);
        });
        
    } catch (error) {
        console.error('Failed to load history:', error);
        tbody.innerHTML = '<tr><td colspan="4" class="text-center text-danger">Failed to load history</td></tr>';
    }
}

/**
 * View scan details
 */
async function viewScanDetails(scanId) {
    try {
        const response = await fetch(`/scan/${scanId}`);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to load scan details');
        }
        
        // Display the details
        displayResults({
            total_samples: data.details.length * 10, // Approximate
            anomalies_count: data.anomalies_count,
            percentage: (data.anomalies_count / data.details.length) * 100,
            threshold: data.details[0]?.threshold || 0.12,
            details: data.details
        });
        
        // Scroll to results
        document.getElementById('results-section').scrollIntoView({ behavior: 'smooth' });
        
    } catch (error) {
        console.error('Failed to load scan details:', error);
        showAlert(`Error loading scan details: ${error.message}`, 'danger');
    }
}

/**
 * Show alert message
 */
function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

/**
 * Show Bootstrap toast notification
 */
function showToast(title, message, type) {
    // Create toast container if it doesn't exist
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '9999';
        document.body.appendChild(toastContainer);
    }
    
    // Determine icon and color based on type
    let icon = 'bi-info-circle';
    let bgClass = 'bg-primary';
    
    if (type === 'warning') {
        icon = 'bi-exclamation-triangle';
        bgClass = 'bg-warning';
    } else if (type === 'danger') {
        icon = 'bi-x-circle';
        bgClass = 'bg-danger';
    } else if (type === 'success') {
        icon = 'bi-check-circle';
        bgClass = 'bg-success';
    }
    
    // Create toast element
    const toastId = `toast-${Date.now()}`;
    const toastHtml = `
        <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header ${bgClass} text-white">
                <i class="bi ${icon} me-2"></i>
                <strong class="me-auto">${title}</strong>
                <small>Just now</small>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;
    
    // Add toast to container
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    
    // Initialize and show toast
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, {
        autohide: true,
        delay: 5000
    });
    toast.show();
    
    // Remove toast element after it's hidden
    toastElement.addEventListener('hidden.bs.toast', function() {
        toastElement.remove();
    });
}

/**
 * Format timestamp
 */
function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString();
}

/**
 * Download results as JSON
 */
function downloadResults(data) {
    const dataStr = JSON.stringify(data, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `scan_results_${Date.now()}.json`;
    link.click();
    
    URL.revokeObjectURL(url);
}

// Scroll to top functionality
window.onscroll = function() {
    const scrollTopBtn = document.getElementById('scrollTopBtn');
    if (scrollTopBtn && (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20)) {
        scrollTopBtn.style.display = 'block';
    } else if (scrollTopBtn) {
        scrollTopBtn.style.display = 'none';
    }
};

console.log('Script loaded successfully');

