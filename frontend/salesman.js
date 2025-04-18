const canvas = document.getElementById("cityCanvas");
const ctx = canvas.getContext("2d");

let gameOver = false;  // Flag to track if the game is over
if (!ctx) {
    console.error("Canvas context not available");
    alert("Your browser doesn't support canvas operations!");
}

let cities = [];
let playerRoute = [];
let nnRoute = [];
let bfRoute = [];
let hkRoute = [];
let distanceMatrix = {};
let playerPathSegments = [];  // Each element: { from: cityA, to: cityB }



// Add player info variables at the top
let playerName = "Anonymous";
let homeCity = "Unknown";

const cityRadius = 8;
const numCities = 10;
let humanDistanceInKm = 0; // Initialize human distance variable
// Generate random cities
let homeCityIndex = Math.floor(Math.random() * numCities); // Randomly choose a home city index
const homeChar = String.fromCharCode(65 + homeCityIndex); 

function generateCities() {
    playerRoute = [];
    nnRoute = [];
    bfRoute = [];
    hkRoute = [];
    firstPathDrawn = false;

    fetch('http://127.0.0.1:5000/api/get_city_distances')
        .then(res => res.json())
        .then(data => {
            if (!data || !data.cities || !data.distances) {
                console.error("Invalid city data:", data);
                return;
            }

            cities = data.cities;
            distanceMatrix = data.distances;

            // Assign dummy x/y positions for drawing (you can make this prettier later)
            const padding = 100;
            const spacingX = (canvas.width - 2 * padding) / numCities;
            const spacingY = (canvas.height - 2 * padding) / numCities;

            cities.forEach((city, index) => {
                const angle = Math.random() * 2 * Math.PI;
                const maxRadius = Math.min(canvas.width, canvas.height) / 2 - (-30); // 60 = safe margin
                const radius = Math.random() * maxRadius;
                const centerX = canvas.width / 2;
                const centerY = canvas.height / 2;
            
                city.x = centerX + radius * Math.cos(angle);
                city.y = centerY + radius * Math.sin(angle);
            });
            

            homeCityIndex = Math.floor(Math.random() * cities.length);
            const homeCityChar = String.fromCharCode(65 + homeCityIndex);
            document.getElementById("homeCity").innerText = `Home City: City ${homeCityChar}`;

            drawCities();
        })
        .catch(err => {
            console.error("Error generating cities:", err);
        });
}


