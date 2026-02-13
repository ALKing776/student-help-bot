// Dashboard JavaScript
let socket;
let charts = {};
let currentTab = 'dashboard';

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
    setupEventListeners();
    connectWebSocket();
    updateTime();
    setInterval(updateTime, 1000);
});

function initializeDashboard() {
    // Initialize sidebar toggle
    document.getElementById('sidebarCollapse').addEventListener('click', function () {
        document.getElementById('sidebar').classList.toggle('active');
    });
    
    // Initialize tab navigation
    setupTabNavigation();
    
    // Load initial data
    loadDashboardData();
    
    // Set up periodic updates
    setInterval(loadDashboardData, 30000); // Update every 30 seconds
}

function setupEventListeners() {
    // Tab navigation
    document.querySelectorAll('[data-tab]').forEach(tab => {
        tab.addEventListener('click', function(e) {
            e.preventDefault();
            const tabName = this.getAttribute('data-tab');
            switchTab(tabName);
        });
    });
    
    // Form submissions
    document.getElementById('password')?.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            this.form.submit();
        }
    });
}

function setupTabNavigation() {
    // Set up tab switching
    const tabs = document.querySelectorAll('.list-unstyled li a[data-tab]');
    tabs.forEach(tab => {
        tab.addEventListener('click', function(e) {
            e.preventDefault();
            const tabName = this.getAttribute('data-tab');
            switchTab(tabName);
        });
    });
}

function switchTab(tabName) {
    // Update active tab in sidebar
    document.querySelectorAll('.list-unstyled li').forEach(li => {
        li.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).closest('li').classList.add('active');
    
    // Hide all tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(`tab-${tabName}`).classList.add('active');
    
    currentTab = tabName;
    
    // Load tab-specific data
    switch(tabName) {
        case 'dashboard':
            loadDashboardData();
            break;
        case 'accounts':
            loadAccountsData();
            break;
        case 'users':
            loadUsersData();
            break;
        case 'services':
            loadServicesData();
            break;
        case 'config':
            loadConfigData();
            break;
    }
}

function connectWebSocket() {
    // Connect to WebSocket
    socket = io();
    
    socket.on('connect', function() {
        console.log('Connected to WebSocket');
        socket.emit('request_updates');
    });
    
    socket.on('stats_update', function(data) {
        updateStatsDisplay(data);
    });
    
    socket.on('accounts_update', function(data) {
        if (currentTab === 'accounts') {
            updateAccountsTable(data.accounts);
        }
    });
    
    socket.on('disconnect', function() {
        console.log('Disconnected from WebSocket');
    });
}

function updateTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString();
    const element = document.getElementById('current-time');
    if (element) {
        element.textContent = timeString;
    }
}

// Dashboard Data Loading
async function loadDashboardData() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        if (data.error) {
            showError('Failed to load dashboard data: ' + data.error);
            return;
        }
        
        updateStatsDisplay(data);
        updateCharts(data);
        updateRecentActivity(data);
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showError('Failed to load dashboard data');
    }
}

function updateStatsDisplay(data) {
    // Update main stats cards
    document.getElementById('active-accounts').textContent = data.dashboard_stats?.active_accounts || 0;
    document.getElementById('total-messages').textContent = formatNumber(data.dashboard_stats?.total_messages || 0);
    document.getElementById('forwarded-messages').textContent = formatNumber(data.dashboard_stats?.forwarded_messages || 0);
    document.getElementById('mpm').textContent = (data.messages_per_minute || 0).toFixed(1);
    
    // Update top services
    updateTopServices(data.dashboard_stats?.top_services || []);
    
    // Update account health
    updateAccountHealth(data.account_utilization);
}

function updateTopServices(services) {
    const container = document.getElementById('top-services-list');
    if (!container) return;
    
    container.innerHTML = '';
    
    services.slice(0, 5).forEach((service, index) => {
        const item = document.createElement('div');
        item.className = 'd-flex justify-content-between align-items-center mb-2';
        item.innerHTML = `
            <div>
                <span class="badge bg-primary me-2">#${index + 1}</span>
                <strong>${service.service}</strong>
            </div>
            <span class="badge bg-secondary">${service.count}</span>
        `;
        container.appendChild(item);
    });
}

