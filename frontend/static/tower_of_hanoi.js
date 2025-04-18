document.addEventListener('DOMContentLoaded', function() {
    // Game state variables
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
let selectedDiskCount = 8;
    
    // DOM Elements
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
    const solutionModal = document.getElementById('solution-modal');
    const successModal = document.getElementById('success-modal');
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
    const diskSelector = document.getElementById('disk-selector');
    const minutesDisplay = document.getElementById('minutes');
    const secondsDisplay = document.getElementById('seconds');
    const moveHistoryList = document.getElementById('move-history-list');
    const moveHistoryPanel = document.getElementById('move-history');
    
    // Color palette for disks
    const diskColors = [
        '#e74c3c', '#3498db', '#2ecc71', '#f39c12', 
        '#9b59b6', '#1abc9c', '#d35400', '#34495e',
        '#c0392b', '#2980b9', '#27ae60', '#f1c40f'
    ];
    
    // Initialize event listeners
    function initEventListeners() {
        // Mode buttons
        mode3PegBtn.addEventListener('click', () => switchMode('3peg'));
        mode4PegBtn.addEventListener('click', () => switchMode('4peg'));
        
// Game control buttons
newGameBtn.addEventListener('click', startNewGame);
showSolutionBtn.addEventListener('click', showSolution);
submitSolutionBtn.addEventListener('click', handleSubmitSolution);
playAgainBtn.addEventListener('click', () => {
    hideModal(successModal);
    startNewGame();
});

// Player input buttons
saveScoreBtn.addEventListener('click', saveScore);
cancelSaveBtn.addEventListener('click', () => {
    playerInputPanel.classList.add('hidden');
});

// Modal close buttons
closeButtons.forEach(btn => {
    btn.addEventListener('click', function() {
        const modal = this.closest('.modal');
        hideModal(modal);
    });
});

// Tabs
tabs.forEach(tab => {
    tab.addEventListener('click', function() {
        const tabId = this.getAttribute('data-tab');
        switchTab(tabId);
    });
});

// Solution tabs
solutionTabs.forEach(tab => {
    tab.addEventListener('click', function() {
        const solutionId = this.getAttribute('data-solution');
        switchSolutionTab(solutionId);
    });
});
// Add disk selector change event
diskSelector.addEventListener('change', function() {
    selectedDiskCount = parseInt(this.value);
    if (gameInProgress) {
        if (confirm('Changing disk count will reset your current game. Continue?')) {
            startNewGame();
        } else {
            // Reset the select to current disk count
            this.value = diskCount;
        }
    }
});

}

// Switch between 3-peg and 4-peg modes
function switchMode(mode) {
if (gameInProgress && gameMode !== mode) {
    if (!confirm('Changing modes will reset your current game. Continue?')) {
        return;
    }
}

gameMode = mode;

// Update UI
if (mode === '3peg') {
    mode3PegBtn.classList.add('active');
    mode4PegBtn.classList.remove('active');
    threePegTowers.classList.remove('hidden');
    fourPegTowers.classList.add('hidden');
} else {
    mode3PegBtn.classList.remove('active');
    mode4PegBtn.classList.add('active');
    threePegTowers.classList.add('hidden');
    fourPegTowers.classList.remove('hidden');
}

if (gameInProgress) {
    startNewGame();
}
}

// Start a new game with random disk count
function startNewGame() {
    // Get selected disk count
    diskCount = parseInt(diskSelector.value);
    
    fetch(`/api/toh/new-game?disks=${diskCount}`)
        .then(response => response.json())
        .then(data => {
            // Update game state
            diskCount = data.disk_count;
            minMoves = data.min_moves;
            yourMoves = 0;
            moveHistory = [];
            solutions = data.solutions;
            gameInProgress = true;
            
            // Clear move history display
            moveHistoryList.innerHTML = '';
            moveHistoryPanel.classList.add('hidden');
            
            // Update UI
            diskCountEl.textContent = diskCount;
            minMovesEl.textContent = minMoves;
            yourMovesEl.textContent = yourMoves;
            
            // Clear existing towers
            clearTowers();
            
            // Setup towers with disks
            setupTowers();
            
            // Setup drag and drop
            setupDragAndDrop();
            
            // Update solution modal
            updateSolutionModal();
            
            // Start timer
            startGameTimer();
        })
        .catch(error => console.error('Error starting new game:', error));
}

// Clear all towers
function clearTowers() {
const towers = gameMode === '3peg' ? 
    document.querySelectorAll('#three-peg-towers .tower') : 
    document.querySelectorAll('#four-peg-towers .tower');

towers.forEach(tower => {
    const disks = tower.querySelectorAll('.disk');
    disks.forEach(disk => disk.remove());
});
}

// Setup towers with disks
function setupTowers() {
    const sourceTower = gameMode === '3peg' ? 
        document.getElementById('tower-A') : 
        document.getElementById('tower-A-4');
    
    // Ensure all towers are visible first
    const towers = gameMode === '3peg' ? 
        document.querySelectorAll('#three-peg-towers .tower') : 
        document.querySelectorAll('#four-peg-towers .tower');
    
    towers.forEach(tower => {
        tower.style.display = 'flex'; // Make sure towers are visible
    });

    // Create disks in descending size (largest at bottom)
    for (let i = diskCount; i > 0; i--) {
        const disk = document.createElement('div');
        disk.className = 'disk';
        disk.dataset.size = i;
        
        // Calculate width based on disk size
        const maxWidth = sourceTower.querySelector('.base').offsetWidth * 0.9;
        const minWidth = maxWidth * 0.3;
        const width = minWidth + ((maxWidth - minWidth) * (i / diskCount));
        
        disk.style.width = `${width}px`;
        disk.style.backgroundColor = diskColors[(i - 1) % diskColors.length];
        
        // Add disk number for better visibility
        disk.textContent = i;
        
        // Add disk to source tower
        sourceTower.insertBefore(disk, sourceTower.querySelector('.peg').nextSibling);
    }
}

// Fix the initialization function to make sure the game starts properly
function initGame() {
    initEventListeners();
    switchTab('instructions');
    
    // Force a new game initialization after a short delay
    setTimeout(() => {
        startNewGame();
    }, 500);
}

// Setup drag and drop functionality
function setupDragAndDrop() {
const disks = document.querySelectorAll('.disk');
const towers = gameMode === '3peg' ? 
    document.querySelectorAll('#three-peg-towers .tower') : 
    document.querySelectorAll('#four-peg-towers .tower');

disks.forEach(disk => {
    disk.setAttribute('draggable', true);
    
    disk.addEventListener('dragstart', function(e) {
        // Check if this is the top disk
        const tower = this.parentElement;
        const topDisk = getTopDisk(tower);
        
        if (this !== topDisk) {
            e.preventDefault();
            return false;
        }
        
        draggingDisk = this;
        draggedTower = tower;
        
        setTimeout(() => {
            this.classList.add('dragging');
        }, 0);
        
        e.dataTransfer.setData('text/plain', this.dataset.size);
        e.dataTransfer.effectAllowed = 'move';
    });
    
    disk.addEventListener('dragend', function() {
        this.classList.remove('dragging');
        draggingDisk = null;
    });
});

towers.forEach(tower => {
    tower.addEventListener('dragover', function(e) {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
    });
    
    tower.addEventListener('drop', function(e) {
        e.preventDefault();
        
        if (!draggingDisk) return;
        
        const targetTower = this;
        const sourceTower = draggedTower;
        
        // Don't do anything if dropping on the same tower
        if (sourceTower === targetTower) return;
        
        const diskSize = parseInt(draggingDisk.dataset.size);
        const topDiskOnTarget = getTopDisk(targetTower);
        
        // Check if move is valid
        if (topDiskOnTarget && parseInt(topDiskOnTarget.dataset.size) < diskSize) {
            return; // Can't place a larger disk on a smaller one
        }
        
        // Get tower IDs for move history
        const sourceId = sourceTower.id.includes('-4') ? 
            sourceTower.id.charAt(sourceTower.id.length - 1) : 
            sourceTower.id.charAt(sourceTower.id.length - 1);
            
        const targetId = targetTower.id.includes('-4') ? 
            targetTower.id.charAt(targetTower.id.length - 1) : 
            targetTower.id.charAt(targetTower.id.length - 1);
        
        // Move the disk
        targetTower.insertBefore(draggingDisk, targetTower.querySelector('.peg').nextSibling);
        draggingDisk.classList.add('animate-move');
        
        // Update move count
        yourMoves++;
        yourMovesEl.textContent = yourMoves;
        
        // Record the move
        moveHistory.push([sourceId, targetId]);
        
        // Add to move history display
        const moveItem = document.createElement('div');
        moveItem.className = 'move-item';
        moveItem.textContent = `${yourMoves}. Move disk ${diskSize} from ${sourceId} to ${targetId}`;
        moveHistoryList.appendChild(moveItem);
        moveHistoryPanel.classList.remove('hidden');
        
        // Scroll to bottom of move history
        moveHistoryList.scrollTop = moveHistoryList.scrollHeight;
        
        // Check for win condition
        checkWinCondition();
    });
});
}

// Get the top disk from a tower
function getTopDisk(tower) {
const disks = tower.querySelectorAll('.disk');
return disks.length > 0 ? disks[0] : null;
}

// Check if the player has won
function checkWinCondition() {
    const destinationTower = gameMode === '3peg' ? 
        document.getElementById('tower-C') : 
        document.getElementById('tower-D-4');
        
    const disksOnDestination = destinationTower.querySelectorAll('.disk');

    if (disksOnDestination.length === diskCount) {
        gameInProgress = false;
        
        // Stop timer
        stopGameTimer();
        
        // Calculate score based on moves and time
        const optimalMoves = minMoves;
        const moveScore = Math.floor((optimalMoves / yourMoves) * 1000);
        const timeScore = Math.max(0, 5000 - (gameSeconds * 10));
        const totalScore = moveScore + timeScore;
        
        const successMessage = document.getElementById('success-message');
        successMessage.innerHTML = `
            <p>Congratulations! You solved the puzzle in ${yourMoves} moves. The minimum possible is ${minMoves} moves.</p>
            <p>Time: ${Math.floor(gameSeconds / 60)}:${(gameSeconds % 60).toString().padStart(2, '0')}</p>
            <p>Score: ${totalScore} points</p>
        `;
        
        // Add success animation to the destination tower
        destinationTower.classList.add('success-animation');
        
        showModal(successModal);
        playerInputPanel.classList.remove('hidden');
        
        // Remove animation after modal is closed
        const closeButtons = successModal.querySelectorAll('.close, #play-again');
        closeButtons.forEach(btn => {
            btn.addEventListener('click', function() {
                destinationTower.classList.remove('success-animation');
            }, { once: true });
        });
    }
}

// Show solution modal
function showSolution() {
if (!gameInProgress) return;

showModal(solutionModal);
}

// Update solution modal with current game data
function updateSolutionModal() {
// Update recursive solution
const recursiveTime = document.getElementById('recursive-time');
const recursiveMoves = document.getElementById('recursive-moves');
recursiveTime.textContent = (solutions.recursive.time * 1000).toFixed(4);
recursiveMoves.innerHTML = '';

solutions.recursive.moves.forEach((move, index) => {
    const moveItem = document.createElement('div');
    moveItem.className = 'move-item';
    moveItem.textContent = `${index + 1}. Move disk from ${move[0]} to ${move[1]}`;
    recursiveMoves.appendChild(moveItem);
});

// Update iterative solution
const iterativeTime = document.getElementById('iterative-time');
const iterativeMoves = document.getElementById('iterative-moves');
iterativeTime.textContent = (solutions.iterative.time * 1000).toFixed(4);
iterativeMoves.innerHTML = '';

solutions.iterative.moves.forEach((move, index) => {
    const moveItem = document.createElement('div');
    moveItem.className = 'move-item';
    moveItem.textContent = `${index + 1}. Move disk from ${move[0]} to ${move[1]}`;
    iterativeMoves.appendChild(moveItem);
});

// Update Frame-Stewart solution
const frameStewartTime = document.getElementById('frame-stewart-time');
const frameStewartMoves = document.getElementById('frame-stewart-moves');
frameStewartTime.textContent = (solutions.frame_stewart.time * 1000).toFixed(4);
frameStewartMoves.innerHTML = '';

solutions.frame_stewart.moves.forEach((move, index) => {
    const moveItem = document.createElement('div');
    moveItem.className = 'move-item';
    moveItem.textContent = `${index + 1}. Move disk from ${move[0]} to ${move[1]}`;
    frameStewartMoves.appendChild(moveItem);
});
}

// Handle submit solution button
function handleSubmitSolution() {
if (!gameInProgress || moveHistory.length === 0) return;

playerInputPanel.classList.remove('hidden');
}

// Save score to database
function saveScore() {
const playerName = playerNameInput.value.trim() || 'Anonymous';

fetch('/api/toh/validate-solution', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        playerName: playerName,
        diskCount: diskCount,
        moves: moveHistory
    })
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        playerInputPanel.classList.add('hidden');
        loadScores();
        switchTab('scores');
    } else {
        alert(data.message);
    }
})
.catch(error => console.error('Error saving score:', error));
}