// Function to convert city ID to alphabetic character (e.g., 0 -> A, 1 -> B, etc.)
function getCityChar(cityId) {
    return String.fromCharCode(65 + cityId); // 65 is ASCII for 'A'
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

// Add function to collect player info
function collectPlayerInfo() {
    playerName = prompt("Please enter your name:", "Anonymous");
    if (!playerName) playerName = "Anonymous";
}

// Update generateCities to prompt for player info on first run
const originalGenerateCities = generateCities;
generateCities = function() {
    if (playerName === "Anonymous") {
        collectPlayerInfo();
    }
    originalGenerateCities();
}
function drawCities() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    //  Draw all cities
    cities.forEach(city => {
        ctx.beginPath();
        ctx.arc(city.x, city.y, cityRadius, 0, Math.PI * 2);
        ctx.fillStyle = city.id === homeCityIndex ? "#ff0000" : "#ff4136";
        ctx.fill();
        ctx.stroke();

        const label = String.fromCharCode(65 + city.id);
        ctx.fillStyle = "black";
        ctx.fillText(label, city.x + 10, city.y);
        if (city.id === homeCityIndex) ctx.fillText("Home", city.x - 10, city.y + 20);
    });

    // ✅ Draw algorithm paths (conditionally)
    if (document.getElementById("showNN")?.checked && nnRoute.length > 1) {
        drawPath([cities[homeCityIndex], ...nnRoute, cities[homeCityIndex]], "green", true);
    }
    if (document.getElementById("showBF")?.checked && bfRoute.length > 1) {
        drawPath([cities[homeCityIndex], ...bfRoute, cities[homeCityIndex]], "purple", true);
    }
    if (document.getElementById("showHK")?.checked && hkRoute.length > 1) {
        drawPath([cities[homeCityIndex], ...hkRoute, cities[homeCityIndex]], "orange", true);
    }

    // 🔷 Draw human route if toggle is on
    if (document.getElementById("showHuman")?.checked) {
        ctx.strokeStyle = "blue";
        ctx.lineWidth = 2;
        ctx.fillStyle = "black";
        ctx.font = "12px Arial";

        playerPathSegments.forEach(segment => {
            const { from, to } = segment;
            ctx.beginPath();
            ctx.moveTo(from.x, from.y);
            ctx.lineTo(to.x, to.y);
            ctx.stroke();

            const midX = (from.x + to.x) / 2;
            const midY = (from.y + to.y) / 2;
            const dist = getDistance(from, to);
            ctx.fillText(`${dist.toFixed(1)} km`, midX + 5, midY - 5);
        });
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
                    playerPathSegments.push({ from: cities[homeCityIndex], to: city });
                    playerRoute.push(city);
                    firstPathDrawn = true;
                    
                    drawCities();  // 👈 Force immediate redraw, including the line
                    
                    console.log(`City ${city.id} added to player route.`);
                    return;
                    
                }
            }

            // If the city is already in the route, skip adding it again
            if (!playerRoute.includes(city)) {
                playerRoute.push(city);
                console.log(`City ${city.id} added to player route.`);
                if (playerRoute.length > 1) {
                    console.log(`Drawing path from city ${playerRoute[playerRoute.length - 2].id} to city ${city.id}`);
                    const from = playerRoute[playerRoute.length - 2];
                    const to = playerRoute[playerRoute.length - 1];
                    playerPathSegments.push({ from, to });  // Track this segment
                    // Show distance label on the segment
                    const a = playerRoute[playerRoute.length - 2];
                    const b = playerRoute[playerRoute.length - 1];
                    const midX = (a.x + b.x) / 2;
                    const midY = (a.y + b.y) / 2;
                    const dist = getDistance(a, b);
                    ctx.fillStyle = "black";
                    ctx.font = "12px Arial";
                    ctx.fillText(`${dist.toFixed(1)} km`, midX + 5, midY - 5);

                }
            }

            // Draw all cities and the paths (only for subsequent clicks)
            drawCities();
            break;
        }
    }
});


function getDistance(a, b) {
    return distanceMatrix[a.id][b.id] || 0;
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
    // Push final leg to playerPathSegments for rendering with distance
    const from = playerRoute[playerRoute.length - 1];
    const to = cities[homeCityIndex];
    playerPathSegments.push({ from, to });

    // Now calculate the distance, ensuring to include home-to-first-city and last-city-to-home
    const humanDistanceInUnits = calculateTotalDistance(fullHumanRoute);  // This should include the return to home
    humanDistanceInKm = humanDistanceInUnits;  // Update the global variable with the calculated value

    console.log(`Full Human Route: `, fullHumanRoute);  // Log the full human route for debugging
    console.log(`Human Distance: `, humanDistanceInKm);

    // Display the human distance in the frontend
    document.getElementById("humanResult").innerText = `Human Distance: ${humanDistanceInKm.toFixed(1)} km`;

    // Hide algorithm results until comparison
    document.getElementById("nnResult").style.display = "none";
    document.getElementById("bfResult").style.display = "none";
    document.getElementById("hkResult").style.display = "none";
    document.getElementById("toggles").style.display = "none";

    stopGame();

    drawCities(); // Redraw the cities and the final path
}


