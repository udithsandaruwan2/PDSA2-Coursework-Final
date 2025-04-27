document.addEventListener('DOMContentLoaded', async () => {
    const urlParams = new URLSearchParams(window.location.search);
    const tableName = urlParams.get('table');
    const tableTitle = document.getElementById('tableTitle');
    const tableHead = document.getElementById('tableHead');
    const tableBody = document.getElementById('tableBody');

    if (!tableName) {
        tableTitle.textContent = 'Error: No table specified';
        return;
    }

    const tableConfigs = {
        eqp_solutions: {
            title: 'Precomputed Solutions',
            headers: ['ID', 'Solution'],
            fields: ['id', 'solution']
        },
        eqp_submissions: {
            title: 'Player Submissions',
            headers: ['ID', 'Username', 'Solution', 'Submitted At'],
            fields: ['id', 'username', 'solution', 'submitted_at']
        },
        eqp_performance: {
            title: 'Performance Metrics',
            headers: ['ID', 'Algorithm Type', 'Execution Time (s)', 'Total Solutions', 'Recorded At'],
            fields: ['id', 'algorithm_type', 'execution_time', 'total_solutions', 'recorded_at']
        }
    };

    const config = tableConfigs[tableName];
    if (!config) {
        tableTitle.textContent = 'Error: Invalid table name';
        return;
    }

    tableTitle.textContent = config.title;

    // Set table headers
    tableHead.innerHTML = `<tr>${config.headers.map(h => `<th>${h}</th>`).join('')}</tr>`;

    try {
        const response = await fetch('http://localhost:5000/api/eight_queens/get_full_table?table=' + tableName);
        const data = await response.json();

        if (data.success && data.data) {
            tableBody.innerHTML = data.data.map(row => {
                return `<tr>${config.fields.map(field => {
                    let value = row[field];
                    if (field === 'execution_time') {
                        value = parseFloat(value).toFixed(2);
                    } else if (field === 'solution') {
                        value = value.substring(0, 16) + '...';
                    } else if (field === 'submitted_at' || field === 'recorded_at') {
                        value = new Date(value).toLocaleString('en-US', {
                            timeZone: 'Asia/Colombo',
                            dateStyle: 'medium',
                            timeStyle: 'short'
                        });
                    }
                    return `<td>${value}</td>`;
                }).join('')}</tr>`;
            }).join('');
        } else {
            tableBody.innerHTML = '<tr><td colspan="' + config.headers.length + '">No data available</td></tr>';
        }
    } catch (error) {
        console.error('Error fetching table data:', error);
        tableBody.innerHTML = '<tr><td colspan="' + config.headers.length + '">Error loading data</td></tr>';
    }
});
