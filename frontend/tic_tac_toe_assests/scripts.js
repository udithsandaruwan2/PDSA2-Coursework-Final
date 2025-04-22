const sessionId = Date.now().toString(); // Unique session ID
let currentBoard = [];

// Start the game when the Start Game button is clicked
async function startGame() {
    const algorithm = document.getElementById("algorithm").value;
    const playerName = document.getElementById("playerName").value;
    localStorage.setItem("player_name", playerName);

    if (!algorithm) {
        alert("Please select an algorithm!");
        return;
    }

    if (!playerName) {
        alert("Please enter your name!");
        return;
    }

    const response = await fetch("/tic_tac_toe/start", {
        method: "POST",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            session_id: sessionId,
            player_name: playerName,
            algorithm: algorithm
        })
    });

    const data = await response.json();
    console.log(data);

    drawBoard(Array(5).fill().map(() => Array(5).fill(0)));

    document.getElementById("startButton").style.display = "none";
    document.getElementById("resetButton").style.display = "inline";
}

// Draw the game board
function drawBoard(board) {
    const table = document.getElementById("board");
    table.innerHTML = "";
    currentBoard = board;

    for (let i = 0; i < 5; i++) {
        const row = document.createElement("tr");
        for (let j = 0; j < 5; j++) {
            const cell = document.createElement("td");
            cell.textContent = board[i][j] === 1 ? "O" : (board[i][j] === -1 ? "X" : "");
            cell.onclick = () => handleClick(i, j);
            row.appendChild(cell);
        }
        table.appendChild(row);
    }
}

// Handle player move
function handleClick(i, j) {
    if (currentBoard[i][j] !== 0) return;

    currentBoard[i][j] = 1;
    drawBoard(currentBoard);

    sendMoveToBackend(i, j);
}

// Send move to backend and get computer response
async function sendMoveToBackend(i, j) {
    const algorithm = document.getElementById("algorithm").value;
    const statusMessage = document.getElementById("statusMessage");
    const playerName = localStorage.getItem("player_name");

    statusMessage.textContent = "Computer is thinking...";
    disableBoard();

    const response = await fetch("/tic_tac_toe/move", {
        method: "POST",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            session_id: sessionId,
            move: [i, j],
            playerName: playerName,
            algorithm: algorithm
        })
    });

    const data = await response.json();

    if (data.error) {
        alert(data.error);
        statusMessage.textContent = "";
        enableBoard();
        return;
    }

    drawBoard(data.board);
    statusMessage.textContent = "";

    if (data.winner) {
        showModal(`Game Over! Winner: ${data.winner}`);
    } else if (data.draw) {
        showModal("Game Over! It's a Draw!");
    }

    enableBoard();
}

// Show result modal
function showModal(message) {
    const modal = document.getElementById("gameModal");
    const modalMessage = document.getElementById("modalMessage");
    modalMessage.textContent = message;
    modal.style.display = "flex";

    setTimeout(() => {
        modal.style.display = "none";
    }, 5000);
}

// Reset the game
async function resetGame() {
    const response = await fetch("/tic_tac_toe/reset", {
        method: "POST",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId })
    });

    const data = await response.json();
    console.log(data);

    drawBoard(Array(5).fill().map(() => Array(5).fill(0)));
    document.getElementById("startButton").style.display = "inline";
    document.getElementById("resetButton").style.display = "none";
    document.getElementById("statusMessage").textContent = "";
}

// Disable board interaction
function disableBoard() {
    const cells = document.querySelectorAll("#board td");
    cells.forEach(cell => {
        cell.style.pointerEvents = "none";
        cell.style.opacity = "0.6";
    });
}

// Enable board interaction
function enableBoard() {
    const cells = document.querySelectorAll("#board td");
    cells.forEach(cell => {
        cell.style.pointerEvents = "auto";
        cell.style.opacity = "1";
    });
}