function compareWithAlgorithms() {
    console.log("Compare with Algorithms clicked");
    submitRoute();  // Ensure the route is submitted before comparison
    if (playerRoute.length < 1) {
        console.log("Player route is empty, please submit your route first!");
        alert("Please submit your route first!");
        return;
    }

    const homeCityObj = cities[homeCityIndex];
    const selectedCityIds = playerRoute.map(city => city.id);
    const selectedCities = cities.filter(city => selectedCityIds.includes(city.id));
    const selectedCityChars = selectedCities.map(city => String.fromCharCode(65 + city.id));
    const homeCityChar = String.fromCharCode(65 + homeCityObj.id);

    const requestData = {
        cities: cities.map(c => ({ id: c.id, name: c.name })),
        player_name: playerName,
        home_city: homeCityChar,
        human_route: selectedCityChars,
        distances: distanceMatrix
    };

    fetch('http://127.0.0.1:5000/api/solve_tsp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestData)
    })
    .then(response => {
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
        return response.json();
    })
    .then(data => {
        document.getElementById("toggles").style.display = "block";

        // 🧠 Convert returned city IDs/objects to full city objects with x/y
        const idToCity = (c) => typeof c === 'object' ? cities.find(city => city.id === c.id) : cities.find(city => city.id === c);

        if (data.nearest_neighbor && !data.nearest_neighbor.error) {
            nnRoute = data.nearest_neighbor.route.map(idToCity);
            document.getElementById("nnResult").innerText =
                `Nearest Neighbor: ${data.nearest_neighbor.distance.toFixed(1)} km (Time: ${(data.nearest_neighbor.time * 1000).toFixed(2)} ms)`;
            document.getElementById("nnResult").style.display = "block";
            document.getElementById("showNN").checked = true;
        }

        if (data.brute_force && !data.brute_force.error) {
            bfRoute = data.brute_force.route.map(idToCity);
            document.getElementById("bfResult").innerText =
                `Brute Force: ${data.brute_force.distance.toFixed(1)} km (Time: ${(data.brute_force.time * 1000).toFixed(2)} ms)`;
            document.getElementById("bfResult").style.display = "block";
            document.getElementById("showBF").checked = true;
        }

        if (data.held_karp && !data.held_karp.error) {
            hkRoute = data.held_karp.route.map(idToCity);
            document.getElementById("hkResult").innerText =
                `Held-Karp: ${data.held_karp.distance.toFixed(1)} km (Time: ${(data.held_karp.time * 1000).toFixed(2)} ms)`;
            document.getElementById("hkResult").style.display = "block";
            document.getElementById("showHK").checked = true;
        }

        const humanDistance = humanDistanceInKm.toFixed(1);
        const nnDistance = parseFloat(data.nearest_neighbor.distance).toFixed(1);
        const bfDistance = parseFloat(data.brute_force.distance).toFixed(1);
        const hkDistance = parseFloat(data.held_karp.distance).toFixed(1);

        let resultMessage = "";
        if (humanDistance <= nnDistance && humanDistance <= bfDistance && humanDistance <= hkDistance) {
            resultMessage = humanDistance < nnDistance || humanDistance < bfDistance || humanDistance < hkDistance
                ? "Congratulations! You found the shortest route!"
                : "Congratulations! You matched the best algorithm route!";
            saveWinToDatabase(data, humanDistance, selectedCityChars);
        } else {
            resultMessage = "Nice try! The algorithm found a shorter route.";
            saveGameSessionToDatabase(data, selectedCityChars);
        }

        document.getElementById("resultMessage").innerText = resultMessage;
        drawCities();  // 🔁 Redraw with all updated routes
    })
    .catch(error => {
        console.error('Error during algorithm comparison:', error);
        alert('Error comparing algorithms. Check the console for more details.');
    });
}



// Function to save the game session after algorithm comparison
function saveGameSessionToDatabase(data, selectedCityIds) {
    const requestData = {
        player_name: playerName,
        home_city: homeChar, // Use the updated home city here
        selected_cities: selectedCityIds,
        nn_distance: data.nearest_neighbor.distance,
        bf_distance: data.brute_force.distance,
        hk_distance: data.held_karp.distance,
        nn_time: data.nearest_neighbor.time,
        bf_time: data.brute_force.time,
        hk_time: data.held_karp.time,
    };

    // Send the game session data to the backend to be saved
    fetch('http://127.0.0.1:5000/api/save_game_session', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
    })
    .then(response => response.json())
    .then(data => {
        console.log('Game session saved:', data);
    })
    .catch(error => {
        console.error('Error saving game session:', error);
    });
}