function updateAccountHealth(utilization) {
    const container = document.getElementById('account-health');
    if (!container) return;
    
    container.innerHTML = `
        <div class="progress mb-2">
            <div class="progress-bar bg-success" role="progressbar" 
                 style="width: ${utilization?.utilization_rate || 0}%" 
                 aria-valuenow="${utilization?.utilization_rate || 0}" 
                 aria-valuemin="0" aria-valuemax="100">
                ${Math.round(utilization?.utilization_rate || 0)}%
            </div>
        </div>
        <small class="text-muted">
            ${utilization?.active_accounts || 0} of ${utilization?.total_accounts || 0} accounts active
        </small>
    `;
}

function updateRecentActivity(data) {
    // Implementation for recent activity display
    const container = document.getElementById('recent-activity');
    if (!container) return;
    
    container.innerHTML = '<p class="text-muted">Recent activity will appear here...</p>';
}

function updateCharts(data) {
    // Update service distribution chart
    if (data.dashboard_stats?.top_services) {
        updateServiceChart(data.dashboard_stats.top_services);
    }
}

function updateServiceChart(services) {
    const ctx = document.getElementById('serviceChart');
    if (!ctx) return;
    
    // Destroy existing chart if it exists
    if (charts.serviceChart) {
        charts.serviceChart.destroy();
    }
    
    const labels = services.map(s => s.service);
    const data = services.map(s => s.count);
    
    charts.serviceChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    '#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// Accounts Management
async function loadAccountsData() {
    try {
        const response = await fetch('/api/accounts');
        const data = await response.json();
        
        if (data.error) {
            showError('Failed to load accounts data: ' + data.error);
            return;
        }
        
        updateAccountsTable(data.accounts);
        
    } catch (error) {
        console.error('Error loading accounts data:', error);
        showError('Failed to load accounts data');
    }
}

function updateAccountsTable(accounts) {
    const tbody = document.querySelector('#accounts-table tbody');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    accounts.forEach(account => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${account.id}</td>
            <td>@${account.username}</td>
            <td>
                <span class="status-indicator ${account.is_connected ? 'status-active' : 'status-inactive'}"></span>
                ${account.is_connected ? 'Connected' : 'Disconnected'}
            </td>
            <td>${formatNumber(account.messages_processed)}</td>
            <td>${account.error_count}</td>
            <td>${account.current_load}</td>
            <td>${formatDateTime(account.last_used)}</td>
            <td>
                <button class="btn btn-sm btn-outline-primary" onclick="viewAccountDetails(${account.id})">
                    <i class="fas fa-eye"></i>
                </button>
                ${!account.is_connected ? 
                    `<button class="btn btn-sm btn-outline-success" onclick="reconnectAccount(${account.id})">
                        <i class="fas fa-plug"></i>
                    </button>` : ''
                }
            </td>
        `;
        tbody.appendChild(row);
    });
}

async function refreshAccounts() {
    showLoading('Refreshing accounts...');
    await loadAccountsData();
    hideLoading();
    showSuccess('Accounts refreshed successfully');
}

// Users Management
async function loadUsersData() {
    try {
        const response = await fetch('/api/users');
        const data = await response.json();
        
        if (data.error) {
            showError('Failed to load users data: ' + data.error);
            return;
        }
        
        updateUsersTable(data.users);
        
    } catch (error) {
        console.error('Error loading users data:', error);
        showError('Failed to load users data');
    }
}

function updateUsersTable(users) {
    const tbody = document.querySelector('#users-table tbody');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    users.slice(0, 50).forEach(user => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${user.id}</td>
            <td>@${user.username}</td>
            <td>${user.messages_count}</td>
            <td>${user.help_requests}</td>
            <td>${formatDateTime(user.last_seen)}</td>
            <td>
                <button class="btn btn-sm btn-outline-primary" onclick="viewUserDetails(${user.id})">
                    <i class="fas fa-user"></i>
                </button>
                <button class="btn btn-sm btn-outline-warning" onclick="blacklistUser(${user.id})">
                    <i class="fas fa-ban"></i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// Services Analytics
async function loadServicesData() {
    try {
        const response = await fetch('/api/services');
        const data = await response.json();
        
        if (data.error) {
            showError('Failed to load services data: ' + data.error);
            return;
        }
        
        updateServicesTable(data.services);
        
    } catch (error) {
        console.error('Error loading services data:', error);
        showError('Failed to load services data');
    }
}

function updateServicesTable(services) {
    const tbody = document.querySelector('#services-table tbody');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    services.forEach(service => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><span class="service-tag">${service.service_name}</span></td>
            <td>${formatNumber(service.total_requests)}</td>
            <td>${formatNumber(service.forwarded_requests)}</td>
            <td>${service.average_confidence}%</td>
            <td>${service.peak_hours.join(', ')}</td>
        `;
        tbody.appendChild(row);
    });
}

