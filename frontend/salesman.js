const canvas = document.getElementById("cityCanvas");
const ctx = canvas.getContext("2d");

if (!ctx) {
    console.error("Canvas context not available");
    alert("Your browser doesn't support canvas operations!");
}

let cities = [];
let playerRoute = [];
let nnRoute = [];
let bfRoute = [];
let hkRoute = [];

// Add player info variables at the top
let playerName = "Anonymous";
let homeCity = "Unknown";

const cityRadius = 8;
const numCities = 6;

// Generate random cities
let homeCityIndex = Math.floor(Math.random() * numCities); // Randomly choose a home city index

// Function to generate random cities with distances between 50 km and 100 km
function generateCities() {
    cities = [];
    playerRoute = [];
    nnRoute = [];
    bfRoute = [];
    hkRoute = [];
    
    const margin = 20;
    const maxWidth = canvas.width - margin * 2;
    const maxHeight = canvas.height - margin * 2;

    // Function to calculate random distances between 50 and 100 kilometers
    function getRandomDistance() {
        const minDistanceKm = 50;
        const maxDistanceKm = 100;
        const randomDistanceKm = Math.random() * (maxDistanceKm - minDistanceKm) + minDistanceKm;
        return randomDistanceKm * 10; // Convert to units
    }
    
    for (let i = 0; i < numCities; i++) {
        const x = Math.random() * maxWidth + margin;
        const y = Math.random() * maxHeight + margin;
        
        cities.push({
            x: Math.min(Math.max(x, margin), canvas.width - margin),
            y: Math.min(Math.max(y, margin), canvas.height - margin),
            id: i,
            distanceToNextCity: getRandomDistance()
        });
    }

    // Highlight the Home City
    document.getElementById("homeCity").innerText = `Home City: City ${homeCityIndex + 1}`;

    // Reset UI elements
    document.getElementById("humanResult").innerText = "Human Distance: N/A";
    document.getElementById("nnResult").style.display = "none";
    document.getElementById("bfResult").style.display = "none";
    document.getElementById("hkResult").style.display = "none";
    document.getElementById("toggles").style.display = "none";
    
    drawCities();
}
// Add function to collect player info
function collectPlayerInfo() {
    playerName = prompt("Please enter your name:", "Anonymous");
    homeCity = prompt("Please enter your home city:", "Unknown");
    if (!playerName) playerName = "Anonymous";
    if (!homeCity) homeCity = "Unknown";
}

// Update generateCities to prompt for player info on first run
const originalGenerateCities = generateCities;
generateCities = function() {
    if (playerName === "Anonymous") {
        collectPlayerInfo();
    }
    originalGenerateCities();
}

// Function to draw cities
function drawCities() {
    // Ensure canvas is cleared only if the first path isn't drawn yet
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    console.log("Drawing cities...");

    // Draw cities
    cities.forEach(city => {
        console.log(`Drawing city with id: ${city.id}`);

        ctx.beginPath();
        ctx.arc(city.x, city.y, cityRadius, 0, Math.PI * 2);

        // Set color: if it's the home city, make it a different color (e.g., red)
        if (city.id === homeCityIndex) {
            ctx.fillStyle = "#ff0000";  // Red color for home city
        } else {
            ctx.fillStyle = "#ff4136";  // Default color for other cities
        }
        ctx.fill();
        ctx.stroke();

        // Draw city ID text
        ctx.fillStyle = "black";
        ctx.fillText(`C${city.id}`, city.x + 10, city.y);

        // If it's the home city, draw "Home" text beneath it
        if (city.id === homeCityIndex) {
            ctx.fillText("Home", city.x - 10, city.y + 20);  // Display "Home" beneath the home city
        }
    });

    // Draw routes based on toggles
    const isGameOver = gameOver;
    if (document.getElementById("showHuman")?.checked && playerRoute.length > 1) {
        // If game is over, close the loop (draw return to home)
        if (isGameOver) {
            drawPath([cities[homeCityIndex], ...playerRoute, cities[homeCityIndex]], "blue", false);
        } else {
            // Draw human path but not close the loop (do not close the loop between home and first city)
            drawPath([cities[homeCityIndex], ...playerRoute], "blue", false);
        }
    }

    if (document.getElementById("showNN")?.checked && nnRoute.length > 1) {
        drawPath([cities[homeCityIndex], ...nnRoute], "green", true);  // Include home city at start and end
    }

    if (document.getElementById("showBF")?.checked && bfRoute.length > 1) {
        drawPath([cities[homeCityIndex], ...bfRoute], "purple", true);  // Include home city at start and end
    }

    if (document.getElementById("showHK")?.checked && hkRoute.length > 1) {
        drawPath([cities[homeCityIndex], ...hkRoute], "orange", true);  // Include home city at start and end
    }
}



