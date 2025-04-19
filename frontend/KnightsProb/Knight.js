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

  document.getElementById('status').innerText = `✅ Knight moved to (${row}, ${col})`;


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

/*function submitPath() {
  fetch('http://localhost:5000/api/validate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ path: selectedPath })
  })
  .then(res => res.json())
  .then(data => {
    if (data.valid) {
      document.getElementById('status').innerText = "✅ Here's a valid Knight's Tour from your starting point! 🎉";
      document.getElementById('winner-form').style.display = 'block'; // Show input box

    } else if (data.message.includes("Incomplete Tour. But you are close! A solution is still possible from here.")) {
      const tryAgain = confirm(data.message + "\nDo you want to continue playing from here?");
      if (tryAgain) {
          selectedPath.pop();
          const lastPos = selectedPath[selectedPath.length - 1];
          drawBoard(lastPos);
      } else {
        document.getElementById('status').innerText = "❌ You chose to quit. Game over.";
      }
    } else {
      document.getElementById('status').innerText = "😕 Hmm... seems like you're out of valid moves. Let's double-check with my algorithms before we call this a loss...";

      const startingPoint = selectedPath[0];
      visualizeBacktrackingTour(startingPoint);
      
    }
  })
  .catch(err => {
    console.error("Error validating path:", err);
    document.getElementById('status').innerText = "❌ Error communicating with the server.";
  });
}
*/


function submitPath() {
  const selectedRadio = document.querySelector('input[name="algo"]:checked');
  if (!selectedRadio) return;

  const algo = selectedRadio.value; // "backtracking" or "warnsdorff"
  const endpoint = `http://localhost:5000/api/validate_${algo}`;

  // Log or display the selected algorithm
  console.log(`Selected Algorithm: ${algo}`);
  // Or show on UI (optional)
  document.getElementById('status').innerText = `🔍 Validating using: ${algo === 'backtracking' ? 'Backtracking Algorithm' : 'Warnsdorff’s Rule'}...`;

  fetch(endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ path: selectedPath })
  })
    .then(res => res.json())
    .then(data => {
      if (data.valid) {
        document.getElementById('status').innerText = "✅ Congrats! You Won. Enter your name to save 🎉";
        document.getElementById('winner-form').style.display = 'block';
      } else if (data.message.includes("Incomplete Tour. But you are close! A solution is still possible from here.")) {
        const tryAgain = confirm(data.message + "\nDo you want to continue playing from here?");
        if (tryAgain) {
          selectedPath.pop();
          const lastPos = selectedPath[selectedPath.length - 1];
          drawBoard(lastPos);
        } else {
          document.getElementById('status').innerText = "❌ You chose to quit. Game over.";
        }
      } else {
        document.getElementById('status').innerText = "😕 Hmm... seems like you're out of valid moves. Let's double-check with my algorithms before we call this a loss...";
        const startingPoint = selectedPath[0];

        if(algo === "backtracking"){
          visualizeBacktrackingTour(startingPoint); // Using backtracking algortihm to visualize the correct path
        }else{
          visualizeWarnsdoffTour(startingPoint) // Using Warnsdoff's algorith to visualize the correct path
        }
        //visualizeBothTour(startingPoint); // using both algo to get the correct path
      }
    })
    .catch(err => {
      console.error("Error validating path:", err);
      document.getElementById('status').innerText = "❌ Error communicating with the server.";
    });
}


//Submitting winner to the database
function submitWinner() {
  const username = document.getElementById("username").value.trim();
  if (!username) {
    alert("Please enter a username.");
    return;
  }

  const startX = selectedPath[0][0];
  const startY = selectedPath[0][1];
  const pathStr = JSON.stringify(selectedPath);
  const timestamp = new Date().toISOString();

  fetch("http://localhost:5000/api/submit_winner", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      name: username,
      start_x: startX,
      start_y: startY,
      path: pathStr,
      timestamp: timestamp
    })
  })
  .then(res => res.json())
  .then(data => {
    document.getElementById('status').innerText = `✅ ${data.message}`;
    document.getElementById('winner-form').style.display = 'none';
    document.getElementById('username').value = ''; // Clear input
  })
  .catch(err => {
    console.error("Error saving winner:", err);
    document.getElementById('status').innerText = "❌ Error saving winner.";
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
      console.log("✅ Backtracking solution path:", data.path);
      visualizeBacktrackSolution(data.path);
      document.getElementById('status').innerText = "❌ You lose this round! No worries, even the best fall sometimes. ";

    } else {
      document.getElementById('status').innerText = "Backtracking Algorithm can't find a solution due to recursion depth";
    }
  })
  .catch(err => {
    console.error("Error reaching the backend:", err);
    alert("Failed to reach the server.");
  });
}

function visualizeWarnsdoffTour(startingPoint) {
  console.log("Sending starting point to backend:", startingPoint);

  fetch('http://127.0.0.1:5000/api/warnsdorff', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ path: [startingPoint] })
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      console.log("✅ Warnsdoff's solution path:", data.path);
      visualizeBacktrackSolution(data.path);
      document.getElementById('status').innerText = "❌ You lose this round! No worries, even the best fall sometimes. ";

    } else {
      document.getElementById('status').innerText = "Warnsdoff's Algorithm can't find a solution due to recursion depth";
    }
  })
  .catch(err => {
    console.error("Error reaching the backend:", err);
    alert("Failed to reach the server.");
  });
}


function visualizeBothTour(startingPoint) {
  console.log("Sending starting point to backend:", startingPoint);

  fetch('http://127.0.0.1:5000/api/solve', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ path: [startingPoint] })
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      console.log("✅ Backtracking solution path:", data.path);
      visualizeBacktrackSolution(data.path);
      document.getElementById('status').innerText = "❌ You lose this round! No worries, even the best fall sometimes. ";

    } else {
      console.warn("❌ Backtracking failed. Trying Warnsdorff...");

      // 🔁 Fallback to Warnsdorff’s heuristic
      fetch('http://127.0.0.1:5000/api/warnsdorff', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: [startingPoint] })
      })
      .then(res => res.json())
      .then(warnData => {
        if (warnData.success) {
          console.log("⚡ Warnsdorff solution path:", warnData.path);
          visualizeBacktrackSolution(warnData.path); // Reuse same visualizer
          alert("Backtracking failed. Shown path uses Warnsdorff’s heuristic.");
          document.getElementById('status').innerText = "❌ You lose this round! No worries, even the best fall sometimes. ";

        } else {
          alert("No solution found even with Warnsdorff.");
          document.getElementById('status').innerText = "Oop! Seems even I can't solve the problem. So how about we call this game a tie and move on?";
        }
      })
      .catch(err => {
        console.error("Error during Warnsdorff fallback:", err);
        alert("Warnsdorff fallback failed.");
      });
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
      document.getElementById('status').innerText = "📚Game over! But learning never stops — check out this successful tour from your starting point.";
      return;
    }

    const [row, col] = path[index];
    selectedPath = path.slice(0, index + 1); // Update selectedPath to match progress
    drawBoard([row, col]);
    index++;
  }, 300); // Delay in ms between steps (adjust speed here)
}


