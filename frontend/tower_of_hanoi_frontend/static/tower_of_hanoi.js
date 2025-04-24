document.addEventListener('DOMContentLoaded', function() {
    let gameMode = '3peg';
    let diskCount = 0;
    let minMoves = 0;
    let yourMoves = 0;
    let moveHistory = [];
    let solutions = {};
    let gameInProgress = false;
    let draggingDisk = null;
    let draggedTower = null;
    let gameTimer = null;
    let gameSeconds = 0;
    let gameStartTime = null;
    let algorithmChart = null;
    let roundsComparisonChart = null;

    const mode3PegBtn = document.getElementById('mode-3peg');
    const mode4PegBtn = document.getElementById('mode-4peg');
    const threePegTowers = document.getElementById('three-peg-towers');
    const fourPegTowers = document.getElementById('four-peg-towers');
    const diskCountEl = document.getElementById('disk-count');
    const minMovesEl = document.getElementById('min-moves');
    const yourMovesEl = document.getElementById('your-moves');
    const newGameBtn = document.getElementById('new-game');
    const showSolutionBtn = document.getElementById('show-solution');
    const submitSolutionBtn = document.getElementById('submit-solution');
    const toggleMoveHistoryBtn = document.getElementById('toggle-move-history');
    const seeAllScoresBtn = document.getElementById('see-all-scores');
    const viewDbTablesBtn = document.getElementById('view-db-tables');
    const manualSubmitBtn = document.getElementById('manual-submit');
    const manualSubmitModal = document.getElementById('manual-submit-modal');
    const manualMoveForm = document.getElementById('manual-move-form');
    const cancelManualSubmitBtn = document.getElementById('cancel-manual-submit');
    const solutionModal = document.getElementById('solution-modal');
    const successModal = document.getElementById('success-modal');
    const allScoresModal = document.getElementById('all-scores-modal');
    const closeButtons = document.querySelectorAll('.close');
    const playAgainBtn = document.getElementById('play-again');
    const playerInputPanel = document.getElementById('player-input');
    const playerNameInput = document.getElementById('player-name');
    const saveScoreBtn = document.getElementById('save-score');
    const cancelSaveBtn = document.getElementById('cancel-save');
    const tabs = document.querySelectorAll('.tab');
    const tabContents = document.querySelectorAll('.tab-content');
    const solutionTabs = document.querySelectorAll('.solution-tab');
    const solutionPanels = document.querySelectorAll('.solution-panel');
    const minutesDisplay = document.getElementById('minutes');
    const secondsDisplay = document.getElementById('seconds');
    const moveHistoryList = document.getElementById('move-history-list');
    const moveHistoryPanel = document.getElementById('move-history');
    const diskSelector = document.getElementById('disk-selector');

    const diskColors = [
        '#e74c3c', '#3498db', '#2ecc71', '#f39c12',
        '#9b59b6', '#1abc9c', '#d35400', '#34495e',
        '#c0392b', '#2980b9'
    ];

    function initEventListeners() {
        mode3PegBtn.addEventListener('click', () => switchMode('3peg'));
        mode4PegBtn.addEventListener('click', () => switchMode('4peg'));
        newGameBtn.addEventListener('click', startNewGame);
        showSolutionBtn.addEventListener('click', showSolution);
        submitSolutionBtn.addEventListener('click', handleSubmitSolution);
        toggleMoveHistoryBtn.addEventListener('click', toggleMoveHistory);
        seeAllScoresBtn.addEventListener('click', showAllScores);
        viewDbTablesBtn.addEventListener('click', viewDatabaseTables);
        manualSubmitBtn.addEventListener('click', () => showModal(manualSubmitModal));
        cancelManualSubmitBtn.addEventListener('click', () => hideModal(manualSubmitModal));
        manualMoveForm.addEventListener('submit', handleManualSubmit);
        playAgainBtn.addEventListener('click', () => {
            hideModal(successModal);
            startNewGame();
        });
        saveScoreBtn.addEventListener('click', saveScore);
        cancelSaveBtn.addEventListener('click', () => {
            playerInputPanel.classList.add('hidden');
        });
        closeButtons.forEach(btn => {
            btn.addEventListener('click', function() {
                hideModal(this.closest('.modal'));
            });
        });
        tabs.forEach(tab => {
            tab.addEventListener('click', function() {
                switchTab(this.getAttribute('data-tab'));
            });
        });
        solutionTabs.forEach(tab => {
            tab.addEventListener('click', function() {
                switchSolutionTab(this.getAttribute('data-solution'));
            });
        });
        diskSelector.addEventListener('change', function() {
            if (gameInProgress && confirm('Changing disk count will reset the game. Continue?')) {
                startNewGame();
            }
        });
    }

    function toggleMoveHistory() {
        moveHistoryPanel.classList.toggle('hidden');
    }

    function switchMode(mode) {
        if (gameInProgress && gameMode !== mode && !confirm('Changing modes will reset the game. Continue?')) {
            return;
        }
        gameMode = mode;
        mode3PegBtn.classList.toggle('active', mode === '3peg');
        mode4PegBtn.classList.toggle('active', mode === '4peg');
        threePegTowers.classList.toggle('hidden', mode !== '3peg');
        fourPegTowers.classList.toggle('hidden', mode === '3peg');
        if (gameInProgress) {
            startNewGame();
        }
    }

    async function startNewGame() {
        try {
            playerInputPanel.classList.add('hidden');
            const selectedDisks = diskSelector.value;
            diskCount = selectedDisks === 'random' ? Math.floor(Math.random() * 6) + 5 : parseInt(selectedDisks);
            
            // For local testing without API
            const mockResponse = {
                disk_count: diskCount,
                min_moves: (2 ** diskCount) - 1,
                solutions: {
                    recursive: { moves: [], time: 0.001 },
                    iterative: { moves: [], time: 0.002 },
                    frame_stewart: { moves: [], time: 0.003 }
                }
            };
            
            let data;
            try {
                const response = await fetch(`/api/toh/new-game?disks=${diskCount}&mode=${gameMode}`);
                if (!response.ok) {
                    console.warn("API not available, using mock data");
                    data = mockResponse;
                } else {
                    data = await response.json();
                }
            } catch (error) {
                console.warn("API fetch failed, using mock data:", error);
                data = mockResponse;
            }

            diskCount = data.disk_count;
            solutions = data.solutions || {};
            
            if (gameMode === '4peg' && solutions.frame_stewart && solutions.frame_stewart.moves) {
                minMoves = solutions.frame_stewart.moves.length;
            } else {
                minMoves = data.min_moves;
            }
            
            yourMoves = 0;
            moveHistory = [];
            gameInProgress = true;

            moveHistoryList.innerHTML = '';
            moveHistoryPanel.classList.add('hidden');
            diskCountEl.textContent = diskCount;
            minMovesEl.textContent = minMoves;
            yourMovesEl.textContent = yourMoves;

            // Clear the manual submission form
            document.getElementById('move-count').value = '';
            document.getElementById('move-sequence').value = '';

            clearTowers();
            setupTowers();
            setupDragAndDrop();
            updateSolutionModal();
            startGameTimer();
        } catch (error) {
            console.error('Error starting new game:', error);
            alert(`Failed to start new game: ${error.message}. Please try again.`);
        }
    }

    function clearTowers() {
        const towers = gameMode === '3peg' ? 
            document.querySelectorAll('#three-peg-towers .tower') : 
            document.querySelectorAll('#four-peg-towers .tower');
        towers.forEach(tower => {
            const disks = tower.querySelectorAll('.disk');
            disks.forEach(disk => disk.remove());
        });
    }

    function setupTowers() {
        const sourceTower = gameMode === '3peg' ? 
            document.getElementById('tower-A') : 
            document.getElementById('tower-A-4');
        
        if (!sourceTower) {
            console.error('Source tower not found!');
            return;
        }

        const baseElement = sourceTower.querySelector('.base');
        if (!baseElement) {
            console.error('Base element not found in source tower');
            return;
        }

        const pegElement = sourceTower.querySelector('.peg');
        if (!pegElement) {
            console.error('Peg element not found in source tower');
            return;
        }

        for (let i = diskCount; i > 0; i--) {
            const disk = document.createElement('div');
            disk.className = 'disk';
            disk.dataset.size = i;
            const maxWidth = baseElement.offsetWidth * 0.9;
            const minWidth = maxWidth * 0.3;
            const width = minWidth + ((maxWidth - minWidth) * (i / diskCount));
            disk.style.width = `${width}px`;
            disk.style.backgroundColor = diskColors[(i - 1) % diskColors.length];
            disk.textContent = i;
            
            sourceTower.insertBefore(disk, pegElement.nextSibling);
        }
    }

    function setupDragAndDrop() {
        const towers = gameMode === '3peg' ? 
            document.querySelectorAll('#three-peg-towers .tower') : 
            document.querySelectorAll('#four-peg-towers .tower');
        
        towers.forEach(tower => {
            const newTower = tower.cloneNode(true);
            tower.parentNode.replaceChild(newTower, tower);
        });
        
        const updatedTowers = gameMode === '3peg' ? 
            document.querySelectorAll('#three-peg-towers .tower') : 
            document.querySelectorAll('#four-peg-towers .tower');
        
        const disks = document.querySelectorAll('.disk');
        
        updatedTowers.forEach(tower => {
            tower.addEventListener('dragover', (e) => {
                e.preventDefault();
                e.dataTransfer.dropEffect = 'move';
            });

            tower.addEventListener('drop', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                if (!draggingDisk || this === draggedTower) return;
                
                const targetTower = this;
                const diskSize = parseInt(draggingDisk.dataset.size);
                const topDiskOnTarget = getTopDisk(targetTower);
                
                if (topDiskOnTarget && parseInt(topDiskOnTarget.dataset.size) < diskSize) {
                    alert('Cannot place a larger disk on a smaller one.');
                    return;
                }
                
                const sourceId = draggedTower.id.match(/[A-D]/)[0];
                const targetId = targetTower.id.match(/[A-D]/)[0];
                
                targetTower.insertBefore(draggingDisk, targetTower.querySelector('.peg').nextSibling);
                draggingDisk.classList.add('animate-move');
                setTimeout(() => draggingDisk.classList.remove('animate-move'), 500);
                
                yourMoves++;
                yourMovesEl.textContent = yourMoves;
                moveHistory.push([diskSize, sourceId, targetId]);
                
                const moveItem = document.createElement('div');
                moveItem.className = 'move-item';
                moveItem.textContent = `${yourMoves}. Move disk ${diskSize} from ${sourceId} to ${targetId}`;
                moveHistoryList.appendChild(moveItem);
                moveHistoryPanel.classList.remove('hidden');
                moveHistoryList.scrollTop = moveHistoryList.scrollHeight;
                
                checkWinCondition();
            });
        });
        
        disks.forEach(disk => {
            disk.setAttribute('draggable', true);
            
            disk.addEventListener('dragstart', function(e) {
                const tower = this.parentElement;
                const topDisk = getTopDisk(tower);
                
                if (this !== topDisk) {
                    e.preventDefault();
                    return;
                }
                
                draggingDisk = this;
                draggedTower = tower;
                this.classList.add('dragging');
                e.dataTransfer.setData('text/plain', this.dataset.size);
                e.dataTransfer.effectAllowed = 'move';
            });
            
            disk.addEventListener('dragend', function() {
                this.classList.remove('dragging');
                draggingDisk = null;
                draggedTower = null;
            });

            disk.style.zIndex = 10 - parseInt(disk.dataset.size);
        });
    }

    function getTopDisk(tower) {
        const disks = Array.from(tower.querySelectorAll('.disk'));
        return disks.length > 0 ? disks[0] : null;
    }

    function checkWinCondition() {
        const destinationTower = gameMode === '3peg' ? 
            document.getElementById('tower-C') : 
            document.getElementById('tower-D-4');
        const disks = Array.from(destinationTower.querySelectorAll('.disk'));

        if (disks.length === diskCount) {
            const isSorted = disks.every((disk, index, array) => {
                return index === 0 || parseInt(array[index-1].dataset.size) < parseInt(disk.dataset.size);
            });
            
            if (!isSorted) return;

            gameInProgress = false;
            stopGameTimer();

            const penalty_factor = Math.min(100, 100 * (yourMoves - minMoves) / minMoves);
            const totalScore = Math.max(0, Math.floor(1000 - (penalty_factor * 10)));
            document.getElementById('success-message').innerHTML = `
                <p>Congratulations! You solved it in ${yourMoves} moves (Minimum: ${minMoves}).</p>
                <p>Time: ${Math.floor(gameSeconds / 60)}:${(gameSeconds % 60).toString().padStart(2, '0')}</p>
                <p>Score: ${totalScore} points</p>
            `;

            showModal(successModal);
            playerInputPanel.classList.remove('hidden');
            handleSubmitSolution(totalScore);
        }
    }

    function showSolution() {
        if (!gameInProgress) {
            alert('Please start a new game to view solutions.');
            return;
        }
        updateSolutionModal();
        showModal(solutionModal);
    }

    function updateSolutionModal() {
        const solutionsData = [
            { id: 'recursive', name: 'Recursive (3-peg)', moves: solutions.recursive?.moves || [], time: solutions.recursive?.time || 0 },
            { id: 'iterative', name: 'Iterative (3-peg)', moves: solutions.iterative?.moves || [], time: solutions.iterative?.time || 0 },
            { id: 'frame_stewart', name: 'Frame-Stewart (4-peg)', moves: solutions.frame_stewart?.moves || [], time: solutions.frame_stewart?.time || 0 }
        ];

        solutionsData.forEach(({ id, name, moves, time }) => {
            const panel = document.getElementById(`${id}-solution`);
            const timeEl = document.getElementById(`${id}-time`);
            const movesEl = document.getElementById(`${id}-moves`);

            if (!panel || !timeEl || !movesEl) {
                console.error(`Solution panel elements missing for ${id}`);
                return;
            }

            console.log(`Raw time for ${id}: ${time} ms`);

            timeEl.textContent = time.toFixed(6) + ' ms';

            movesEl.innerHTML = '';

            if (moves.length === 0) {
                const errorItem = document.createElement('div');
                errorItem.className = 'move-item';
                errorItem.textContent = `No moves available for ${name}.`;
                movesEl.appendChild(errorItem);
            } else {
                moves.forEach((move, index) => {
                    const [disk, source, dest] = move;
                    const moveItem = document.createElement('div');
                    moveItem.className = 'move-item';
                    moveItem.textContent = `${index + 1}. Move disk ${disk} from ${source} to ${dest}`;
                    movesEl.appendChild(moveItem);
                });
            }
        });
    }

    async function showAllScores() {
        try {
            const response = await fetch('/api/toh/all-scores');
            const scores = await response.json();

            const scoresBody = document.getElementById('all-scores-body');
            scoresBody.innerHTML = '';
            scores.forEach(score => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${score.player_name}</td>
                    <td>${score.disk_count}</td>
                    <td>${score.moves_count}</td>
                    <td>${score.mode}</td>
                    <td>${score.score_amount}</td>
                    <td>${score.timestamp}</td>
                `;
                scoresBody.appendChild(row);
            });

            showModal(allScoresModal);
        } catch (error) {
            console.error('Error loading all scores:', error);
            alert('Failed to load scores. Please try again.');
        }
    }

    function viewDatabaseTables() {
        window.open('/api/toh/db-tables', '_blank');
    }

    async function handleSubmitSolution(totalScore = 0) {
        if (!gameInProgress && moveHistory.length === 0) {
            alert('No moves to submit. Please start a new game.');
            return;
        }

        try {
            const moves = moveHistory;
            if (moves.length === 0) {
                alert('No moves recorded.');
                return;
            }

            const invalidMove = moves.find(move => 
                !Array.isArray(move) || 
                move.length !== 3 || 
                typeof move[0] !== 'number' || 
                !['A', 'B', 'C', 'D'].includes(move[1]) || 
                !['A', 'B', 'C', 'D'].includes(move[2])
            );
            if (invalidMove) {
                alert('Invalid move format in history.');
                return;
            }

            const response = await fetch('/api/toh/validate-solution', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    playerName: 'Anonymous',
                    diskCount, 
                    moves,
                    mode: gameMode
                })
            });
            const data = await response.json();

            if (data.success) {
                yourMoves = moves.length;
                yourMovesEl.textContent = yourMoves;
                moveHistoryList.innerHTML = '';
                moves.forEach((move, i) => {
                    const [disk, source, dest] = move;
                    const moveItem = document.createElement('div');
                    moveItem.className = 'move-item';
                    moveItem.textContent = `${i + 1}. Move disk ${disk} from ${source} to ${dest}`;
                    moveHistoryList.appendChild(moveItem);
                });

                const isOptimal = yourMoves === minMoves;
                document.getElementById('success-message').innerHTML = `
                    <p>Congratulations! You solved it in ${yourMoves} moves (Minimum: ${minMoves}).</p>
                    <p>${isOptimal ? 'Optimal solution!' : 'Try to match the minimum moves!'}</p>
                    <p>Time: ${Math.floor(gameSeconds / 60)}:${(gameSeconds % 60).toString().padStart(2, '0')}</p>
                    <p>Score: ${totalScore} points</p>
                `;
            } else {
                alert(data.message);
            }
        } catch (error) {
            console.error('Error validating solution:', error);
            alert('Failed to validate solution. Please try again.');
        }
    }

    async function saveScore() {
        const playerName = playerNameInput.value.trim() || 'Anonymous';
        try {
            const movesJson = JSON.stringify(moveHistory);
            const totalScore = Math.floor((minMoves / yourMoves) * 1000);
            const response = await fetch('/api/toh/validate-solution', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    playerName, 
                    diskCount, 
                    moves: moveHistory,
                    mode: gameMode
                })
            });
            const data = await response.json();

            if (data.success) {
                await fetch('/api/toh/save-game-result', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        playerName,
                        diskCount,
                        movesCount: moveHistory.length,
                        movesJson,
                        mode: gameMode,
                        scoreAmount: totalScore
                    })
                });
                playerInputPanel.classList.add('hidden');
                loadScores();
                switchTab('scores');
            } else {
                alert("Failed to validate your solution. Please try again.");
            }
        } catch (error) {
            console.error('Error saving score:', error);
            alert('Failed to save score. Please try again.');
        }
    }

    async function handleManualSubmit(e) {
        e.preventDefault();
        const moveCount = parseInt(document.getElementById('move-count').value);
        const sequenceText = document.getElementById('move-sequence').value.trim();
        const moves = [];
        const lines = sequenceText.split('\n').map(line => line.trim()).filter(line => line);
        
        if (lines.length !== moveCount) {
            alert(`Number of moves (${moveCount}) does not match sequence count (${lines.length}).`);
            return;
        }
        
        for (const line of lines) {
            const parts = line.split(/\s+/);
            if (parts.length !== 3) {
                alert(`Invalid move format: "${line}". Use: disk source dest (e.g., 1 A B)`);
                return;
            }
            const disk = parseInt(parts[0]);
            const source = parts[1].toUpperCase();
            const dest = parts[2].toUpperCase();
            if (isNaN(disk) || disk < 1 || disk > diskCount ||
                !['A', 'B', 'C', 'D'].includes(source) || !['A', 'B', 'C', 'D'].includes(dest)) {
                alert(`Invalid move: "${line}". Disk must be 1-${diskCount}, pegs must be A-D.`);
                return;
            }
            if (gameMode === '3peg' && (source === 'D' || dest === 'D')) {
                alert(`Invalid move: "${line}". Peg D is not allowed in 3-peg mode.`);
                return;
            }
            moves.push([disk, source, dest]);
        }
        
        try {
            const response = await fetch('/api/toh/validate-solution', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    playerName: playerNameInput.value.trim() || 'Anonymous',
                    diskCount,
                    moves,
                    mode: gameMode
                })
            });
            const data = await response.json();
            hideModal(manualSubmitModal);
            if (data.success) {
                yourMoves = moves.length;
                yourMovesEl.textContent = yourMoves;
                moveHistory = moves;
                moveHistoryList.innerHTML = '';
                moves.forEach((move, i) => {
                    const [disk, source, dest] = move;
                    const moveItem = document.createElement('div');
                    moveItem.className = 'move-item';
                    moveItem.textContent = `${i + 1}. Move disk ${disk} from ${source} to ${dest}`;
                    moveHistoryList.appendChild(moveItem);
                });
                moveHistoryPanel.classList.remove('hidden');
                const penalty_factor = Math.min(100, 100 * (yourMoves - minMoves) / minMoves);
                const totalScore = Math.max(0, Math.floor(1000 - (penalty_factor * 10)));
                document.getElementById('success-message').innerHTML = `
                    <p>Congratulations! You solved it in ${yourMoves} moves (Minimum: ${minMoves}).</p>
                    <p>${data.optimal ? 'Optimal solution!' : 'Try to match the minimum moves!'}</p>
                    <p>Time: ${Math.floor(gameSeconds / 60)}:${(gameSeconds % 60).toString().padStart(2, '0')}</p>
                    <p>Score: ${totalScore} points</p>
                `;
                showModal(successModal);
                playerInputPanel.classList.remove('hidden');
                gameInProgress = false;
                stopGameTimer();
            } else {
                alert(data.message);
            }
        } catch (error) {
            console.error('Error submitting manual moves:', error);
            alert('Failed to submit moves. Please try again.');
        }
    }

    async function loadScores() {
        try {
            const response = await fetch('/api/toh/scores');
            const scores = await response.json();
            
            const scoresBody = document.getElementById('scores-body');
            scoresBody.innerHTML = '';
            scores.forEach(score => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${score.player_name}</td>
                    <td>${score.disk_count}</td>
                    <td>${score.moves_count}</td>
                `;
                scoresBody.appendChild(row);
            });
        } catch (error) {
            console.error('Error loading scores:', error);
        }
    }

    async function loadAlgorithmComparison() {
        try {
            const response = await fetch('/api/toh/algorithm-comparison');
            const data = await response.json();
            
            console.log('Algorithm comparison data:', data);

            const algorithmBody = document.getElementById('algorithm-body');
            algorithmBody.innerHTML = '';
            data.forEach(item => {
                const row = document.createElement('tr');
                const algorithmName = {
                    'recursive': 'Recursive',
                    'iterative': 'Iterative',
                    'frame_stewart': 'Frame-Stewart'
                }[item.algorithm_type] || 'Unknown';
                row.innerHTML = `
                    <td>${item.disk_count}</td>
                    <td>${algorithmName}</td>
                    <td>${item.peg_count}</td>
                    <td>${item.avg_time.toFixed(6)} ms</td>
                `;
                algorithmBody.appendChild(row);
            });

            const chartData = await fetch('/api/toh/algorithm-comparison-chart').then(res => res.json());
            console.log('Algorithm chart data:', chartData);
            renderAlgorithmChart(chartData);
        } catch (error) {
            console.error('Error loading algorithm comparison:', error);
        }
    }

    async function loadRoundsComparison() {
        try {
            const response = await fetch('/api/toh/rounds-comparison');
            const data = await response.json();
            
            console.log('Rounds comparison data:', data);

            const roundsBody = document.getElementById('rounds-comparison-body');
            roundsBody.innerHTML = '';
            data.forEach(item => {
                const row = document.createElement('tr');
                const algorithmName = {
                    'recursive': 'Recursive',
                    'iterative': 'Iterative',
                    'frame_stewart': 'Frame-Stewart'
                }[item.algorithm_type] || 'Unknown';
                const mode = item.peg_count === 4 ? '4peg' : '3peg';
                row.innerHTML = `
                    <td>${item.disk_count}</td>
                    <td>${item.min_moves}</td>
                    <td>${item.avg_time.toFixed(6)} ms</td>
                    <td>${mode}</td>
                    <td>${algorithmName}</td>
                `;
                roundsBody.appendChild(row);
            });

            const chartData = await fetch('/api/toh/rounds-comparison-chart').then(res => res.json());
            console.log('Rounds comparison chart data:', chartData);
            renderRoundsComparisonChart(chartData);
        } catch (error) {
            console.error('Error loading rounds comparison:', error);
        }
    }

    function renderAlgorithmChart(chartData) {
        const ctx = document.getElementById('algorithm-chart').getContext('2d');
        if (algorithmChart) {
            algorithmChart.destroy();
        }
        algorithmChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: chartData.labels,
                datasets: chartData.datasets.map(dataset => ({
                    ...dataset,
                    borderColor: dataset.backgroundColor,
                    fill: false,
                    tension: 0.1
                }))
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'top' },
                    title: { display: true, text: 'Algorithm Performance (ms)' }
                },
                scales: {
                    x: { title: { display: true, text: 'Number of Disks' } },
                    y: { 
                        title: { display: true, text: 'Execution Time (ms)' },
                        beginAtZero: true
                    }
                }
            }
        });
    }

    function renderRoundsComparisonChart(chartData) {
        const ctx = document.getElementById('rounds-comparison-chart').getContext('2d');
        if (roundsComparisonChart) {
            roundsComparisonChart.destroy();
        }
        roundsComparisonChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: chartData.labels,
                datasets: chartData.datasets.map(dataset => ({
                    ...dataset,
                    borderColor: dataset.backgroundColor,
                    fill: false,
                    tension: 0.1
                }))
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'top' },
                    title: { display: true, text: '10 Rounds Algorithm Performance (ms)' }
                },
                scales: {
                    x: { title: { display: true, text: 'Round' } },
                    y: { 
                        title: { display: true, text: 'Execution Time (ms)' },
                        beginAtZero: true
                    }
                }
            }
        });
    }

    function switchTab(tabId) {
        tabs.forEach(tab => tab.classList.toggle('active', tab.getAttribute('data-tab') === tabId));
        tabContents.forEach(content => content.classList.toggle('active', content.id === `${tabId}-content`));
        if (tabId === 'scores') loadScores();
        else if (tabId === 'algorithms') loadAlgorithmComparison();
        else if (tabId === 'rounds-comparison') loadRoundsComparison();
    }

    function switchSolutionTab(solutionId) {
        solutionTabs.forEach(tab => tab.classList.toggle('active', tab.getAttribute('data-solution') === solutionId));
        solutionPanels.forEach(panel => panel.classList.toggle('active', panel.id === `${solutionId}-solution`));
    }

    function showModal(modal) {
        modal.classList.remove('hidden');
        modal.classList.add('show');
    }

    function hideModal(modal) {
        modal.classList.remove('show');
        modal.classList.add('hidden');
    }

    function startGameTimer() {
        gameSeconds = 0;
        updateTimerDisplay();
        if (gameTimer) clearInterval(gameTimer);
        gameStartTime = Date.now();
        gameTimer = setInterval(() => {
            gameSeconds = Math.floor((Date.now() - gameStartTime) / 1000);
            updateTimerDisplay();
        }, 1000);
    }

    function updateTimerDisplay() {
        const minutes = Math.floor(gameSeconds / 60);
        const seconds = gameSeconds % 60;
        minutesDisplay.textContent = minutes.toString().padStart(2, '0');
        secondsDisplay.textContent = seconds.toString().padStart(2, '0');
    }

    function stopGameTimer() {
        if (gameTimer) {
            clearInterval(gameTimer);
            gameTimer = null;
        }
    }

    function initGame() {
        initEventListeners();
        switchTab('instructions');
        startNewGame();
    }

    initGame();
});