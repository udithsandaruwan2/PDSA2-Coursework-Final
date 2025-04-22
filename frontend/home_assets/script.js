fetch('http://127.0.0.1:5000/')
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error("Error:", error));

function startGame(game) {
    if (game === "tic_tac_toe") {
        window.location.href = "tic_tac_toe.html";  // Redirect to Tic-Tac-Toe page
    } else if (game === "salesman_problem") {
        window.location.href = "salesman_problem.html";
    } else if (game === "tower_of_hanoi") {
        window.location.href = "tower_of_hanoi.html";
    } else if (game === "eight_queens") {
        window.location.href = "eight_queens.html";
    } else if (game === "knight_problem") {
        window.location.href = "knight_problem.html";
    } 
    else{
        console.error("Unknown game:", game);
        alert("Unknown game: " + game);
    }
}