// Configuration Management
async function loadConfigData() {
    try {
        const response = await fetch('/api/config');
        const data = await response.json();
        
        if (data.error) {
            showError('Failed to load config data: ' + data.error);
            return;
        }
        
        updateConfigDisplay(data);
        
    } catch (error) {
        console.error('Error loading config data:', error);
        showError('Failed to load config data');
    }
}

function updateConfigDisplay(config) {
    const container = document.getElementById('current-config');
    if (!container) return;
    
    container.innerHTML = '';
    
    Object.entries(config).forEach(([key, value]) => {
        const item = document.createElement('div');
        item.className = 'mb-3 p-2 bg-light rounded';
        item.innerHTML = `
            <div class="d-flex justify-content-between">
                <strong>${key}:</strong>
                <span>${String(value)}</span>
            </div>
        `;
        container.appendChild(item);
    });
}

async function updateConfig() {
    const key = document.getElementById('config-key').value;
    const value = document.getElementById('config-value').value;
    
    if (!key || !value) {
        showError('Please enter both key and value');
        return;
    }
    
    try {
        const response = await fetch('/api/config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ key, value })
        });
        
        const data = await response.json();
        
        if (data.error) {
            showError('Failed to update config: ' + data.error);
            return;
        }
        
        showSuccess('Configuration updated successfully');
        document.getElementById('config-key').value = '';
        document.getElementById('config-value').value = '';
        loadConfigData();
        
    } catch (error) {
        console.error('Error updating config:', error);
        showError('Failed to update configuration');
    }
}

// Reports Generation
async function generateReport() {
    const reportType = document.getElementById('report-type').value;
    const days = document.getElementById('report-days').value;
    const format = document.getElementById('report-format').value;
    
    showLoading('Generating report...');
    
    try {
        const response = await fetch(`/api/reports/${reportType}?days=${days}&format=${format}`);
        const data = await response.text();
        
        const output = document.getElementById('reports-output');
        output.innerHTML = `
            <div class="alert alert-success">
                <h6><i class="fas fa-check-circle"></i> Report Generated Successfully</h6>
                <pre class="mt-3" style="max-height: 400px; overflow-y: auto;">${data}</pre>
                <button class="btn btn-sm btn-outline-primary mt-2" onclick="downloadReport('${reportType}', '${format}')">
                    <i class="fas fa-download"></i> Download
                </button>
            </div>
        `;
        
        hideLoading();
        showSuccess('Report generated successfully');
        
    } catch (error) {
        console.error('Error generating report:', error);
        hideLoading();
        showError('Failed to generate report');
    }
}

function downloadReport(reportType, format) {
    // Implementation for downloading reports
    showInfo('Download functionality would be implemented here');
}

// Utility Functions
function formatNumber(num) {
    return new Intl.NumberFormat().format(num);
}

function formatDateTime(dateString) {
    if (!dateString) return 'Never';
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
}

function showLoading(message = 'Loading...') {
    // Implementation for loading indicator
    console.log('Loading:', message);
}

function hideLoading() {
    // Implementation for hiding loading indicator
    console.log('Loading hidden');
}

function showError(message) {
    // Implementation for error toast
    alert('Error: ' + message);
    console.error('Error:', message);
}

function showSuccess(message) {
    // Implementation for success toast
    console.log('Success:', message);
}

function showInfo(message) {
    // Implementation for info toast
    console.log('Info:', message);
}

// Account Actions
function viewAccountDetails(accountId) {
    showInfo(`View details for account ${accountId}`);
}

function reconnectAccount(accountId) {
    showInfo(`Reconnecting account ${accountId}`);
}

// User Actions
function viewUserDetails(userId) {
    showInfo(`View details for user ${userId}`);
}

function blacklistUser(userId) {
    if (confirm(`Are you sure you want to blacklist user ${userId}?`)) {
        showInfo(`Blacklisting user ${userId}`);
    }
}