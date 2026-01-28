import React, { useEffect, useState } from 'react';
import {
    AppBar,
    Box,
    Container,
    Toolbar,
    Typography,
    CircularProgress,
    Alert,
} from '@mui/material';
import {
    BugReport,
    Cancel,
    RateReview,
    TrendingUp,
} from '@mui/icons-material';
import { SummaryCard } from './SummaryCard';
import { PatternChart } from './PatternChart';
import {
    fetchDashboardSummary,
    fetchPatternsOverTime,
    fetchSeverityDistribution,
    fetchPatternEffectiveness,
    DashboardSummary,
    ChartData,
} from '../api/client';

export const Dashboard: React.FC = () => {
    const [summary, setSummary] = useState<DashboardSummary | null>(null);
    const [patternsOverTime, setPatternsOverTime] = useState<ChartData | null>(null);
    const [severityDistribution, setSeverityDistribution] = useState<ChartData | null>(null);
    const [patternEffectiveness, setPatternEffectiveness] = useState<ChartData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const loadData = async () => {
            try {
                setLoading(true);
                const [summaryData, patternsData, severityData, effectivenessData] = await Promise.all([
                    fetchDashboardSummary(),
                    fetchPatternsOverTime(),
                    fetchSeverityDistribution(),
                    fetchPatternEffectiveness(),
                ]);
                setSummary(summaryData);
                setPatternsOverTime(patternsData);
                setSeverityDistribution(severityData);
                setPatternEffectiveness(effectivenessData);
                setError(null);
            } catch (err) {
                setError('Failed to load dashboard data. Please try again later.');
                console.error('Dashboard error:', err);
            } finally {
                setLoading(false);
            }
        };

        loadData();
    }, []);

    if (loading) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
                <CircularProgress size={60} />
            </Box>
        );
    }

    if (error) {
        return (
            <Container maxWidth="lg" sx={{ mt: 4 }}>
                <Alert severity="error">{error}</Alert>
            </Container>
        );
    }

    return (
        <Box sx={{ flexGrow: 1 }}>
            <AppBar position="static" elevation={0} sx={{ backgroundColor: 'background.paper' }}>
                <Toolbar>
                    <Typography variant="h5" component="div" sx={{ flexGrow: 1, fontWeight: 700 }}>
                        Feedback Loop Analytics
                    </Typography>
                </Toolbar>
            </AppBar>

            <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
                {/* Summary Cards */}
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3, mb: 3 }}>
                    <Box sx={{ flex: '1 1 calc(25% - 18px)', minWidth: '250px' }}>
                        <SummaryCard
                            title="Total Bugs"
                            value={summary?.total_bugs || 0}
                            icon={BugReport}
                            color="#ef4444"
                        />
                    </Box>
                    <Box sx={{ flex: '1 1 calc(25% - 18px)', minWidth: '250px' }}>
                        <SummaryCard
                            title="Test Failures"
                            value={summary?.total_test_failures || 0}
                            icon={Cancel}
                            color="#f59e0b"
                        />
                    </Box>
                    <Box sx={{ flex: '1 1 calc(25% - 18px)', minWidth: '250px' }}>
                        <SummaryCard
                            title="Code Reviews"
                            value={summary?.total_code_reviews || 0}
                            icon={RateReview}
                            color="#6366f1"
                        />
                    </Box>
                    <Box sx={{ flex: '1 1 calc(25% - 18px)', minWidth: '250px' }}>
                        <SummaryCard
                            title="Effectiveness"
                            value={`${Math.round((summary?.pattern_effectiveness_score || 0) * 100)}%`}
                            icon={TrendingUp}
                            color="#10b981"
                        />
                    </Box>
                </Box>

                {/* Charts */}
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3 }}>
                    <Box sx={{ flex: '1 1 calc(66.66% - 12px)', minWidth: '300px' }}>
                        {patternsOverTime && (
                            <PatternChart
                                title="Patterns Over Time"
                                data={patternsOverTime}
                                type="line"
                            />
                        )}
                    </Box>
                    <Box sx={{ flex: '1 1 calc(33.33% - 12px)', minWidth: '300px' }}>
                        {severityDistribution && (
                            <PatternChart
                                title="Severity Distribution"
                                data={severityDistribution}
                                type="pie"
                            />
                        )}
                    </Box>
                    <Box sx={{ flex: '1 1 100%' }}>
                        {patternEffectiveness && (
                            <PatternChart
                                title="Pattern Effectiveness"
                                data={patternEffectiveness}
                                type="bar"
                            />
                        )}
                    </Box>
                </Box>
            </Container>
        </Box>
    );
};