function drawPath(route, color, closeLoop = false) {
    if (!route || route.length < 2) return;
    console.log(`Drawing path from ${route[0].id} to ${route[1].id}`);  // Add this log to check

    ctx.beginPath();
    ctx.moveTo(route[0].x, route[0].y);
    for (let i = 1; i < route.length; i++) {
        ctx.lineTo(route[i].x, route[i].y);
    }

    if (closeLoop) {
        ctx.lineTo(route[0].x, route[0].y);
    }

    ctx.strokeStyle = color;
    ctx.lineWidth = 2;
    ctx.stroke();
}


let firstPathDrawn = false;  // Flag to check if the first path has been drawn

canvas.addEventListener("click", (event) => {
    if (gameOver) return;  // If the game is over, ignore further clicks

    const rect = canvas.getBoundingClientRect();
    const mouseX = event.clientX - rect.left;
    const mouseY = event.clientY - rect.top;

    // Check if the clicked point is on a city
    for (let city of cities) {
        const dx = city.x - mouseX;
        const dy = city.y - mouseY;
        if (Math.sqrt(dx * dx + dy * dy) < cityRadius * 2) {
            console.log(`Clicked on city with id: ${city.id}`);

            // If the home city is clicked, automatically submit the route
            if (city.id === homeCityIndex) {
                console.log("Home city clicked, submitting route.");
                submitRoute();
                return;
            }

            // If it's the first city to be selected (playerRoute is empty)
            if (playerRoute.length === 0 && !firstPathDrawn) {
                console.log(`First city clicked: Drawing path from home city (id: ${homeCityIndex}) to city ${city.id}`);

                if (cities[homeCityIndex] && city) {
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                    drawCities();
                    drawPath([cities[homeCityIndex], city], "blue", false);
                    firstPathDrawn = true;
                    playerRoute.push(city);
                    console.log(`City ${city.id} added to player route.`);
                    // Do NOT call drawCities() at the end of the handler for the first city
                    return; // Prevent further code and the final drawCities() call
                } else {
                    console.error("Error: Home or first city is undefined.");
                    return;
                }
            }

            // If the city is already in the route, skip adding it again
            if (!playerRoute.includes(city)) {
                playerRoute.push(city);
                console.log(`City ${city.id} added to player route.`);
                if (playerRoute.length > 1) {
                    console.log(`Drawing path from city ${playerRoute[playerRoute.length - 2].id} to city ${city.id}`);
                    drawPath([playerRoute[playerRoute.length - 2], playerRoute[playerRoute.length - 1]], "blue", false);
                }
            }

            // Draw all cities and the paths (only for subsequent clicks)
            drawCities();
            break;
        }
    }
});


function getDistance(a, b) {
    // Calculate Euclidean distance between two cities
    const distanceInUnits = Math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2);
    return distanceInUnits; // If the canvas is scaled by 10 km each
}

function calculateTotalDistance(route) {
    let dist = 0;
    console.log("Calculating total distance for the human path:");
    for (let i = 0; i < route.length - 1; i++) {
        const distance = getDistance(route[i], route[i + 1]);
        dist += distance;
        console.log(`Distance between C${route[i].id} and C${route[i + 1].id}: ${distance.toFixed(2)} km`);
    }
    console.log(`Total human distance: ${dist.toFixed(2)} km`);
    return dist;
}

