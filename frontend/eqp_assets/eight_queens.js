document.addEventListener('DOMContentLoaded', function () {
    class QueensGame {
        constructor() {
            this.board = document.getElementById('board');
            if (!this.board) {
                console.error('Board element not found!');
                return;
            }
            this.queenCounter = document.getElementById('queenCount');
            this.solutionCounter = document.getElementById('solutionCount');
            this.progressFill = document.getElementById('progressFill');
            this.usernameInput = document.getElementById('username');
            this.queensPlaced = 0;
            this.boardState = Array(8).fill().map(() => Array(8).fill(0));
            this.chartInstance = null;

            // Initialize the game
            this.initializeBoard();
            this.initializeControls();
            this.fetchSolutions();
            this.fetchPerformanceMetrics();
        }

        initializeBoard() {
            console.log('Initializing the board...');
            this.board.innerHTML = '';
            let squareCount = 0;
            for (let row = 0; row < 8; row++) {
                for (let col = 0; col < 8; col++) {
                    const square = document.createElement('div');
                    square.className = `square ${(row + col) % 2 === 0 ? 'white' : 'black'}`;
                    square.dataset.row = row;
                    square.dataset.col = col;
                    square.setAttribute('aria-label', `Square at row ${row + 1}, column ${col + 1}`);
                    square.addEventListener('click', this.handleSquareClick.bind(this));
                    this.board.appendChild(square);
                    squareCount++;
                }
            }
            console.log(`Added ${squareCount} squares to the board`);
        }

        handleSquareClick(event) {
            const square = event.target;
            const row = parseInt(square.dataset.row);
            const col = parseInt(square.dataset.col);

            if (!square.classList.contains('has-queen')) {
                if (this.queensPlaced < 8) {
                    square.classList.add('has-queen');
                    this.boardState[row][col] = 1;
                    this.queensPlaced++;
                    this.updateHints();
                } else {
                    document.getElementById('results').innerHTML = '<p class="error">You can only place 8 queens.</p>';
                }
            } else {
                square.classList.remove('has-queen');
                this.boardState[row][col] = 0;
                this.queensPlaced--;
                this.updateHints();
            }

            this.queenCounter.textContent = this.queensPlaced;
            console.log('Current board state:', this.boardState);
            console.log('Queens placed:', this.queensPlaced);
        }

        updateHints() {
            const squares = document.querySelectorAll('.square');
            squares.forEach(square => {
                const row = parseInt(square.dataset.row);
                const col = parseInt(square.dataset.col);
                square.classList.remove('conflict', 'safe');
            });
        
            // Find queen positions
            const queens = [];
            for (let r = 0; r < 8; r++) {
                for (let c = 0; c < 8; c++) {
                    if (this.boardState[r][c] === 1) queens.push([r, c]);
                }
            }
        
            // Check for conflicts
            const conflicts = new Set();
            for (let i = 0; i < queens.length; i++) {
                const [r1, c1] = queens[i];
                for (let j = i + 1; j < queens.length; j++) {
                    const [r2, c2] = queens[j];
                    if (r1 === r2 || c1 === c2 || Math.abs(r1 - r2) === Math.abs(c1 - c2)) {
                        conflicts.add(`${r1},${c1}`);
                        conflicts.add(`${r2},${c2}`);
                    }
                }
            }
        
            // Update square styles
            squares.forEach(square => {
                const row = parseInt(square.dataset.row);
                const col = parseInt(square.dataset.col);
                if (this.boardState[row][col] === 1 && conflicts.has(`${row},${col}`)) {
                    square.classList.add('conflict');
                } else if (this.boardState[row][col] === 0 && this.queensPlaced < 8) {
                    let safe = true;
                    for (const [qr, qc] of queens) {
                        if (row === qr || col === qc || Math.abs(row - qr) === Math.abs(col - qc)) {
                            safe = false;
                            break;
                        }
                    }
                    if (safe) square.classList.add('safe');
                }
            });
        
            // Update results with hint
            const resultsDiv = document.getElementById('results');
            if (conflicts.size > 0) {
                resultsDiv.innerHTML = '<p class="error">Some queens are threatening each other!</p>';
            } else if (this.queensPlaced > 0) {
                resultsDiv.innerHTML = '<p style="color: green;">No conflicts detected. Keep going!</p>';
            } else {
                resultsDiv.innerHTML = '';
            }
        }

        undoMove() {
            for (let r = 7; r >= 0; r--) {
                for (let c = 7; c >= 0; c--) {
                    if (this.boardState[r][c] === 1) {
                        this.boardState[r][c] = 0;
                        const square = document.querySelector(`.square[data-row="${r}"][data-col="${c}"]`);
                        square.classList.remove('has-queen');
                        this.queensPlaced--;
                        this.queenCounter.textContent = this.queensPlaced;
                        this.updateHints();
                        return;
                    }
                }
            }
        }

        resetBoard() {
            console.log('Resetting the board...');
            this.queensPlaced = 0;
            this.boardState = Array(8).fill().map(() => Array(8).fill(0));
            this.queenCounter.textContent = '0';
            this.initializeBoard();
            document.getElementById('results').innerHTML = '';
            if (this.chartInstance) {
                this.chartInstance.destroy();
                this.chartInstance = null;
            }
        }

        initializeControls() {
            document.getElementById('computeBtn').addEventListener('click', () => this.computeSolutions());
            document.getElementById('validateBtn').addEventListener('click', () => this.validateSolution());
            document.getElementById('undoBtn').addEventListener('click', () => this.undoMove());
            document.getElementById('resetBtn').addEventListener('click', () => this.resetBoard());
            document.getElementById('viewDbBtn').addEventListener('click', () => this.viewDatabase());
            document.getElementById('viewStatsBtn').addEventListener('click', () => this.runAndViewStats());
            document.getElementById('viewPlayerStatsBtn').addEventListener('click', () => {
                window.open('eqp_assets/player_stats.html', '_blank');
            });
        }

        async computeSolutions() {
            const computeBtn = document.getElementById('computeBtn');
            computeBtn.disabled = true;
            const resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = '<p>Computing one round of solutions...</p>';

            try {
                const response = await fetch('http://localhost:5000/api/eight_queens/compute_solutions', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
                const data = await response.json();
                if (data.success) {
                    resultsDiv.innerHTML = '<p style="color: green;">Computed one round of solutions successfully!</p>';
                    this.fetchPerformanceMetrics();
                    this.fetchSolutions();
                    if (this.chartInstance) {
                        this.chartInstance.destroy();
                        this.chartInstance = null;
                    }
                } else {
                    resultsDiv.innerHTML = `<p class="error">Error: ${data.message || 'Error computing solutions.'}</p>`;
                }
            } catch (error) {
                console.error('Error computing solutions:', error);
                resultsDiv.innerHTML = `<p class="error">An error occurred while computing solutions: ${error.message}</p>`;
            } finally {
                computeBtn.disabled = false;
            }
        }

        async runPerformanceTest() {
            const rounds = 10;
            const resultsDiv = document.getElementById('results');
            const runBtn = document.getElementById('runPerformanceBtn');
            const computeBtn = document.getElementById('computeBtn');
        
            runBtn.disabled = true;
            computeBtn.disabled = true;
            resultsDiv.innerHTML = `<p>Running random solution performance test (0 of ${rounds} completed)...</p>`;
        
            try {
                const performanceData = {
                    rounds: [],
                    sequential_times: [],
                    sequential_solutions: []
                };
        
                for (let i = 0; i < rounds; i++) {
                    const response = await fetch('http://localhost:5000/api/eight_queens/validate_random_solution', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' }
                    });
                    if (!response.ok) throw new Error(`Run ${i + 1} failed: ${response.status}`);
                    const data = await response.json();
                    if (!data.success) throw new Error(`Run ${i + 1} failed: ${data.message}`);
                    
                    performanceData.rounds.push(String(i + 1));
                    performanceData.sequential_times.push(data.execution_time);
                    performanceData.sequential_solutions.push(data.solution_count);
                    resultsDiv.innerHTML = `<p>Running random solution performance test (${i + 1} of ${rounds} completed)...</p>`;
                }
        
                resultsDiv.innerHTML = `<p style="color: green;">Completed ${rounds} random solution performance runs.</p>`;
                this.fetchPerformanceMetrics();
        
                // Open a popup with the performance chart
                const popup = window.open('', 'RandomSolutionPerformanceChart', 'width=900,height=600');
                popup.document.write(`
                    <!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>Random Solution Performance Chart</title>
                        <link rel="stylesheet" href="eqp_assets/eight_queens.css">
                        <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
                        <style>
                            body { margin: 20px; background: #f7fafc; }
                            #chartContainer { max-width: 800px; margin: 0 auto; background: #ffffff; border-radius: 10px; padding: 20px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); }
                            .close-btn { display: block; margin: 20px auto; padding: 10px 20px; background: #2b6cb0; color: white; border: none; border-radius: 6px; cursor: pointer; }
                            .close-btn:hover { background: #1a4971; }
                        </style>
                    </head>
                    <body>
                        <div id="chartContainer">
                            <canvas id="performanceChart" width="800" height="400"></canvas>
                        </div>
                        <button class="close-btn" onclick="window.close()">Close</button>
                        <script>
                            const data = ${JSON.stringify(performanceData)};
                            const ctx = document.getElementById('performanceChart').getContext('2d');
                            new Chart(ctx, {
                                type: 'bar',
                                data: {
                                    labels: data.rounds,
                                    datasets: [{
                                        label: 'Sequential (Random Solutions)',
                                        data: data.sequential_times,
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
                                                text: 'Run Number',
                                                font: { size: 14 }
                                            }
                                        },
                                        y: {
                                            title: {
                                                display: true,
                                                text: 'Execution Time (seconds)',
                                                font: { size: 14 }
                                            },
                                            beginAtZero: true
                                        }
                                    },
                                    plugins: {
                                        legend: { position: 'top' },
                                        title: {
                                            display: true,
                                            text: 'Execution Times for Random Solution Validation',
                                            font: { size: 16 }
                                        },
                                        tooltip: {
                                            callbacks: {
                                                label: function(context) {
                                                    const time = context.parsed.y.toFixed(2);
                                                    const index = context.dataIndex;
                                                    const solutions = data.sequential_solutions[index];
                                                    return \`Sequential: \${time} seconds, Solutions: \${solutions}\`;
                                                }
                                            }
                                        }
                                    }
                                }
                            });
                        </script>
                    </body>
                    </html>
                `);
                popup.document.close();
        
            } catch (error) {
                console.error('Error running performance test:', error);
                resultsDiv.innerHTML = `<p class="error">Error running performance test: ${error.message}</p>`;
            } finally {
                runBtn.disabled = false;
                computeBtn.disabled = false;
            }
        }

        renderPerformanceChart(data) {
            if (this.chartInstance) {
                this.chartInstance.destroy();
            }

            const ctx = document.getElementById('performanceChart').getContext('2d');
            this.chartInstance = new Chart(ctx, {
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
                                text: 'Run Number (Run 10 is Most Recent)',
                                font: { size: 14 }
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: 'Execution Time (seconds)',
                                font: { size: 14 }
                            },
                            beginAtZero: true
                        }
                    },
                    plugins: {
                        legend: { position: 'top' },
                        title: {
                            display: true,
                            text: 'Sequential vs. Parallel Execution Times (Last 10 Runs)',
                            font: { size: 16 }
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
        }

        async validateSolution() {
            const username = this.usernameInput.value.trim();
            const resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = ''; // Clear previous messages

            if (!username) {
                resultsDiv.innerHTML = '<p class="error">Please enter your username.</p>';
                return;
            }
            if (this.queensPlaced !== 8) {
                resultsDiv.innerHTML = '<p class="error">Please place exactly 8 queens.</p>';
                return;
            }

            try {
                const response = await fetch('http://localhost:5000/api/eight_queens/submit_solution', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, board: this.boardState })
                });
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                const data = await response.json();

                if (data.message.includes('Game reset')) {
                    resultsDiv.innerHTML = `<p style="color: green;">${data.message}</p>`;
                    document.getElementById('validateBtn').disabled = false;
                    this.fetchSolutions();
                    this.resetBoard();
                } else if (data.message.includes('already been submitted')) {
                    const emptyRows = [];
                    for (let r = 0; r < 8; r++) {
                        if (this.boardState[r].every(cell => cell === 0)) emptyRows.push(r + 1);
                    }
                    const hint = emptyRows.length > 0
                        ? `Try placing a queen in row ${emptyRows[0]}.`
                        : 'Try a different configuration.';
                    resultsDiv.innerHTML = `<p style="color: orange;">${data.message} ${hint}</p>`;
                } else if (data.success) {
                    resultsDiv.innerHTML = `<p style="color: green;">${data.message} (${data.unique_solutions}/92 unique solutions found)</p>`;
                    this.fetchSolutions();
                    // Do not reset board automatically to allow further modifications
                } else {
                    resultsDiv.innerHTML = `<p class="error">Error: ${data.message}</p>`;
                }
            } catch (error) {
                console.error('Error validating solution:', error);
                resultsDiv.innerHTML = `<p class="error">Failed to submit solution: ${error.message}</p>`;
            }
        }

        async fetchSolutions() {
            try {
                const response = await fetch('http://localhost:5000/api/eight_queens/get_solutions');
                const data = await response.json();

                console.log('Solutions data:', data);

                const leaderboardList = document.getElementById('leaderboardList');
                leaderboardList.innerHTML = '';

                if (data.success && data.submitted_solutions && data.submitted_solutions.length > 0) {
                    const playerScores = {};
                    data.submitted_solutions.forEach(submission => {
                        const username = submission.username;
                        if (!playerScores[username]) {
                            playerScores[username] = 0;
                        }
                        playerScores[username]++;
                    });

                    const sortedPlayers = Object.entries(playerScores).sort((a, b) => b[1] - a[1]);
                    sortedPlayers.forEach(([username, score]) => {
                        const listItem = document.createElement('li');
                        listItem.textContent = `Player: ${username}, Solutions: ${score}`;
                        leaderboardList.appendChild(listItem);
                    });

                    // Update progress bar
                    const uniqueCount = new Set(data.submitted_solutions.map(s => s.solution)).size;
                    this.solutionCounter.textContent = uniqueCount;
                    this.progressFill.style.width = `${(uniqueCount / 92) * 100}%`;
                    const progressBar = document.getElementById('progressBar');
                    progressBar.setAttribute('data-complete', uniqueCount === 92 ? 'true' : 'false');
                } else {
                    leaderboardList.innerHTML = '<li>No solutions submitted yet.</li>';
                    this.solutionCounter.textContent = '0';
                    this.progressFill.style.width = '0%';
                    document.getElementById('progressBar').setAttribute('data-complete', 'false');
                }
            } catch (error) {
                console.error('Error fetching solutions:', error);
            }
        }

        async fetchPerformanceMetrics() {
            try {
                const response = await fetch('http://localhost:5000/api/eight_queens/get_performance');
                const data = await response.json();
        
                console.log('Performance metrics:', data);
        
                const metricsDiv = document.getElementById('performanceMetrics');
                metricsDiv.innerHTML = '';
        
                if (data.success && data.performance_metrics && data.performance_metrics.length > 0) {
                    // Sort by recorded_at (descending) and take the 10 most recent
                    const recentMetrics = data.performance_metrics
                        .sort((a, b) => new Date(b.recorded_at) - new Date(a.recorded_at))
                        .slice(0, 10);
                    
                    recentMetrics.forEach(metric => {
                        const p = document.createElement('p');
                        p.textContent = `${metric.algorithm_type.charAt(0).toUpperCase() + metric.algorithm_type.slice(1)}: ${
                            metric.total_solutions
                        } solutions in ${metric.execution_time.toFixed(2)} seconds (Recorded: ${new Date(metric.recorded_at).toLocaleString('en-US', {
                            timeZone: 'Asia/Colombo',
                            dateStyle: 'medium',
                            timeStyle: 'short'
                        })})`;
                        metricsDiv.appendChild(p);
                    });
                } else {
                    metricsDiv.innerHTML = '<p>No performance metrics available.</p>';
                }
            } catch (error) {
                console.error('Error fetching performance metrics:', error);
                const metricsDiv = document.getElementById('performanceMetrics');
                metricsDiv.innerHTML = '<p class="error">Error loading performance metrics.</p>';
            }
        }

        async viewDatabase() {
            try {
                const response = await fetch('http://localhost:5000/api/eight_queens/get_database');
                const data = await response.json();
                console.log('Database data:', data);

                const dbContentsDiv = document.getElementById('databaseContents');
                dbContentsDiv.innerHTML = '';

                if (data.success) {
                    const submissionsCard = document.createElement('div');
                    submissionsCard.className = 'db-card';
                    submissionsCard.innerHTML = '<h3>Player Submissions (eqp_submissions) - Last 10</h3>';
                    if (data.eqp_submissions && data.eqp_submissions.length > 0) {
                        data.eqp_submissions.forEach(row => {
                            const p = document.createElement('p');
                            const sriLankaTime = new Date(row.submitted_at).toLocaleString('en-US', {
                                timeZone: 'Asia/Colombo',
                                dateStyle: 'medium',
                                timeStyle: 'short'
                            });
                            p.textContent = `ID: ${row.id}, Username: ${row.username}, Solution: ${row.solution.substring(0, 16)}..., Submitted At: ${sriLankaTime}`;
                            submissionsCard.appendChild(p);
                        });
                        const link = document.createElement('a');
                        link.href = 'eqp_assets/view_table.html?table=eqp_submissions';
                        link.textContent = 'View All Submissions';
                        link.className = 'db-link';
                        submissionsCard.appendChild(link);
                    } else {
                        submissionsCard.innerHTML += '<p>No submissions available.</p>';
                    }
                    dbContentsDiv.appendChild(submissionsCard);

                    const performanceCard = document.createElement('div');
                    performanceCard.className = 'db-card';
                    performanceCard.innerHTML = '<h3>Performance Metrics (eqp_performance) - Last 10</h3>';
                    if (data.eqp_performance && data.eqp_performance.length > 0) {
                        data.eqp_performance.forEach(row => {
                            const p = document.createElement('p');
                            const sriLankaTime = new Date(row.recorded_at).toLocaleString('en-US', {
                                timeZone: 'Asia/Colombo',
                                dateStyle: 'medium',
                                timeStyle: 'short'
                            });
                            p.textContent = `ID: ${row.id}, Algorithm: ${row.algorithm_type}, Time: ${row.execution_time.toFixed(2)}s, Solutions: ${row.total_solutions}, Recorded At: ${sriLankaTime}`;
                            performanceCard.appendChild(p);
                        });
                        const link = document.createElement('a');
                        link.href = 'eqp_assets/view_table.html?table=eqp_performance';
                        link.textContent = 'View All Performance Metrics';
                        link.className = 'db-link';
                        performanceCard.appendChild(link);
                    } else {
                        performanceCard.innerHTML += '<p>No performance metrics available.</p>';
                    }
                    dbContentsDiv.appendChild(performanceCard);
                } else {
                    dbContentsDiv.innerHTML = `<p class="error">Error: ${data.message || 'Failed to load database data.'}</p>`;
                }
            } catch (error) {
                console.error('Error fetching database data:', error);
                document.getElementById('databaseContents').innerHTML = '<p class="error">An error occurred while fetching database data.</p>';
            }
        }

        async runAndViewStats() {
            const roundsInput = document.getElementById('roundsInput').value;
            const rounds = parseInt(roundsInput) || 10;
            const resultsDiv = document.getElementById('results');
            const viewStatsBtn = document.getElementById('viewStatsBtn');
            const computeBtn = document.getElementById('computeBtn');
        
            if (rounds < 1) {
                resultsDiv.innerHTML = '<p class="error">Please enter a positive number of rounds.</p>';
                return;
            }
        
            viewStatsBtn.disabled = true;
            computeBtn.disabled = true;
            resultsDiv.innerHTML = `<p>Running algorithms for ${rounds} rounds...</p>`;
        
            try {
                const response = await fetch('http://localhost:5000/api/eight_queens/run_algorithm_rounds', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ rounds })
                });
                const data = await response.json();
        
                if (!data.success) {
                    throw new Error(data.message || 'Failed to run algorithm rounds');
                }
        
                resultsDiv.innerHTML = `<p style="color: green;">Completed ${rounds} rounds of algorithm execution.</p>`;
                this.fetchPerformanceMetrics();
        
                // Verify performance_stats.html exists before opening
                const checkResponse = await fetch('eqp_assets/performance_stats.html', { method: 'HEAD' });
                if (checkResponse.ok) {
                    window.open('eqp_assets/performance_stats.html', '_blank');
                } else {
                    throw new Error('Performance stats page not found');
                }
            } catch (error) {
                console.error('Error running algorithm rounds:', error);
                resultsDiv.innerHTML = `<p class="error">Error: ${error.message}</p>`;
            } finally {
                viewStatsBtn.disabled = false;
                computeBtn.disabled = false;
            }
        }
    }

    const game = new QueensGame();
});
