const boardSize = 8;  // 8x8 Chessboard

function createBoard() {
    const board = document.getElementById("board");  // Get the board container from HTML
    board.innerHTML = "";  // Clear the board before generating it

    // Loop through rows and columns to create the chessboard cells
    for (let row = 0; row < boardSize; row++) {
        for (let col = 0; col < boardSize; col++) {
            const cell = document.createElement("div");  // Create a new div for each cell
            cell.classList.add("cell");  // Add the "cell" class to each cell

            // Set color based on position (alternating black and white)
            if ((row + col) % 2 === 0) {
                cell.classList.add("white");  // Even cells will be white
            } else {
                cell.classList.add("black");  // Odd cells will be black
            }

            // Add a unique ID for each cell (e.g., '0-0', '0-1', '1-0', etc.)
            cell.setAttribute('id', `${row}-${col}`);

            // Append the cell to the board container
            board.appendChild(cell);
        }
    }
}

// Call the function to create the board when the page loads
window.onload = createBoard;
