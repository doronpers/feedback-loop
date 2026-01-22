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

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function () {
    console.log('Feedback Loop Dashboard initializing...');
    initializeDashboard();
});

/**
 * Initialize the dashboard
 */
async function initializeDashboard() {
    try {
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
 * Load summary metrics data
 */
async function loadSummaryData() {
    try {
        const response = await fetch(`${API_BASE}/summary`);
        const data = await response.json();

        // Update summary cards
        document.getElementById('total-bugs').textContent = data.total_bugs || 0;
        document.getElementById('total-test-failures').textContent = data.total_test_failures || 0;
        document.getElementById('total-code-reviews').textContent = data.total_code_reviews || 0;
        document.getElementById('total-deployments').textContent = data.total_deployment_issues || 0;

        // Update top patterns
        updateTopPatterns(data.top_patterns || []);

    } catch (error) {
        console.error('Failed to load summary data:', error);
    }
}

/**
 * Load chart data and render charts
 */
async function loadChartData() {
    try {
        // Load patterns over time chart
        const patternsResponse = await fetch(`${API_BASE}/charts/patterns-over-time`);
        const patternsData = await patternsResponse.json();
        renderPatternsOverTimeChart(patternsData);

        // Load severity distribution chart
        const severityResponse = await fetch(`${API_BASE}/charts/severity-distribution`);
        const severityData = await severityResponse.json();
        renderSeverityChart(severityData);

        // Load pattern effectiveness chart
        const effectivenessResponse = await fetch(`${API_BASE}/charts/pattern-effectiveness`);
        const effectivenessData = await effectivenessResponse.json();
        renderEffectivenessChart(effectivenessData);

        // Load adoption vs reduction chart
        const adoptionResponse = await fetch(`${API_BASE}/charts/adoption-reduction`);
        const adoptionData = await adoptionResponse.json();
        renderAdoptionReductionChart(adoptionData);

        // Load ROI chart
        const roiResponse = await fetch(`${API_BASE}/charts/pattern-roi`);
        const roiData = await roiResponse.json();
        renderROIChart(roiData);

        // Load team usage chart
        const teamResponse = await fetch(`${API_BASE}/charts/team-usage`);
        const teamData = await teamResponse.json();
        renderTeamUsageChart(teamData);

    } catch (error) {
        console.error('Failed to load chart data:', error);
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
 * Render patterns over time chart
 */
function renderPatternsOverTimeChart(data) {
    const ctx = document.getElementById('patternsOverTimeChart').getContext('2d');

    if (patternsOverTimeChart) {
        patternsOverTimeChart.destroy();
    }

    patternsOverTimeChart = new Chart(ctx, {
        type: 'line',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Violations'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Date'
                    }
                }
            },
            plugins: {
                legend: {
                    display: true
                }
            }
        }
    });
}

/**
 * Render severity distribution chart
 */
function renderSeverityChart(data) {
    const ctx = document.getElementById('severityChart').getContext('2d');

    if (severityChart) {
        severityChart.destroy();
    }

    severityChart = new Chart(ctx, {
        type: 'doughnut',
        data: data,
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

/**
 * Render pattern effectiveness chart
 */
function renderEffectivenessChart(data) {
    const ctx = document.getElementById('effectivenessChart').getContext('2d');

    if (effectivenessChart) {
        effectivenessChart.destroy();
    }

    effectivenessChart = new Chart(ctx, {
        type: 'bar',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Effectiveness (%)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Pattern'
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
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
 * Show error message
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
        </div>
    `;

    document.body.appendChild(errorDiv);
}

/**
 * Auto-refresh dashboard (optional)
 */
function setupAutoRefresh() {
    // Refresh every 5 minutes
    setInterval(() => {
        console.log('Auto-refreshing dashboard...');
        initializeDashboard();
    }, 5 * 60 * 1000);
}

/**
 * Render adoption vs reduction chart
 */
function renderAdoptionReductionChart(data) {
    const ctx = document.getElementById('adoptionReductionChart').getContext('2d');

    if (adoptionReductionChart) {
        adoptionReductionChart.destroy();
    }

    adoptionReductionChart = new Chart(ctx, {
        type: 'line',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Count'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Date'
                    }
                }
            },
            plugins: {
                legend: {
                    display: true
                }
            }
        }
    });
}

/**
 * Render ROI chart
 */
function renderROIChart(data) {
    const ctx = document.getElementById('roiChart').getContext('2d');

    if (roiChart) {
        roiChart.destroy();
    }

    roiChart = new Chart(ctx, {
        type: 'bar',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'ROI Ratio'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Pattern'
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

/**
 * Render team usage chart
 */
function renderTeamUsageChart(data) {
    const ctx = document.getElementById('teamUsageChart').getContext('2d');

    if (teamUsageChart) {
        teamUsageChart.destroy();
    }

    teamUsageChart = new Chart(ctx, {
        type: 'radar',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            },
            scales: {
                r: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Setup auto-refresh when dashboard loads
document.addEventListener('DOMContentLoaded', function () {
    // Uncomment to enable auto-refresh
    // setupAutoRefresh();
});
