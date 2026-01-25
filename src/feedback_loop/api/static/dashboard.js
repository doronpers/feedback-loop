/**
 * Feedback Loop Dashboard JavaScript
 *
 * Handles data fetching, chart rendering, and UI updates for the analytics dashboard.
 */

// Global chart instances
let patternsOverTimeChart = null;
let severityChart = null;
let effectivenessChart = null;
let adoptionReductionChart = null;
let roiChart = null;
let teamUsageChart = null;

// API base URL
const API_BASE = '/dashboard';

// Global state
let currentDateRange = '30d';
let pollingInterval = null;

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function () {
    console.log('Feedback Loop Dashboard initializing...');
    initDarkMode();
    createDashboardControls();
    initializeDashboard();
});

/**
 * Initialize the dashboard
 */
async function initializeDashboard() {
    try {
        // Show loading states
        showLoadingStates();

        // Load all dashboard data
        await Promise.all([
            loadSummaryData(),
            loadChartData(),
            loadInsights(),
            loadRecentActivity()
        ]);

        // Update timestamp
        document.getElementById('last-updated').textContent = new Date().toLocaleString();

        console.log('Dashboard initialized successfully');
    } catch (error) {
        console.error('Failed to initialize dashboard:', error);
        showError('Failed to load dashboard data');
    }
}

/**
 * Show loading states for all sections
 */
function showLoadingStates() {
    // Summary cards
    ['total-bugs', 'total-test-failures', 'total-code-reviews', 'total-deployments'].forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.innerHTML = '<div class="loading-skeleton"><div class="skeleton-line"></div></div>';
        }
    });

    // Charts
    const chartContainers = document.querySelectorAll('.chart-container canvas');
    chartContainers.forEach(container => {
        const parent = container.parentElement;
        if (parent) {
            const loadingDiv = document.createElement('div');
            loadingDiv.className = 'loading-skeleton';
            loadingDiv.innerHTML = '<div class="skeleton-line"></div><div class="skeleton-line short"></div>';
            container.style.display = 'none';
            parent.appendChild(loadingDiv);
        }
    });
}

/**
 * Hide loading states
 */
function hideLoadingStates() {
    const skeletons = document.querySelectorAll('.loading-skeleton');
    skeletons.forEach(skeleton => skeleton.remove());

    const charts = document.querySelectorAll('.chart-container canvas');
    charts.forEach(chart => {
        chart.style.display = 'block';
    });
}

/**
 * Load summary metrics data
 */