// Function to submit the player's route
function submitRoute() {
    if (playerRoute.length < 1) {
        alert("Please visit at least one city!");
        return;
    }

    // Build the full human route: home -> cities -> home
    const fullHumanRoute = [cities[homeCityIndex], ...playerRoute, cities[homeCityIndex]];

    // Draw the final segment from last visited city to home city if at least one city was visited
    if (playerRoute.length > 0) {
        drawPath([playerRoute[playerRoute.length - 1], cities[homeCityIndex]], "blue", false);
    }

    // Now calculate the distance, ensuring to include home-to-first-city and last-city-to-home
    const humanDistanceInUnits = calculateTotalDistance(fullHumanRoute);  // This should include the return to home
    const humanDistanceInKm = humanDistanceInUnits;  // Directly in km (no scaling needed)

    document.getElementById("humanResult").innerText = `Human Distance: ${humanDistanceInKm.toFixed(2)} km`;

    document.getElementById("nnResult").style.display = "none";
    document.getElementById("bfResult").style.display = "none";
    document.getElementById("toggles").style.display = "none";

    stopGame();

    drawCities(); // Redraw the cities and the final path
}

function compareWithAlgorithms() {
    console.log("Compare with Algorithms clicked");

    if (playerRoute.length < 1) {
        console.log("Player route is empty, please submit your route first!");  // Log if the player route is empty
        alert("Please submit your route first!");
        return;
    }

    // Prepare the cities array for backend: must include 'id', 'x', 'y' for each city
    const citiesForBackend = playerRoute.map(city => ({
        id: city.id,
        x: city.x,
        y: city.y
    }));

    try {
        const requestData = {
            cities: citiesForBackend,
            player_name: playerName,
            home_city: homeCity,
            human_route: playerRoute.map(city => city.id)
        };
        console.log("Data being sent to the backend:", requestData);

        fetch('http://127.0.0.1:5000/api/solve_tsp', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Defensive: check for error in response
            if (data.error) {
                alert(data.error);
                return;
            }

            // Process results and display them
            document.getElementById("toggles").style.display = "block";
            
            if (data.nearest_neighbor && !data.nearest_neighbor.error) {
                console.log("Nearest Neighbor result:", data.nearest_neighbor);  // Log the Nearest Neighbor result
                nnRoute = JSON.parse(data.nearest_neighbor.route);  // Parse route if it's JSON
                document.getElementById("nnResult").innerText =
                    `Nearest Neighbor: ${data.nearest_neighbor.distance.toFixed(2)} km (Time: ${(data.nearest_neighbor.time * 1000).toFixed(2)} ms)`;
                document.getElementById("nnResult").style.display = "block";
                document.getElementById("showNN").checked = true;
            }

            if (data.brute_force && !data.brute_force.error) {
                console.log("Brute Force result:", data.brute_force);  // Log the Brute Force result
                bfRoute = JSON.parse(data.brute_force.route);  // Parse route if it's JSON
                document.getElementById("bfResult").innerText =
                    `Brute Force: ${data.brute_force.distance.toFixed(2)} km (Time: ${(data.brute_force.time * 1000).toFixed(2)} ms)`;
                document.getElementById("bfResult").style.display = "block";
                document.getElementById("showBF").checked = true;
            }

            if (data.held_karp && !data.held_karp.error) {
                console.log("Held-Karp result:", data.held_karp);  // Log the Held-Karp result
                hkRoute = JSON.parse(data.held_karp.route);  // Parse route if it's JSON
                document.getElementById("hkResult").innerText =
                    `Held-Karp: ${data.held_karp.distance.toFixed(2)} km (Time: ${(data.held_karp.time * 1000).toFixed(2)} ms)`;
                document.getElementById("hkResult").style.display = "block";
                document.getElementById("showHK").checked = true;
            }

            drawCities();  // Redraw the cities with the updated routes
        })
        .catch(error => {
            console.error('Error during algorithm comparison:', error);
            alert('Error comparing algorithms. Check the console for more details.');
        });
    } catch (error) {
        console.error('Unexpected Error:', error);
        alert('Error comparing algorithms. Check the console for more details.');
    }
}


