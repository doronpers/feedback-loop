import React from 'react';
import { Card, CardContent, Typography, Box } from '@mui/material';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    BarElement,
    ArcElement,
    Title,
    Tooltip,
    Legend,
    Filler,
} from 'chart.js';
import { Line, Bar, Pie } from 'react-chartjs-2';
import type { ChartData } from '../api/client';

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    BarElement,
    ArcElement,
    Title,
    Tooltip,
    Legend,
    Filler
);

interface PatternChartProps {
    title: string;
    data: ChartData;
    type: 'line' | 'bar' | 'pie';
}

export const PatternChart: React.FC<PatternChartProps> = ({ title, data, type }) => {
    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'top' as const,
                labels: {
                    color: '#cbd5e1',
                    font: {
                        family: 'Inter',
                    },
                },
            },
            title: {
                display: false,
            },
        },
        scales:
            type !== 'pie'
                ? {
                    x: {
                        ticks: { color: '#cbd5e1' },
                        grid: { color: '#334155' },
                    },
                    y: {
                        ticks: { color: '#cbd5e1' },
                        grid: { color: '#334155' },
                    },
                }
                : undefined,
    };

    const renderChart = () => {
        switch (type) {
            case 'line':
                return <Line data={data} options={options} />;
            case 'bar':
                return <Bar data={data} options={options} />;
            case 'pie':
                return <Pie data={data} options={options} />;
            default:
                return null;
        }
    };

    return (
        <Card>
            <CardContent>
                <Typography variant="h6" gutterBottom>
                    {title}
                </Typography>
                <Box sx={{ height: 300, mt: 2 }}>{renderChart()}</Box>
            </CardContent>
        </Card>
    );
};
