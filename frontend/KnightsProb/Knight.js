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
          // Backtrack one move
          selectedPath.pop();
          // Get the new last position
          const lastPos = selectedPath[selectedPath.length - 1];
          // Redraw the board from the new position
          drawBoard(lastPos);
      } else {
        document.getElementById('status').innerText = "❌ You chose to quit. Game over.";
      }
    } else {
      document.getElementById('status').innerText = "❌ " + data.message;
      // in here we can call the fucntion ti visualize
      
      // Get the same starting point that user got
      const startingPoint = selectedPath[0];

      // Call the function to visualize a full Knight's Tour from startingPoint
      visualizeBacktrackingTour(startingPoint);
      
    }
  })
  .catch(err => {
    console.error("Error validating path:", err);
    document.getElementById('status').innerText = "❌ Error communicating with the server.";
  });
}


function visualizeBacktrackingTour(startingPoint) {
  console.log("Sending starting point to backend:", startingPoint);

  fetch('http://127.0.0.1:5000/api/solve', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ path: [startingPoint] })
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      console.log("Backtracking solution path:", data.path); // 👈 Print the path
      //visualizeBacktrackSolution(data.path);
    } else {
      alert("No solution found from this starting point.");
    }
  })
  .catch(err => {
    console.error("Error reaching the backend:", err);
    alert("Failed to reach the server.");
  });
}


function visualizeBacktrackSolution(path) {
  let index = 0;

  const interval = setInterval(() => {
    if (index >= path.length) {
      clearInterval(interval);
      document.getElementById('status').innerText = "✅ Here's a valid Knight's Tour from your starting point!";
      return;
    }

    const [row, col] = path[index];
    selectedPath = path.slice(0, index + 1); // Update selectedPath to match progress
    drawBoard([row, col]);
    index++;
  }, 300); // Delay in ms between steps (adjust speed here)
}


