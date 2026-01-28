import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export interface DashboardSummary {
    total_bugs: number;
    total_test_failures: number;
    total_code_reviews: number;
    total_deployment_issues: number;
    pattern_effectiveness_score: number;
    top_patterns: Array<{ pattern: string; count: number }>;
    recent_activity: Array<{ type: string; description: string; timestamp: string; severity: string }>;
}

export interface ChartData {
    labels: string[];
    datasets: Array<{
        label?: string;
        data: number[];
        borderColor?: string;
        backgroundColor?: string | string[];
        tension?: number;
    }>;
}

export const fetchDashboardSummary = async (dateRange: string = '30d'): Promise<DashboardSummary> => {
    const response = await apiClient.get(`/dashboard/summary?date_range=${dateRange}`);
    return response.data;
};

export const fetchPatternsOverTime = async (dateRange: string = '30d'): Promise<ChartData> => {
    const response = await apiClient.get(`/dashboard/charts/patterns-over-time?date_range=${dateRange}`);
    return response.data;
};

export const fetchSeverityDistribution = async (dateRange: string = '30d'): Promise<ChartData> => {
    const response = await apiClient.get(`/dashboard/charts/severity-distribution?date_range=${dateRange}`);
    return response.data;
};

export const fetchPatternEffectiveness = async (dateRange: string = '30d'): Promise<ChartData> => {
    const response = await apiClient.get(`/dashboard/charts/pattern-effectiveness?date_range=${dateRange}`);
    return response.data;
};
