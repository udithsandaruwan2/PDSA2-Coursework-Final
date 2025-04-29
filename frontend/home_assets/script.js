// Initial API fetch
fetch('http://127.0.0.1:5000/')
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error("Error:", error));

// Add some visual feedback when clicking games
document.addEventListener('DOMContentLoaded', function() {
    // Remove loading class if it exists when returning to the page
    document.body.classList.remove('loading');
    
    const gameTiles = document.querySelectorAll('.game-tile');
    
    gameTiles.forEach(tile => {
        tile.addEventListener('click', function(e) {
            // Add click effect
            this.style.transform = 'scale(0.95) translateY(-5px)';
            
            // Add ripple effect
            let ripple = document.createElement('span');
            ripple.classList.add('ripple');
            this.appendChild(ripple);
            
            // Calculate position based on the tile itself
            const rect = this.getBoundingClientRect();
            let x = e.clientX - rect.left;
            let y = e.clientY - rect.top;
            
            ripple.style.left = `${x}px`;
            ripple.style.top = `${y}px`;
            
            setTimeout(() => {
                ripple.remove();
                this.style.transform = '';
            }, 300);
        });
    });
});

// Game navigation function
function startGame(game) {
    // Create a session storage flag to track that we're navigating away
    sessionStorage.setItem('gameNavigation', 'true');
    
    // Show loading animation
    document.body.classList.add('loading');
    
    // Wait a moment before redirecting for better UX
    setTimeout(() => {
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
        else {
            console.error("Unknown game:", game);
            alert("Unknown game: " + game);
            document.body.classList.remove('loading');
            sessionStorage.removeItem('gameNavigation');
        }
    }, 300); // Reduced timeout for faster navigation
}