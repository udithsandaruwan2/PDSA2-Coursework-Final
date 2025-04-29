document.addEventListener('DOMContentLoaded', async () => {
    console.log('Fetching player statistics...');
    try {
        const response = await fetch('http://localhost:5000/api/eight_queens/get_player_stats');
        const data = await response.json();

        console.log('Player stats data:', data);
        if (!data.success) {
            alert('Error fetching player statistics: ' + (data.message || 'Unknown error'));
            return;
        }

        const ctx = document.getElementById('playerChart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.players,
                datasets: [{
                    label: 'Solutions Submitted',
                    data: data.solution_counts,
                    backgroundColor: 'rgba(43, 108, 176, 0.6)',
                    borderColor: '#2b6cb0',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Player Username',
                            font: { size: 14 }
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Number of Solutions',
                            font: { size: 14 }
                        },
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                },
                plugins: {
                    legend: { position: 'top' },
                    title: {
                        display: true,
                        text: 'Top Players by Solutions Submitted',
                        font: { size: 16 }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error fetching player stats:', error);
        alert('Failed to load player statistics. Check the console for details.');
    }
});