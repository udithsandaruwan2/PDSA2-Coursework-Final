// frontend/script.js
const board = document.getElementById("board");
const statusDiv = document.getElementById("status");

let knightPos = null;
let visited = [];
let moveCount = 0;

// Build 8x8 board
function drawBoard() {
  board.innerHTML = "";
  for (let i = 0; i < 8; i++) {
    for (let j = 0; j < 8; j++) {
      const square = document.createElement("div");
      square.className = `square ${ (i + j) % 2 === 0 ? "white" : "black" }`;
      square.dataset.row = i;
      square.dataset.col = j;
      square.onclick = () => handleMove(i, j, square);
      board.appendChild(square);
    }
  }
}

// Randomly start knight
function startGame() {
  drawBoard();
  visited = [];
  moveCount = 1;
  const row = Math.floor(Math.random() * 8);
  const col = Math.floor(Math.random() * 8);
  knightPos = [row, col];
  markVisited(row, col);
  statusDiv.innerText = `Knight starts at (${row}, ${col})`;
  document.getElementById("winForm").style.display = "none";
}

function markVisited(row, col) {
  visited.push(`${row},${col}`);
  const square = document.querySelector(`[data-row="${row}"][data-col="${col}"]`);
  if (square) {
    square.classList.add("visited");
    square.innerText = moveCount;
  }
}

function isValidKnightMove(fromRow, fromCol, toRow, toCol) {
  const dx = Math.abs(fromRow - toRow);
  const dy = Math.abs(fromCol - toCol);
  return (dx === 2 && dy === 1) || (dx === 1 && dy === 2);
}

function handleMove(row, col, square) {
  if (!knightPos) return;
  const [currentRow, currentCol] = knightPos;
  if (!isValidKnightMove(currentRow, currentCol, row, col)) {
    statusDiv.innerText = "❌ Invalid knight move!";
    return;
  }

  const key = `${row},${col}`;
  if (visited.includes(key)) {
    statusDiv.innerText = "⚠️ Already visited!";
    return;
  }

  knightPos = [row, col];
  moveCount++;
  markVisited(row, col);

  if (visited.length === 64) {
    statusDiv.innerText = "🎉 All squares visited! You win!";
    document.getElementById("winForm").style.display = "block";
  }
}

function submitWin() {
  const name = document.getElementById("playerName").value;
  if (!name) {
    alert("Please enter a name!");
    return;
  }

  fetch('/submit_win', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      name: name,
      moves: visited
    })
  }).then(res => {
    if (res.ok) {
      alert("Saved successfully!");
      document.getElementById("winForm").style.display = "none";
    } else {
      alert("Error saving data!");
    }
  });
}

document.getElementById("startBtn").addEventListener("click", startGame);
