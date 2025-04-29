let selectedPath = [];
let startPosition = null;


function startGame() {
  fetch('http://localhost:5000/knight/start')
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
  fetch('http://localhost:5000/knight/validate', {
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
  const endpoint = `http://localhost:5000/knight/validate_${algo}`;

  // Log or display the selected algorithm
  console.log(`Selected Algorithm: ${algo}`);
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

        // 🎯 After a win: Calculate performance of both algorithms
        const startingPoint = selectedPath[0];

        // Solve using Backtracking
        fetch("http://localhost:5000/knight/solve", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ path: [startingPoint] })
        })
        .then(res => res.json())
        .then(backtrackData => {
          const backtrackingTime = backtrackData.backtrack_elapsed_time ;

          // Solve using Warnsdorff
          fetch("http://localhost:5000/knight/warnsdorff", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ path: [startingPoint] })
          })
          .then(res => res.json())
          .then(warnsdoffData => {
            const warnsdoffTime = warnsdoffData.warnsdoff_elapsed_time;

            // Save performance
            console.log("Saving performance metrics to backend:", backtrackingTime, warnsdoffTime);
            savePerformanceData(backtrackingTime, warnsdoffTime);
          })
          .catch(err => console.error("❌ Error calling Warnsdorff API:", err));
        })
        .catch(err => console.error("❌ Error calling Backtracking API:", err));
      } 
      else if (data.message.includes("Incomplete Tour. But you are close! A solution is still possible from here.")) {
        const tryAgain = confirm(data.message + "\nDo you want to continue playing from here?");
        if (tryAgain) {
          selectedPath.pop();
          const lastPos = selectedPath[selectedPath.length - 1];
          drawBoard(lastPos);
        } else {
          document.getElementById('status').innerText = "❌ You chose to quit. Game over.";
        }
      } 
      else {
        document.getElementById('status').innerText = "😕 Hmm... seems like you're out of valid moves. Let's double-check with my algorithms before we call this a loss...";
        const startingPoint = selectedPath[0];

        if (algo === "backtracking") {
          visualizeBacktrackingTour(startingPoint);
        } else if (algo === "warnsdorff") {
          visualizeWarnsdoffTour(startingPoint);
        } else if (algo === "using_both") {
          visualizeBothTour(startingPoint);
        } else {
          alert("Please select one or both algorithm");
        }
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

  fetch("http://localhost:5000/knight/submit_winner", {
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

  fetch('http://127.0.0.1:5000/knight/solve', {
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
      const backtrackingTime = data.backtrack_elapsed_time;
      savePerformanceData(backtrackingTime, null);

    } else {
      const backtrackingTime = data.backtrack_elapsed_time;
      savePerformanceData(backtrackingTime, null);
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

  fetch('http://127.0.0.1:5000/knight/warnsdorff', {
    method: 'POST',
    headers:  { 'Content-Type': 'application/json' },
    body: JSON.stringify({ path: [startingPoint] })
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      console.log("✅ Warnsdoff's solution path:", data.path);
      visualizeBacktrackSolution(data.path);
      document.getElementById('status').innerText = "❌ You lose this round! No worries, even the best fall sometimes. ";
      const warnsdoffsTime = data.warnsdoff_elapsed_time;
      savePerformanceData(null, warnsdoffsTime);

    } else {
      const warnsdoffsTime = data.warnsdoff_elapsed_time;
      savePerformanceData(null, warnsdoffsTime);
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

  let backtrackingTime;
  let warnsdoffTime;

  fetch('http://127.0.0.1:5000/knight/solve', {
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
      document.getElementById('path').innerText = `Backtracking path: ${JSON.stringify(data.path)}`;

      backtrackingTime = data.backtrack_elapsed_time;

      // Warnsdoff's Path
      fetch('http://127.0.0.1:5000/knight/warnsdorff', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: [startingPoint] })
      })
      .then(res => res.json())
      .then(warnData => {
        if (warnData.success) {
          console.log("⚡ Warnsdorff solution path:", warnData.path);

            visualizeWarnsdorffSolution(warnData.path); 
            document.getElementById('warnsdoffs_path').innerText = `Warnsdoff's path: ${JSON.stringify(warnData.path)}`;
         

          warnsdoffTime = warnData.warnsdoff_elapsed_time;
        } else {
          document.getElementById('warnsdoffs_path').innerText = "No path found using WarnsDoff's algorithm";
          document.getElementById('status').innerText = "🤝 Oop! Seems even I can't solve the problem. So how about we call this game a tie and move on?";
          warnsdoffTime = warnData.warnsdoff_elapsed_time;
        }

        savePerformanceData(backtrackingTime, warnsdoffTime);
      })
      .catch(err => {
        console.error("Error during Warnsdorff fallback:", err);
        alert("Warnsdorff fallback failed.");
        savePerformanceData(backtrackingTime, warnsdoffTime);
      });

    } else {
      document.getElementById('path').innerText = `No path found using backtracking algorithm`;

      console.warn("❌ Backtracking failed. Trying Warnsdorff...");
      backtrackingTime = data.backtrack_elapsed_time;

      // 🔁 Fallback to Warnsdorff’s heuristic
      fetch('http://127.0.0.1:5000/knight/warnsdorff', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: [startingPoint] })
      })
      .then(res => res.json())
      .then(warnData => {
        if (warnData.success) {
          console.log("⚡ Warnsdorff solution path:", warnData.path);
          visualizeBacktrackSolution(warnData.path); // Reuse same visualizer
          document.getElementById('warnsdoffs_path').innerText = `Warnsdoff's path: ${JSON.stringify(warnData.path)}`;
          document.getElementById('status').innerText = "Backtracking failed path using Warnsdoff's algorithm ";
          document.getElementById('status').innerText = "❌ You lose this round! No worries, even the best fall sometimes. ";
          warnsdoffTime = warnData.warnsdoff_elapsed_time;
        } else {
          alert("No solution found even with Warnsdorff.");
          warnsdoffTime = warnData.warnsdoff_elapsed_time;
          document.getElementById('status').innerText = "Oop! Seems even I can't solve the problem. So how about we call this game a tie and move on?";
        }

        savePerformanceData(backtrackingTime, warnsdoffTime);
      })
      .catch(err => {
        console.error("Error during Warnsdorff fallback:", err);
        alert("Warnsdorff fallback failed.");
        savePerformanceData(backtrackingTime, warnsdoffTime);
      });
    }
  })
  .catch(err => {
    console.error("Error reaching the backend:", err);
    alert("Failed to reach the server.");
  });
}