async function loadSummaryData() {
    try {
        const response = await fetch(`${API_BASE}/summary?date_range=${currentDateRange}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();

        // Update summary cards
        document.getElementById('total-bugs').textContent = data.total_bugs || 0;
        document.getElementById('total-test-failures').textContent = data.total_test_failures || 0;
        document.getElementById('total-code-reviews').textContent = data.total_code_reviews || 0;
        document.getElementById('total-deployments').textContent = data.total_deployment_issues || 0;

        // Update top patterns
        updateTopPatterns(data.top_patterns || []);

        hideLoadingStates();
    } catch (error) {
        console.error('Failed to load summary data:', error);
        showErrorState('total-bugs-card', 'Failed to load summary data', () => loadSummaryData());
    }
}

/**
 * Load chart data and render charts
 */
async function loadChartData() {
    try {
        const dateRangeParam = `?date_range=${currentDateRange}`;

        // Load all charts in parallel
        const [
            patternsResponse,
            severityResponse,
            effectivenessResponse,
            adoptionResponse,
            roiResponse,
            teamResponse
        ] = await Promise.all([
            fetch(`${API_BASE}/charts/patterns-over-time${dateRangeParam}`),
            fetch(`${API_BASE}/charts/severity-distribution${dateRangeParam}`),
            fetch(`${API_BASE}/charts/pattern-effectiveness${dateRangeParam}`),
            fetch(`${API_BASE}/charts/adoption-reduction${dateRangeParam}`),
            fetch(`${API_BASE}/charts/pattern-roi${dateRangeParam}`),
            fetch(`${API_BASE}/charts/team-usage${dateRangeParam}`)
        ]);

        // Check all responses
        const responses = [patternsResponse, severityResponse, effectivenessResponse, adoptionResponse, roiResponse, teamResponse];
        const failed = responses.filter(r => !r.ok);
        if (failed.length > 0) {
            throw new Error(`${failed.length} chart requests failed`);
        }

        // Parse and render
        const [patternsData, severityData, effectivenessData, adoptionData, roiData, teamData] = await Promise.all(
            responses.map(r => r.json())
        );

        renderPatternsOverTimeChart(patternsData);
        renderSeverityChart(severityData);
        renderEffectivenessChart(effectivenessData);
        renderAdoptionReductionChart(adoptionData);
        renderROIChart(roiData);
        renderTeamUsageChart(teamData);

        hideLoadingStates();
    } catch (error) {
        console.error('Failed to load chart data:', error);
        showErrorState('charts-grid', 'Failed to load chart data', () => loadChartData());
    }
}

/**
 * Load insights and recommendations
 */
async function loadInsights() {
    try {
        const response = await fetch(`${API_BASE}/insights`);
        const data = await response.json();

        const insightsList = document.getElementById('insights-list');

        if (data.insights && data.insights.length > 0) {
            insightsList.innerHTML = data.insights.map(insight => `
                <div class="insight-item">
                    <div class="insight-title">${insight.title || 'Insight'}</div>
                    <div class="insight-description">${insight.description || ''}</div>
                    <div class="insight-impact">${insight.impact || ''}</div>
                </div>
            `).join('');
        } else {
            insightsList.innerHTML = '<p>No insights available yet. Run some tests with metrics enabled!</p>';
        }

    } catch (error) {
        console.error('Failed to load insights:', error);
        document.getElementById('insights-list').innerHTML = '<p>Failed to load insights</p>';
    }
}

/**
 * Load recent activity
 */
async function loadRecentActivity() {
    try {
        const response = await fetch(`${API_BASE}/summary`);
        const data = await response.json();

        const activityList = document.getElementById('recent-activity');

        if (data.recent_activity && data.recent_activity.length > 0) {
            activityList.innerHTML = data.recent_activity.map(activity => {
                const timestamp = new Date(activity.timestamp).toLocaleString();
                const icon = getActivityIcon(activity.type);
                const severityClass = `severity-${activity.severity || 'low'}`;

                return `
                    <div class="activity-item ${severityClass}">
                        <div class="activity-icon">${icon}</div>
                        <div class="activity-content">
                            <div class="activity-description">${activity.description}</div>
                            <div class="activity-timestamp">${timestamp}</div>
                        </div>
                    </div>
                `;
            }).join('');
        } else {
            activityList.innerHTML = '<p>No recent activity</p>';
        }

    } catch (error) {
        console.error('Failed to load recent activity:', error);
        document.getElementById('recent-activity').innerHTML = '<p>Failed to load activity</p>';
    }
}

/**
 * Update top patterns display
 */
function updateTopPatterns(patterns) {
    const container = document.getElementById('top-patterns');

    if (patterns && patterns.length > 0) {
        container.innerHTML = patterns.map((pattern, index) => `
            <div class="pattern-item">
                <div class="pattern-rank">#${index + 1}</div>
                <div class="pattern-info">
                    <div class="pattern-name">${pattern.pattern}</div>
                    <div class="pattern-count">${pattern.count} occurrences</div>
                </div>
            </div>
        `).join('');
    } else {
        container.innerHTML = '<p>No pattern data available</p>';
    }
}

/**
 * Get enhanced chart configuration
 */
function getChartConfig() {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const textColor = isDark ? '#e5e7eb' : '#374151';
    const gridColor = isDark ? '#374151' : '#e5e7eb';

    return {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
            intersect: false,
            mode: 'index'
        },
        plugins: {
            tooltip: {
                enabled: true,
                backgroundColor: isDark ? 'rgba(31, 41, 55, 0.95)' : 'rgba(0, 0, 0, 0.8)',
                titleColor: textColor,
                bodyColor: textColor,
                padding: 12,
                titleFont: { size: 14, weight: 'bold' },
                bodyFont: { size: 13 },
                callbacks: {
                    label: function(context) {
                        const label = context.dataset.label || '';
                        const value = context.parsed.y !== null ? context.parsed.y : context.parsed;
                        return `${label}: ${value}`;
                    }
                }
            },
            legend: {
                display: true,
                position: 'bottom',
                labels: {
                    usePointStyle: true,
                    padding: 15,
                    color: textColor
                }
            }
        },
        scales: {
            x: {
                ticks: { color: textColor },
                grid: { color: gridColor }
            },
            y: {
                ticks: { color: textColor },
                grid: { color: gridColor }
            }
        }
    };
}

/**
 * Render patterns over time chart
 */
function renderPatternsOverTimeChart(data) {
    const ctx = document.getElementById('patternsOverTimeChart');
    if (!ctx) return;

    const canvas = ctx.getContext('2d');

    if (patternsOverTimeChart) {
        patternsOverTimeChart.destroy();
    }

    const config = getChartConfig();
    config.scales.y.beginAtZero = true;
    config.scales.y.title = { display: true, text: 'Violations', color: config.scales.y.ticks.color };
    config.scales.x.title = { display: true, text: 'Date', color: config.scales.x.ticks.color };

    patternsOverTimeChart = new Chart(canvas, {
        type: 'line',
        data: data,
        options: config
    });
}

/**
 * Render severity distribution chart
 */
function renderSeverityChart(data) {
    const ctx = document.getElementById('severityChart');
    if (!ctx) return;

    const canvas = ctx.getContext('2d');

    if (severityChart) {
        severityChart.destroy();
    }

    const config = getChartConfig();
    config.plugins.legend.position = 'bottom';

    severityChart = new Chart(canvas, {
        type: 'doughnut',
        data: data,
        options: config
    });
}

/**
 * Render pattern effectiveness chart
 */
function renderEffectivenessChart(data) {
    const ctx = document.getElementById('effectivenessChart');
    if (!ctx) return;

    const canvas = ctx.getContext('2d');

    if (effectivenessChart) {
        effectivenessChart.destroy();
    }

    const config = getChartConfig();
    config.scales.y.beginAtZero = true;
    config.scales.y.max = 100;
    config.scales.y.title = { display: true, text: 'Effectiveness (%)', color: config.scales.y.ticks.color };
    config.scales.x.title = { display: true, text: 'Pattern', color: config.scales.x.ticks.color };
    config.plugins.legend.display = false;

    effectivenessChart = new Chart(canvas, {
        type: 'bar',
        data: data,
        options: config
    });
}

/**
 * Get activity icon based on type
 */
function getActivityIcon(activityType) {
    const icons = {
        'pattern_applied': '🔧',
        'test_failure': '❌',
        'code_review': '👁️',
        'bug_fixed': '🐛',
        'deployment': '🚀',
        'default': '📝'
    };

    return icons[activityType] || icons.default;
}

/**
 * Show error message overlay
 */
function showError(message) {
    console.error(message);

    // Create error overlay
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-overlay';
    errorDiv.innerHTML = `
        <div class="error-message">
            <h3>⚠️ Dashboard Error</h3>
            <p>${message}</p>
            <p>Check that feedback-loop is running and has metrics data.</p>
            <button class="retry-button" onclick="location.reload()">Reload Dashboard</button>
        </div>
    `;

    document.body.appendChild(errorDiv);

    // Auto-remove after 10 seconds
    setTimeout(() => {
        if (errorDiv.parentNode) {
            errorDiv.parentNode.removeChild(errorDiv);
        }
    }, 10000);
}

/**
 * Show error state for a specific element
 */
function showErrorState(elementId, message, retryCallback) {
    const element = document.getElementById(elementId);
    if (!element) return;

    const errorHtml = `
        <div class="error-state">
            <div class="error-icon">⚠️</div>
            <div class="error-message">${message}</div>
            ${retryCallback ? `<button class="retry-button" onclick="(${retryCallback.toString()})()">Retry</button>` : ''}
        </div>
    `;

    element.innerHTML = errorHtml;
}

/**
 * Show empty state for a specific element
 */
function showEmptyState(elementId, message, icon = '📭') {
    const element = document.getElementById(elementId);
    if (!element) return;

    const emptyHtml = `
        <div class="empty-state">
            <div class="empty-state-icon">${icon}</div>
            <div class="empty-message">${message}</div>
        </div>
    `;

    element.innerHTML = emptyHtml;
}

/**
 * Initialize dark mode
 */
function initDarkMode() {
    const savedTheme = localStorage.getItem('dashboard-theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);

    // Create theme toggle button
    const header = document.querySelector('.dashboard-header');
    if (header) {
        const toggle = document.createElement('button');
        toggle.className = 'theme-toggle';
        toggle.setAttribute('aria-label', 'Toggle dark mode');
        toggle.setAttribute('aria-pressed', savedTheme === 'dark');
        toggle.innerHTML = savedTheme === 'dark' ? '☀️' : '🌙';
        toggle.onclick = () => {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('dashboard-theme', newTheme);
            toggle.setAttribute('aria-pressed', newTheme === 'dark');
            toggle.innerHTML = newTheme === 'dark' ? '☀️' : '🌙';

            // Re-render charts with new theme
            loadChartData();
        };
        header.appendChild(toggle);
    }
}

/**
 * Create dashboard controls (date range filter, export button)
 */
function createDashboardControls() {
    const container = document.querySelector('.dashboard-container');
    if (!container) return;

    const controlsDiv = document.createElement('div');
    controlsDiv.className = 'dashboard-controls';

    // Date range filter
    const dateFilter = document.createElement('div');
    dateFilter.className = 'date-filter-container';
    dateFilter.innerHTML = `
        <label for="date-range">Time Period:</label>
        <select id="date-range" aria-label="Select time period">
            <option value="7d">Last 7 days</option>
            <option value="30d" selected>Last 30 days</option>
            <option value="90d">Last 90 days</option>
            <option value="1y">Last year</option>
            <option value="all">All time</option>
        </select>
    `;

    // Export button
    const exportButton = document.createElement('button');
    exportButton.className = 'export-button';
    exportButton.textContent = 'Export Data';
    exportButton.onclick = exportDashboardData;

    controlsDiv.appendChild(dateFilter);
    controlsDiv.appendChild(exportButton);

    // Insert after header
    const header = document.querySelector('.dashboard-header');
    if (header && header.nextSibling) {
        container.insertBefore(controlsDiv, header.nextSibling);
    } else {
        container.insertBefore(controlsDiv, container.firstChild.nextSibling);
    }

    // Add event listener for date range change
    const dateRangeSelect = document.getElementById('date-range');
    if (dateRangeSelect) {
        dateRangeSelect.addEventListener('change', (e) => {
            currentDateRange = e.target.value;
            initializeDashboard();
        });
    }
}

/**
 * Update date range and reload data
 */
function updateDateRange(range) {
    currentDateRange = range;
    initializeDashboard();
}

/**
 * Export dashboard data
 */
async function exportDashboardData() {
    try {
        const response = await fetch(`${API_BASE}/export?format=json&date_range=${currentDateRange}`);
        if (!response.ok) {
            throw new Error('Export failed');
        }

        const data = await response.json();
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `feedback-loop-dashboard-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    } catch (error) {
        console.error('Export failed:', error);
        alert('Failed to export data. Please try again.');
    }
}

/**
 * Start polling for real-time updates
 */
function startPolling(interval = 30000) {
    if (pollingInterval) {
        clearInterval(pollingInterval);
    }

    pollingInterval = setInterval(async () => {
        try {
            await Promise.all([
                loadSummaryData(),
                loadChartData(),
                loadInsights(),
                loadRecentActivity()
            ]);
            console.log('Dashboard updated');
        } catch (error) {
            console.error('Polling error:', error);
        }
    }, interval);
}

/**
 * Stop polling
 */
function stopPolling() {
    if (pollingInterval) {
        clearInterval(pollingInterval);
        pollingInterval = null;
    }
}

/**
 * Auto-refresh dashboard (optional)
 */
function setupAutoRefresh() {
    // Refresh every 5 minutes
    startPolling(5 * 60 * 1000);
}

/**
 * Render adoption vs reduction chart
 */
function renderAdoptionReductionChart(data) {
    const ctx = document.getElementById('adoptionReductionChart');
    if (!ctx) return;

    const canvas = ctx.getContext('2d');

    if (adoptionReductionChart) {
        adoptionReductionChart.destroy();
    }

    const config = getChartConfig();
    config.scales.y.beginAtZero = true;
    config.scales.y.title = { display: true, text: 'Count', color: config.scales.y.ticks.color };
    config.scales.x.title = { display: true, text: 'Date', color: config.scales.x.ticks.color };

    adoptionReductionChart = new Chart(canvas, {
        type: 'line',
        data: data,
        options: config
    });
}

/**
 * Render ROI chart
 */
function renderROIChart(data) {
    const ctx = document.getElementById('roiChart');
    if (!ctx) return;

    const canvas = ctx.getContext('2d');

    if (roiChart) {
        roiChart.destroy();
    }

    const config = getChartConfig();
    config.scales.y.beginAtZero = true;
    config.scales.y.title = { display: true, text: 'ROI Ratio', color: config.scales.y.ticks.color };
    config.scales.x.title = { display: true, text: 'Pattern', color: config.scales.x.ticks.color };
    config.plugins.legend.display = false;

    roiChart = new Chart(canvas, {
        type: 'bar',
        data: data,
        options: config
    });
}

/**
 * Render team usage chart
 */
function renderTeamUsageChart(data) {
    const ctx = document.getElementById('teamUsageChart');
    if (!ctx) return;

    const canvas = ctx.getContext('2d');

    if (teamUsageChart) {
        teamUsageChart.destroy();
    }

    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const textColor = isDark ? '#e5e7eb' : '#374151';
    const gridColor = isDark ? '#374151' : '#e5e7eb';

    const config = {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
            intersect: false,
            mode: 'index'
        },
        plugins: {
            tooltip: {
                enabled: true,
                backgroundColor: isDark ? 'rgba(31, 41, 55, 0.95)' : 'rgba(0, 0, 0, 0.8)',
                titleColor: textColor,
                bodyColor: textColor,
                padding: 12
            },
            legend: {
                position: 'bottom',
                labels: {
                    usePointStyle: true,
                    padding: 15,
                    color: textColor
                }
            }
        },
        scales: {
            r: {
                beginAtZero: true,
                ticks: { color: textColor },
                grid: { color: gridColor },
                pointLabels: { color: textColor }
            }
        }
    };

    teamUsageChart = new Chart(canvas, {
        type: 'radar',
        data: data,
        options: config
    });
}

// Setup auto-refresh when dashboard loads
document.addEventListener('DOMContentLoaded', function () {
    // Uncomment to enable auto-refresh
    // setupAutoRefresh();
});
