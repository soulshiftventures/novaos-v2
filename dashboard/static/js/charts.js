/**
 * NovaOS V2 Dashboard Charts
 * Shared chart utilities and configurations
 */

// Chart.js default configurations
if (typeof Chart !== 'undefined') {
    Chart.defaults.color = '#8b949e';
    Chart.defaults.borderColor = '#30363d';
    Chart.defaults.backgroundColor = 'rgba(88, 166, 255, 0.1)';

    Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif';
    Chart.defaults.font.size = 12;

    // Dark mode colors
    Chart.defaults.plugins.legend.labels.color = '#c9d1d9';
    Chart.defaults.scale.grid.color = '#30363d';
    Chart.defaults.scale.ticks.color = '#8b949e';
}

/**
 * Chart color palette
 */
const ChartColors = {
    primary: 'rgba(88, 166, 255, 0.8)',
    success: 'rgba(63, 185, 80, 0.8)',
    warning: 'rgba(210, 153, 34, 0.8)',
    danger: 'rgba(248, 81, 73, 0.8)',
    info: 'rgba(13, 202, 240, 0.8)',
    secondary: 'rgba(139, 148, 158, 0.8)',

    primaryLight: 'rgba(88, 166, 255, 0.2)',
    successLight: 'rgba(63, 185, 80, 0.2)',
    warningLight: 'rgba(210, 153, 34, 0.2)',
    dangerLight: 'rgba(248, 81, 73, 0.2)',
    infoLight: 'rgba(13, 202, 240, 0.2)',
    secondaryLight: 'rgba(139, 148, 158, 0.2)'
};

/**
 * Format currency value
 */
function formatCurrency(value) {
    if (typeof value !== 'number') {
        value = parseFloat(value);
    }
    return '$' + value.toFixed(2);
}

/**
 * Format percentage value
 */
function formatPercent(value) {
    if (typeof value !== 'number') {
        value = parseFloat(value);
    }
    return value.toFixed(1) + '%';
}

/**
 * Format large numbers (K, M, B)
 */
function formatLargeNumber(value) {
    if (typeof value !== 'number') {
        value = parseFloat(value);
    }

    if (value >= 1000000000) {
        return (value / 1000000000).toFixed(1) + 'B';
    } else if (value >= 1000000) {
        return (value / 1000000).toFixed(1) + 'M';
    } else if (value >= 1000) {
        return (value / 1000).toFixed(1) + 'K';
    }

    return value.toFixed(0);
}

/**
 * Get color based on ROI value
 */
function getROIColor(roi) {
    if (roi >= 300) return ChartColors.success;
    if (roi >= 100) return ChartColors.warning;
    return ChartColors.danger;
}

/**
 * Get color based on health status
 */
function getHealthColor(health) {
    if (health === 'healthy') return ChartColors.success;
    if (health === 'warning') return ChartColors.warning;
    return ChartColors.danger;
}

/**
 * Create a line chart
 */
function createLineChart(canvasId, labels, data, label, color) {
    const ctx = document.getElementById(canvasId).getContext('2d');

    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: label,
                data: data,
                borderColor: color,
                backgroundColor: color.replace('0.8', '0.2'),
                tension: 0.1,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

/**
 * Create a bar chart
 */
function createBarChart(canvasId, labels, data, label, colors) {
    const ctx = document.getElementById(canvasId).getContext('2d');

    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: label,
                data: data,
                backgroundColor: colors || ChartColors.primary
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

/**
 * Create a pie/doughnut chart
 */
function createPieChart(canvasId, labels, data, colors) {
    const ctx = document.getElementById(canvasId).getContext('2d');

    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

/**
 * Update chart data
 */
function updateChartData(chart, labels, data) {
    if (!chart) return;

    chart.data.labels = labels;
    chart.data.datasets[0].data = data;
    chart.update();
}

/**
 * Destroy chart if exists
 */
function destroyChart(chart) {
    if (chart) {
        chart.destroy();
    }
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        ChartColors,
        formatCurrency,
        formatPercent,
        formatLargeNumber,
        getROIColor,
        getHealthColor,
        createLineChart,
        createBarChart,
        createPieChart,
        updateChartData,
        destroyChart
    };
}