// Nearest Neighbour Algorithm
function nearestNeighbour(citiesList) {
    let unvisited = [...citiesList];
    let visited = [];
    let current = unvisited[0];
    visited.push(current);
    unvisited.splice(0, 1);

    while (unvisited.length > 0) {
        let nearest = unvisited.reduce((min, city) =>
            getDistance(current, city) < getDistance(current, min) ? city : min
        );
        current = nearest;
        visited.push(current);
        unvisited = unvisited.filter(c => c !== current);
    }
    return visited;
}

// Brute Force Algorithm
function bruteForce(citiesList) {
    if (citiesList.length > 8) {
        alert("Too many cities for brute force approach! Maximum is 8 cities.");
        return [];
    }

    try {
        const permutations = permute(citiesList);
        let bestDistance = Infinity;
        let bestRoute = [];

        permutations.forEach(route => {
            const dist = calculateTotalDistance([...route, route[0]]);
            if (dist < bestDistance) {
                bestDistance = dist;
                bestRoute = route;
            }
        });

        return bestRoute;
    } catch (error) {
        console.error("Error in brute force algorithm:", error);
        return [];
    }
}

function permute(arr) {
    if (arr.length === 0) return [[]];
    return arr.flatMap((v, i) =>
        permute([...arr.slice(0, i), ...arr.slice(i + 1)]).map(p => [v, ...p])
    );
}

let gameOver = false;  // Flag to track if the game is over

// Reset game function
function resetGame() {
    gameOver = false;  // Reset gameOver flag
    playerRoute = [];
    nnRoute = [];
    bfRoute = [];
    hkRoute = [];
    firstPathDrawn = false;  // Reset the first path drawing flag

    document.getElementById("humanResult").innerText = "Human Distance: N/A";
    document.getElementById("nnResult").style.display = "none";
    document.getElementById("bfResult").style.display = "none";
    document.getElementById("hkResult").style.display = "none";

    // Reset checkboxes with correct IDs
    document.getElementById("showHuman").checked = true;
    document.getElementById("showNN").checked = false;
    document.getElementById("showBF").checked = false;
    document.getElementById("showHK").checked = false;

    // Generate new cities after reset
    generateCities();  // Generate new cities after reset
}

// Stop the game from proceeding further after submitting the route or clicking home city
function stopGame() {
    gameOver = true;
    document.getElementById("humanResult").innerText += " (Game Over)";
}

// Add viewStats function to display database statistics
function viewStats() {
    fetch('http://127.0.0.1:5000/api/view_stats')
        .then(response => response.json())
        .then(data => { 
            const statsDiv = document.getElementById('statsContent');
            const stats = data.stats;
            
            if (!stats || stats.length === 0) {
                statsDiv.innerHTML = '<p>No statistics available yet.</p>';
                return;
            }

            let html = '<table class="stats-table">';
            html += '<  tr><th>Algorithm</th><th>Avg Time (ms)</th><th>Min Time (ms)</th><th>Max Time (ms)</th><th>Avg Distance</th></tr>';
            
            stats.forEach(stat => {
                const [algo, avgTime, minTime, maxTime, avgDist] = stat;
                html += `
                    <tr>
                        <td>${algo}</td>
                        <td>${(avgTime * 1000).toFixed(2)}</td>
                        <td>${(minTime * 1000).toFixed(2)}</td>
                        <td>${(maxTime * 1000).toFixed(2)}</td>
                        <td>${avgDist.toFixed(2)}</td>
                    </tr>
                `;
            });
            
            html += '</table>';
            statsDiv.innerHTML = html;
            document.getElementById('statsResult').style.display = 'block';
        })
        .catch(error => {
            console.error('Error fetching stats:', error);
            document.getElementById('statsContent').innerHTML = 
                '<p class="error">Error loading statistics. Check console for details.</p>';
            document.getElementById('statsResult').style.display = 'block';
        });
}

// Add link to database viewer
function addDatabaseViewerLink() {
    const link = document.createElement('a');
    link.href = 'http://127.0.0.1:5000/api/db_viewer';
    link.target = '_blank';
    link.innerText = 'View Database Contents';
    link.style.display = 'block';
    link.style.marginTop = '20px';
    document.getElementById('result').appendChild(link);
}

// Update initial load to add database viewer link
window.onload = function() {
    console.log("Generating cities...");
    generateCities();
    addDatabaseViewerLink();
}
