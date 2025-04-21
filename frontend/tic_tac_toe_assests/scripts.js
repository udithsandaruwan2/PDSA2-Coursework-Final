const sessionId = Date.now().toString(); // Unique session ID
let currentBoard = [];

// Start the game when the Start Game button is clicked
async function startGame() {
    const algorithm = document.getElementById("algorithm").value;
    const playerName = document.getElementById("playerName").value;  // Get player name from the input field

    // Check if both algorithm and player name are selected
    if (!algorithm) {
        alert("Please select an algorithm!");
        return;
    }

    if (!playerName) {
        alert("Please enter your name!");
        return;
    }

    // Send the algorithm choice and player name along with the session ID to the server
    const response = await fetch("/tic_tac_toe/start", {
        method: "POST",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            session_id: sessionId,
            player_name: playerName,  // Send the player name
            algorithm: algorithm
        })
    });

    const data = await response.json();
    console.log(data);  // Optionally log the response

    // Initialize and draw the board
    drawBoard(Array(5).fill().map(() => Array(5).fill(0)));

    // Show reset button and hide start button
    document.getElementById("startButton").style.display = "none";
    document.getElementById("resetButton").style.display = "inline";
}

// Function to draw the board on the screen
function drawBoard(board) {
    const table = document.getElementById("board");
    table.innerHTML = "";  // Clear previous board
    currentBoard = board;

    // Create the board cells
    for (let i = 0; i < 5; i++) {
        const row = document.createElement("tr");
        for (let j = 0; j < 5; j++) {
            const cell = document.createElement("td");
            cell.textContent = board[i][j] === 1 ? "O" : (board[i][j] === -1 ? "X" : "");
            cell.onclick = () => handleClick(i, j);  // Attach click event handler for moves
            row.appendChild(cell);
        }
        table.appendChild(row);
    }
}

// Handle player move and pass the selected algorithm for AI
async function handleClick(i, j) {
    // If the cell is already filled, ignore the click
    if (currentBoard[i][j] !== 0) return;

    const algorithm = document.getElementById("algorithm").value;
    const startTime = Date.now();  // Track start time for move duration

    const response = await fetch("/tic_tac_toe/move", {
        method: "POST",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            session_id: sessionId,
            move: [i, j],
            algorithm: algorithm
        })
    });

    const data = await response.json();

    if (data.error) {
        alert(data.error);
        return;
    }

    const endTime = Date.now();  // Optional: Track duration for your reference
    drawBoard(data.board);

    // Show result if game is over
    if (data.winner) {
        showModal(`Game Over! Winner: ${data.winner}`);
    } else if (data.draw) {
        showModal("Game Over! It's a Draw!");
    }
}


// Function to show the modal with the message
function showModal(message) {
    const modal = document.getElementById("gameModal");
    const modalMessage = document.getElementById("modalMessage");
    modalMessage.textContent = message;  // Set the message inside the modal
    modal.style.display = "flex";  // Show the modal

    // Hide the modal after 5 seconds
    setTimeout(() => {
        modal.style.display = "none";  // Hide the modal
    }, 5000);
}

// Reset the game state
async function resetGame() {
    // Send a request to reset the game session
    const response = await fetch("/tic_tac_toe/reset", {
        method: "POST",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId })
    });

    const data = await response.json();
    console.log(data);  // Optionally log the response

    // Reset the game board and hide the reset button
    drawBoard(Array(5).fill().map(() => Array(5).fill(0)));

    // Show start button and hide reset button
    document.getElementById("startButton").style.display = "inline";
    document.getElementById("resetButton").style.display = "none";
}