// Load scores from database
function loadScores() {
fetch('/api/toh/scores')
    .then(response => response.json())
    .then(data => {
        const scoresBody = document.getElementById('scores-body');
        scoresBody.innerHTML = '';
        
        data.forEach(score => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${score.player_name}</td>
                <td>${score.disk_count}</td>
                <td>${score.moves_count}</td>
            `;
            scoresBody.appendChild(row);
        });
    })
    .catch(error => console.error('Error loading scores:', error));
}

// Load algorithm comparison data
function loadAlgorithmComparison() {
fetch('/api/toh/algorithm-comparison')
    .then(response => response.json())
    .then(data => {
        const algorithmBody = document.getElementById('algorithm-body');
        algorithmBody.innerHTML = '';
        
        data.forEach(item => {
            const row = document.createElement('tr');
            
            // Format algorithm name for display
            let algorithmName = 'Unknown';
            if (item.algorithm_type === 'recursive') algorithmName = 'Recursive';
            if (item.algorithm_type === 'iterative') algorithmName = 'Iterative';
            if (item.algorithm_type === 'frame_stewart') algorithmName = 'Frame-Stewart';
            
            row.innerHTML = `
                <td>${item.disk_count}</td>
                <td>${algorithmName}</td>
                <td>${item.peg_count}</td>
                <td>${(item.avg_time * 1000).toFixed(4)}</td>
            `;
            algorithmBody.appendChild(row);
        });
    })
    .catch(error => console.error('Error loading algorithm comparison:', error));
}

// Switch between tabs
function switchTab(tabId) {
// Update tab buttons
tabs.forEach(tab => {
    if (tab.getAttribute('data-tab') === tabId) {
        tab.classList.add('active');
    } else {
        tab.classList.remove('active');
    }
});

// Update tab content
tabContents.forEach(content => {
    if (content.id === `${tabId}-content`) {
        content.classList.add('active');
    } else {
        content.classList.remove('active');
    }
});

// Load data if needed
if (tabId === 'scores') {
    loadScores();
} else if (tabId === 'algorithms') {
    loadAlgorithmComparison();
}
}

// Switch between solution tabs
function switchSolutionTab(solutionId) {
// Update tab buttons
solutionTabs.forEach(tab => {
    if (tab.getAttribute('data-solution') === solutionId) {
        tab.classList.add('active');
    } else {
        tab.classList.remove('active');
    }
});

// Update tab content
solutionPanels.forEach(panel => {
    if (panel.id === `${solutionId}-solution`) {
        panel.classList.add('active');
    } else {
        panel.classList.remove('active');
    }
});
}

// Show modal
function showModal(modal) {
modal.classList.remove('hidden');
modal.classList.add('show');
}

// Hide modal
function hideModal(modal) {
modal.classList.remove('show');
modal.classList.add('hidden');
}
// New function to start the game timer
function startGameTimer() {
    // Reset timer
    gameSeconds = 0;
    updateTimerDisplay();
    
    // Clear any existing timer
    if (gameTimer) {
        clearInterval(gameTimer);
    }
    
    // Start new timer
    gameStartTime = Date.now();
    gameTimer = setInterval(() => {
        gameSeconds = Math.floor((Date.now() - gameStartTime) / 1000);
        updateTimerDisplay();
    }, 1000);
}

// Update the timer display
function updateTimerDisplay() {
    const minutes = Math.floor(gameSeconds / 60);
    const seconds = gameSeconds % 60;
    minutesDisplay.textContent = minutes.toString().padStart(2, '0');
    secondsDisplay.textContent = seconds.toString().padStart(2, '0');
}

// Stop the game timer
function stopGameTimer() {
    if (gameTimer) {
        clearInterval(gameTimer);
        gameTimer = null;
    }
}


// Initialize the game
function initGame() {
initEventListeners();
switchTab('instructions');
}

// Start the game
initGame();
});