// Same visualizer for all the  three options
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
  }, 400); // Delay in ms between steps (adjust speed here)
}

function visualizeWarnsdorffSolution(path) {
  console.log("Visualizing Warnsdorff's solution path:", path);

  // Get the Warnsdorff board element and make it visible
  const warnsdorffBoard = document.getElementById('warnsdorff-board');
  const warnsdorffContainer = document.getElementById('warnsdorff-container');
  warnsdorffContainer.style.display = 'block'; // Make the Warnsdorff board visible

  // Clear the board before rendering
  warnsdorffBoard.innerHTML = '';

  let index = 0;
  const interval = setInterval(() => {
    if (index >= path.length) {
      clearInterval(interval);
      document.getElementById('status').innerText = "📚 Game over! You've completed the Warnsdorff's tour.";
      return;
    }

    const [row, col] = path[index];
    selectedPath = path.slice(0, index + 1); // Update the selected path to match progress
    drawWarnsdorffBoard([row, col]); // Draw Warnsdorff's path on its board
    index++;
  }, 400); // Adjust the speed here
}

function drawWarnsdorffBoard(currentPos) {
  const board = document.getElementById('warnsdorff-board');
  board.innerHTML = '';

  const validMoves = getValidMoves(currentPos); // Assuming this function works for Warnsdorff

  for (let row = 0; row < 8; row++) {
    for (let col = 0; col < 8; col++) {
      const square = document.createElement('div');
      square.classList.add('square');
      square.classList.add((row + col) % 2 === 0 ? 'white' : 'black');
      square.dataset.row = row;
      square.dataset.col = col;

      if (row === currentPos[0] && col === currentPos[1]) {
        square.classList.add('start');
        square.innerText = '♞'; // Knight symbol
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



function savePerformanceData(backtrackingTime, warnsdoffTime) {
  console.log("📊 Saving performance data...");
  console.log("⏱️ Backtracking time:", backtrackingTime);
  console.log("⏱️ Warnsdorff time:", warnsdoffTime );

  fetch('http://127.0.0.1:5000/knight/save', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      backtracking_time: backtrackingTime,
      warnsdoffs_time: warnsdoffTime
    })
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      console.log("✅ Performance data saved successfully.");
    } else {
      console.warn("⚠️ Failed to save performance data:", data.message);
    }
  })
  .catch(err => {
    console.error("❌ Error saving performance data:", err);
  });
}
