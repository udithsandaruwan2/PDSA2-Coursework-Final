document.addEventListener("DOMContentLoaded", () => {
    console.log("Fetching algorithm statistics...");
    fetch('http://127.0.0.1:5000/api/tsp_assets/get_algorithm_stats')
        .then(response => {
            if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
            return response.json();
        })
        .then(data => {
            console.log("Algorithm stats data:", data);
            if (data.error) {
                alert("Error fetching algorithm statistics: " + data.error);
                return;
            }

            const ctx = document.getElementById('algorithmChart').getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.rounds,  // X-axis: Game rounds (1 to 10)
                    datasets: [
                        {
                            label: 'Nearest Neighbor',
                            data: data.nn_times,
                            borderColor: '#008000',  // Green
                            backgroundColor: 'rgba(0, 128, 0, 0.1)',
                            fill: false,
                            tension: 0.1,
                            cityCounts: data.city_counts  // Attach city counts for tooltips
                        },
                        {
                            label: 'Branch and Bound',
                            data: data.bb_times,
                            borderColor: '#800080',  // Purple
                            backgroundColor: 'rgba(128, 0, 128, 0.1)',
                            fill: false,
                            tension: 0.1,
                            cityCounts: data.city_counts
                        },
                        {
                            label: 'Held-Karp',
                            data: data.hk_times,
                            borderColor: '#FFA500',  // Orange
                            backgroundColor: 'rgba(255, 165, 0, 0.1)',
                            fill: false,
                            tension: 0.1,
                            cityCounts: data.city_counts
                        }
                    ]
                },
                options: {
                    responsive: true,
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'Game Round (Round 10 is Most Recent)',
                                font: { size: 14 }
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: 'Execution Time (ms)',
                                font: { size: 14 }
                            },
                            beginAtZero: true
                        }
                    },
                    plugins: {
                        legend: {
                            position: 'top'
                        },
                        title: {
                            display: true,
                            text: 'Algorithm Execution Times Over Recent Game Rounds',
                            font: { size: 16 }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const label = context.dataset.label || '';
                                    const time = context.parsed.y.toFixed(2);
                                    const roundIndex = context.dataIndex;
                                    const cityCount = context.dataset.cityCounts[roundIndex];
                                    return `${label}: ${time} ms (Cities: ${cityCount})`;
                                }
                            }
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error("Error fetching algorithm stats:", error);
            alert("Failed to load algorithm statistics. Check the console for details.");
        });
});