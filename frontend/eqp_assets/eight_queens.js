document.addEventListener('DOMContentLoaded', function () {
    class QueensGame {
        constructor() {
            this.board = document.getElementById('board');
            this.queenCounter = document.getElementById('queenCount');
            this.solutionCounter = document.getElementById('solutionCount');
            this.progressFill = document.getElementById('progressFill');
            this.usernameInput = document.getElementById('username');
            this.roundsInput = document.getElementById('roundsInput');
            this.messagesDiv = document.getElementById('messages');

            if (!this.board || !this.queenCounter || !this.solutionCounter || !this.progressFill || !this.messagesDiv) {
                console.warn('Required DOM elements not found. QueensGame not initialized.');
                return;
            }

            this.queensPlaced = 0;
            this.boardState = Array(8).fill().map(() => Array(8).fill(0));
            this.chartInstance = null;

            this.initializeBoard();
            this.initializeControls();
            this.fetchSolutions();
            this.fetchPerformanceMetrics();
        }

        showMessage(content, type) {
            this.messagesDiv.innerHTML = `<p class="${type}">${content}</p>`;
            this.messagesDiv.classList.remove('pulse');
            void this.messagesDiv.offsetWidth; // Trigger reflow
            this.messagesDiv.classList.add('pulse');
        }

        initializeBoard() {
            console.debug('Initializing the board...');
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
                    this.showMessage('You can only place 8 queens.', 'error');
                }
            } else {
                square.classList.remove('has-queen');
                this.boardState[row][col] = 0;
                this.queensPlaced--;
                this.updateHints();
            }

            if (this.queenCounter) {
                this.queenCounter.textContent = this.queensPlaced;
            }
            console.debug('Current board state:', this.boardState);
            console.debug('Queens placed:', this.queensPlaced);
        }

        updateHints() {
            const squares = document.querySelectorAll('.square');
            squares.forEach(square => {
                const row = parseInt(square.dataset.row);
                const col = parseInt(square.dataset.col);
                square.classList.remove('conflict', 'safe');
            });

            const queens = [];
            for (let r = 0; r < 8; r++) {
                for (let c = 0; c < 8; c++) {
                    if (this.boardState[r][c] === 1) queens.push([r, c]);
                }
            }

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

            if (conflicts.size > 0) {
                this.showMessage('Some queens are threatening each other!', 'error');
            } else if (this.queensPlaced > 0) {
                this.showMessage('No conflicts detected. Keep going!', 'success');
            } else {
                this.messagesDiv.innerHTML = '';
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
                        if (this.queenCounter) {
                            this.queenCounter.textContent = this.queensPlaced;
                        }
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
            if (this.queenCounter) {
                this.queenCounter.textContent = '0';
            }
            this.initializeBoard();
            this.messagesDiv.innerHTML = '';
            if (this.chartInstance) {
                this.chartInstance.destroy();
                this.chartInstance = null;
            }
        }

        initializeControls() {
            const controls = [
                { id: 'computeBtn', handler: () => this.computeSolutions() },
                { id: 'validateBtn', handler: () => this.validateSolution() },
                { id: 'undoBtn', handler: () => this.undoMove() },
                { id: 'resetBtn', handler: () => this.resetBoard() },
                { id: 'viewDbBtn', handler: () => this.viewDatabase() },
                { id: 'viewStatsBtn', handler: () => this.viewStats() },
                { id: 'viewPlayerStatsBtn', handler: () => window.open('eqp_assets/player_stats.html', '_blank') }
            ];

            controls.forEach(({ id, handler }) => {
                const button = document.getElementById(id);
                if (button) {
                    button.addEventListener('click', handler);
                } else {
                    console.warn(`Button #${id} not found.`);
                }
            });
        }

        viewStats() {
            try {
                window.open('eqp_assets/performance_stats.html', '_blank');
            } catch (error) {
                console.error('Error opening performance stats page:', error);
                this.showMessage('Error: Unable to open performance stats page.', 'error');
            }
        }

        async computeSolutions() {
            const computeBtn = document.getElementById('computeBtn');
            const rounds = parseInt(this.roundsInput?.value) || 1;
            if (rounds < 1) {
                this.showMessage('Please enter a positive number of rounds.', 'error');
                return;
            }
            if (computeBtn) computeBtn.disabled = true;
            this.showMessage(`Computing ${rounds} round(s) of solutions...`, 'warning');

            try {
                const response = await fetch('http://localhost:5000/api/eight_queens/compute_solutions', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ rounds })
                });
                const data = await response.json();
                if (data.success) {
                    this.showMessage(`Computed ${rounds} round(s) successfully!`, 'success');
                    this.fetchPerformanceMetrics();
                    this.fetchSolutions();
                    if (this.chartInstance) {
                        this.chartInstance.destroy();
                        this.chartInstance = null;
                    }
                } else {
                    this.showMessage(`Error: ${data.message || 'Error computing solutions.'}`, 'error');
                }
            } catch (error) {
                console.error('Error computing solutions:', error);
                this.showMessage(`An error occurred while computing solutions: ${error.message}`, 'error');
            } finally {
                if (computeBtn) computeBtn.disabled = false;
            }
        }

        async validateSolution() {
            const username = this.usernameInput?.value.trim();
            this.messagesDiv.innerHTML = '';

            if (!username) {
                this.showMessage('Please enter your username.', 'error');
                return;
            }
            if (this.queensPlaced !== 8) {
                this.showMessage('Please place exactly 8 queens.', 'error');
                return;
            }

            try {
                const response = await fetch('http://localhost:5000/api/eight_queens/submit_solution', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, board: this.boardState })
                });
                const data = await response.json();

                if (!response.ok) {
                    this.showMessage(`${data.message || 'Failed to submit solution. Please try again.'}`, 'error');
                    console.warn('Error validating solution:', data.message, 'Status:', response.status);
                    return;
                }

                if (data.message.includes('Game reset')) {
                    this.showMessage(`${data.message}`, 'success');
                    const validateBtn = document.getElementById('validateBtn');
                    if (validateBtn) validateBtn.disabled = false;
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
                    this.showMessage(`${data.message} ${hint}`, 'warning');
                } else if (data.success) {
                    this.showMessage(`${data.message} (${data.unique_solutions}/92 unique solutions found)`, 'success');
                    this.fetchSolutions();
                } else {
                    this.showMessage(`Error: ${data.message}`, 'error');
                }
            } catch (error) {
                console.error('Error validating solution:', error);
                this.showMessage('Failed to submit solution. Please try again.', 'error');
            }
        }

        async fetchSolutions() {
            try {
                const response = await fetch('http://localhost:5000/api/eight_queens/get_solutions');
                const data = await response.json();

                console.debug('Solutions data:', data);

                const leaderboardList = document.getElementById('leaderboardList');
                if (leaderboardList) {
                    leaderboardList.innerHTML = '';
                }

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
                    if (leaderboardList) {
                        sortedPlayers.forEach(([username, score]) => {
                            const listItem = document.createElement('li');
                            listItem.textContent = `Player: ${username}, Solutions: ${score}`;
                            leaderboardList.appendChild(listItem);
                        });
                    }

                    const uniqueCount = new Set(data.submitted_solutions.map(s => s.solution)).size;
                    if (this.solutionCounter) {
                        this.solutionCounter.textContent = uniqueCount;
                    }
                    if (this.progressFill) {
                        this.progressFill.style.width = `${(uniqueCount / 92) * 100}%`;
                    }
                    const progressBar = document.getElementById('progressBar');
                    if (progressBar) {
                        progressBar.setAttribute('data-complete', uniqueCount === 92 ? 'true' : 'false');
                    }
                } else {
                    if (leaderboardList) {
                        leaderboardList.innerHTML = '<li>No solutions submitted yet.</li>';
                    }
                    if (this.solutionCounter) {
                        this.solutionCounter.textContent = '0';
                    }
                    if (this.progressFill) {
                        this.progressFill.style.width = '0%';
                    }
                    const progressBar = document.getElementById('progressBar');
                    if (progressBar) {
                        progressBar.setAttribute('data-complete', 'false');
                    }
                }
            } catch (error) {
                console.error('Error fetching solutions:', error);
                this.showMessage('Failed to load leaderboard.', 'error');
            }
        }

        async fetchPerformanceMetrics() {
            try {
                const response = await fetch('http://localhost:5000/api/eight_queens/get_performance');
                const data = await response.json();

                console.debug('Performance metrics:', data);

                const metricsDiv = document.getElementById('performanceMetrics');
                if (!metricsDiv) return;

                metricsDiv.innerHTML = '<h2>Performance Metrics</h2>';

                if (data.success && data.performance_metrics && data.performance_metrics.length > 0) {
                    data.performance_metrics.slice(0, 10).forEach(metric => {
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
                    metricsDiv.innerHTML += '<p>No performance metrics available.</p>';
                }
            } catch (error) {
                console.error('Error fetching performance metrics:', error);
                const metricsDiv = document.getElementById('performanceMetrics');
                if (metricsDiv) {
                    metricsDiv.innerHTML = '<h2>Performance Metrics</h2><p class="error">Error loading performance metrics.</p>';
                }
                this.showMessage('Failed to load performance metrics.', 'error');
            }
        }

        async viewDatabase() {
            try {
                const response = await fetch('http://localhost:5000/api/eight_queens/get_database');
                const data = await response.json();
                console.log('Database data:', data);

                const dbContentsDiv = document.getElementById('databaseContents');
                if (!dbContentsDiv) return;

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
                    this.showMessage('Failed to load database contents.', 'error');
                }
            } catch (error) {
                console.error('Error fetching database data:', error);
                const dbContentsDiv = document.getElementById('databaseContents');
                if (dbContentsDiv) {
                    dbContentsDiv.innerHTML = '<p class="error">An error occurred while fetching database data.</p>';
                }
                this.showMessage('Failed to load database contents.', 'error');
            }
        }
    }

    if (document.getElementById('board')) {
        const game = new QueensGame();
    } else {
        console.log('Not on eight_queens.html, skipping QueensGame initialization.');
    }
});