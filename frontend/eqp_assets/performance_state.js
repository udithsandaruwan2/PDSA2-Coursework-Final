document.addEventListener('DOMContentLoaded', async () => {
    const renderCharts = (data) => {
        // Bar Chart
        const barCtx = document.getElementById('barChart').getContext('2d');
        new Chart(barCtx, {
            type: 'bar',
            data: {
                labels: data.rounds,
                datasets: [
                    {
                        label: 'Sequential',
                        data: data.sequential_times,
                        backgroundColor: 'rgba(43, 108, 176, 0.6)',
                        borderColor: '#2b6cb0',
                        borderWidth: 1
                    },
                    {
                        label: 'Parallel',
                        data: data.parallel_times,
                        backgroundColor: 'rgba(56, 178, 172, 0.6)',
                        borderColor: '#38b2ac',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Run Number (Most Recent Last)',
                            font: { size: 12 }
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Execution Time (seconds)',
                            font: { size: 12 }
                        },
                        beginAtZero: true
                    }
                },
                plugins: {
                    legend: { position: 'top' },
                    title: {
                        display: true,
                        text: 'Sequential vs. Parallel Execution Times (Bar)',
                        font: { size: 14 }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.dataset.label || '';
                                const time = context.parsed.y.toFixed(2);
                                const index = context.dataIndex;
                                const solutions = context.dataset.label === 'Sequential'
                                    ? data.sequential_solutions[index]
                                    : data.parallel_solutions[index];
                                return `${label}: ${time} seconds, Solutions: ${solutions}`;
                            }
                        }
                    }
                }
            }
        });

        // Line Chart
        const lineCtx = document.getElementById('lineChart').getContext('2d');
        new Chart(lineCtx, {
            type: 'line',
            data: {
                labels: data.rounds,
                datasets: [
                    {
                        label: 'Sequential',
                        data: data.sequential_times,
                        borderColor: '#2b6cb0',
                        backgroundColor: 'rgba(43, 108, 176, 0.1)',
                        fill: false,
                        tension: 0.1
                    },
                    {
                        label: 'Parallel',
                        data: data.parallel_times,
                        borderColor: '#38b2ac',
                        backgroundColor: 'rgba(56, 178, 172, 0.1)',
                        fill: false,
                        tension: 0.1
                    }
                ]
            },
            options: {
                responsive: true,
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Run Number (Most Recent Last)',
                            font: { size: 12 }
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Execution Time (seconds)',
                            font: { size: 12 }
                        },
                        beginAtZero: true
                    }
                },
                plugins: {
                    legend: { position: 'top' },
                    title: {
                        display: true,
                        text: 'Sequential vs. Parallel Execution Times (Line)',
                        font: { size: 14 }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.dataset.label || '';
                                const time = context.parsed.y.toFixed(2);
                                const index = context.dataIndex;
                                const solutions = context.dataset.label === 'Sequential'
                                    ? data.sequential_solutions[index]
                                    : data.parallel_solutions[index];
                                return `${label}: ${time} seconds, Solutions: ${solutions}`;
                            }
                        }
                    }
                }
            }
        });
    };

    try {
        const response = await fetch('http://localhost:5000/api/eight_queens/get_performance_stats');
        const data = await response.json();

        if (!data.success) {
            alert('Error fetching performance statistics: ' + (data.message || 'Unknown error'));
            return;
        }

        renderCharts(data);
    } catch (error) {
        console.error('Error fetching performance stats:', error);
        alert('Failed to load performance statistics. Check the console for details.');
    }
});
