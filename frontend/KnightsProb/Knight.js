let selectedPath = [];
let startPosition = null;

function startGame() {
  fetch('http://localhost:5000/api/start')
    .then(res => res.json())
    .then(data => {
      const pos = data.start;
      startPosition = [pos.x, pos.y];
      selectedPath = [startPosition];
      drawBoard(startPosition);
      document.getElementById('status').innerText = `Knight starts at (${pos.x}, ${pos.y})`;
    });
}

function drawBoard(currentPos) {
  const board = document.getElementById('board');
  board.innerHTML = '';

  fetch('http://localhost:5000/api/valid-moves', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      currentPos: currentPos,
      selectedPath: selectedPath
    })
  })
  .then(res => res.json())
  .then(data => {
    const validMoves = data.validMoves;

    for (let row = 0; row < 8; row++) {
      for (let col = 0; col < 8; col++) {
        const square = document.createElement('div');
        square.classList.add('square');
        square.classList.add((row + col) % 2 === 0 ? 'white' : 'black');
        square.dataset.row = row;
        square.dataset.col = col;

        if (row === currentPos[0] && col === currentPos[1]) {
          square.classList.add('start');
          square.innerText = '♞';
        } else if (selectedPath.some(p => p[0] === row && p[1] === col)) {
          square.classList.add('selected');
          square.innerText = selectedPath.findIndex(p => p[0] === row && p[1] === col);
        } else if (validMoves.some(m => m[0] === row && m[1] === col)) {
          square.classList.add('valid-move');
        }

        square.onclick = () => selectMove(row, col);
        board.appendChild(square);
      }
    }
  });
}

// 🛑 Remove getValidMoves() since it's now handled by the backend

function selectMove(row, col) {
  const last = selectedPath[selectedPath.length - 1];
  const dx = Math.abs(last[0] - row);
  const dy = Math.abs(last[1] - col);
  const isKnightMove = (dx === 2 && dy === 1) || (dx === 1 && dy === 2);

  if (!isKnightMove || selectedPath.some(p => p[0] === row && p[1] === col)) {
    document.getElementById('status').innerText = "Invalid move!";
    return;
  }

  selectedPath.push([row, col]);
  drawBoard([row, col]);

  if (selectedPath.length === 64) {
    submitPath();
    return;
  }

  // 🔁 Check if user is stuck using backend-powered drawBoard
  // drawBoard will automatically show valid moves; if none left, notify user
  fetch('http://localhost:5000/api/valid-moves', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      currentPos: [row, col],
      selectedPath: selectedPath
    })
  })
  .then(res => res.json())
  .then(data => {
    const nextValidMoves = data.validMoves;
    if (nextValidMoves.length === 0) {
      const tryUndo = confirm("You're stuck! Want to undo your last move and try again?");
      if (tryUndo) {
        selectedPath.pop(); // remove last move
        drawBoard(selectedPath[selectedPath.length - 1]); // redraw from previous
      } else {
        document.getElementById('status').innerText = "❌ You're stuck! Game Over.";
      }
    }
  });
}

function submitPath() {
  fetch('http://localhost:5000/api/validate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ path: selectedPath })
  })
  .then(res => res.json())
  .then(data => {
    if (data.valid) {
      document.getElementById('status').innerText = "✅ You Win!";
    } else {
      document.getElementById('status').innerText = "❌ " + data.message;
    }
  });
}