// Function to save the winning data to the database
function saveWinToDatabase(data, humanDistance, humanRoute) {
    const requestData = {
        session_id: data.session_id,
        player_name: playerName,
        home_city: homeChar,
        human_route: humanRoute,
        human_distance: humanDistance,
        nn_distance: data.nearest_neighbor.distance,
        bf_distance: data.brute_force.distance,
        hk_distance: data.held_karp.distance,
        nn_time: data.nearest_neighbor.time,
        bf_time: data.brute_force.time,
        hk_time: data.held_karp.time,
    };

    fetch('http://127.0.0.1:5000/api/save_win', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
    })
    .then(response => response.json())
    .then(data => {
        console.log("Player win saved successfully!");
    })
    .catch(error => {
        console.error('Error saving player win to database:', error);
    });
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


// Reset game function
function resetGame() {
    gameOver = false;  // Reset gameOver flag
    playerRoute = [];
    nnRoute = [];
    bfRoute = [];
    hkRoute = [];
    playerPathSegments = [];  // Clear route segments

    firstPathDrawn = false;  // Reset the first path drawing flag

    document.getElementById("humanResult").innerText = "Human Distance: N/A";
    document.getElementById("nnResult").style.display = "none";
    document.getElementById("bfResult").style.display = "none";
    document.getElementById("hkResult").style.display = "none";
    document.getElementById("resultMessage").innerText = "";  // Clear result message

    // Reset checkboxes with correct IDs
    document.getElementById("showHuman").checked = true;
    document.getElementById("showNN").checked = false;
    document.getElementById("showBF").checked = false;
    document.getElementById("showHK").checked = false;

    homeCityIndex = Math.floor(Math.random() * numCities);

    // Generate new cities after reset
    generateCities();  // Generate new cities after reset
}

// Stop the game from proceeding further after submitting the route or clicking home city
function stopGame() {
    gameOver = true;
    document.getElementById("humanResult").innerText += " (Game Over)";
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

document.addEventListener("DOMContentLoaded", () => {
    console.log("DOM fully loaded. Initializing game...");
    generateCities(); // ← this is your wrapped version with player prompt
    addDatabaseViewerLink();

    // Attach checkbox event listeners just in case `onchange` fails
    ['showHuman', 'showNN', 'showBF', 'showHK'].forEach(id => {
        const checkbox = document.getElementById(id);
        if (checkbox) {
            checkbox.addEventListener('change', drawCities);
        }
    });
});



function viewCityDistances() {
    if (!cities || cities.length < 2) {
        alert("No cities available to show distances.");
        return;
    }

    const tableDiv = document.getElementById('statsContent');
    let html = "<h2>City Distance Table</h2>";
    html += "<table class='distance-table' style='border-collapse: collapse; width: 100%; text-align: center;'>";

    html += "<tr><th>City</th>";
    for (let i = 0; i < cities.length; i++) {
        html += `<th>${String.fromCharCode(65 + i)}</th>`;
    }
    html += "</tr>";

    for (let i = 0; i < cities.length; i++) {
        html += `<tr><td>${String.fromCharCode(65 + i)}</td>`;
        for (let j = 0; j < cities.length; j++) {
            if (i === j) {
                html += "<td>---</td>";
            } else {
                const dist = distanceMatrix[i][j]?.toFixed(2) || "N/A";
                html += `<td>${dist} km</td>`;
            }
        }
        html += "</tr>";
    }

    html += "</table>";
    tableDiv.innerHTML = html;
    document.getElementById('statsResult').style.display = 'block';
}

