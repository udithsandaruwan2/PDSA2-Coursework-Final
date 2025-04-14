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

  const validMoves = getValidMoves(currentPos);

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
}

function getValidMoves([x, y]) {
  const moves = [
    [x + 2, y + 1], [x + 1, y + 2], [x - 1, y + 2], [x - 2, y + 1],
    [x - 2, y - 1], [x - 1, y - 2], [x + 1, y - 2], [x + 2, y - 1]
  ];

  return moves.filter(([nx, ny]) =>
    nx >= 0 && nx < 8 && ny >= 0 && ny < 8 &&
    !selectedPath.some(p => p[0] === nx && p[1] === ny)
  );
}

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

  const nextValidMoves = getValidMoves([row, col]);
  if (nextValidMoves.length === 0) {
    document.getElementById('status').innerText = "You're stuck! Submitting the path to check whether we can backtrack...";
    submitPath();
  }
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
    } else if (data.message.includes("Incomplete Tour. But you are close! A solution is still possible from here.")) {
      const tryAgain = confirm(data.message + "\nDo you want to continue playing from here?");
      if (tryAgain) {
        document.getElementById('status').innerText = "🔁 Continue playing. Try to complete the tour!";
      } else {
        document.getElementById('status').innerText = "❌ You chose to quit. Game over.";
      }
    } else {
      document.getElementById('status').innerText = "❌ " + data.message;
    }
  })
  .catch(err => {
    console.error("Error validating path:", err);
    document.getElementById('status').innerText = "❌ Error communicating with the server.";
  });
}
