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
    cities = [];
    playerRoute = [];
    nnRoute = [];
    bfRoute = [];
    hkRoute = [];

    const kmToUnit = 1; // 1 km = 10 canvas units
    const minDist = 50 * kmToUnit;
    const maxDist = 100 * kmToUnit;
    const margin = 20;

    const canvasWidth = canvas.width;
    const canvasHeight = canvas.height;

    // Start with center city
    const center = {
        x: canvasWidth / 2,
        y: canvasHeight / 2,
        id: 0
    };
    cities.push(center);

    for (let i = 1; i < numCities; i++) {
        let placed = false;
        let attempts = 0;

        while (!placed && attempts < 150000) {
            const base = cities[Math.floor(Math.random() * cities.length)];
            const angle = Math.random() * Math.PI * 2;
            const distance = minDist + Math.random() * (maxDist - minDist);

            const newX = base.x + distance * Math.cos(angle);
            const newY = base.y + distance * Math.sin(angle);

            if (
                newX > margin && newX < canvasWidth - margin &&
                newY > margin && newY < canvasHeight - margin
            ) {
                const newCity = { x: newX, y: newY, id: i };

                // Check distances to all previous cities
                let valid = cities.every(city => {
                    const dx = newCity.x - city.x;
                    const dy = newCity.y - city.y;
                    const dist = Math.sqrt(dx * dx + dy * dy);
                    return dist >= minDist && dist <= maxDist;
                });

                if (valid) {
                    cities.push(newCity);
                    placed = true;
                }
            }

            attempts++;
        }

        if (!placed) {
            console.warn(`Failed to place city ${i} after ${attempts} attempts.`);
            break;
        }
    }

    homeCityIndex = Math.floor(Math.random() * cities.length);
    const homeCityChar = String.fromCharCode(65 + homeCityIndex);
    document.getElementById("homeCity").innerText = `Home City: City ${homeCityChar}`;
    drawCities();
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
    // Ensure canvas is cleared
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    console.log("Drawing cities...");

    // Draw cities using coordinates from the backend
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

        // Draw city ID text as A, B, C, ...
        const cityLabel = String.fromCharCode(65 + city.id); // 65 is 'A'
        ctx.fillStyle = "black";
        ctx.fillText(`${cityLabel}`, city.x + 10, city.y);

        // If it's the home city, draw "Home" text beneath it
        if (city.id === homeCityIndex) {
            ctx.fillText("Home", city.x - 10, city.y + 20);  // Display "Home" beneath the home city
        }
    });

    // Handle drawing the paths (if any)
    const isGameOver = gameOver;
    if (document.getElementById("showHuman")?.checked && playerRoute.length > 1) {
        if (isGameOver) {
            drawPath([cities[homeCityIndex], ...playerRoute, cities[homeCityIndex]], "blue", false);
        } else {
            drawPath([cities[homeCityIndex], ...playerRoute], "blue", false);
        }
    }

    if (document.getElementById("showNN")?.checked && nnRoute.length > 1) {
        drawPath([cities[homeCityIndex], ...nnRoute], "green", true);
    }

    if (document.getElementById("showBF")?.checked && bfRoute.length > 1) {
        drawPath([cities[homeCityIndex], ...bfRoute], "purple", true);
    }

    if (document.getElementById("showHK")?.checked && hkRoute.length > 1) {
        drawPath([cities[homeCityIndex], ...hkRoute], "orange", true);
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
    humanDistanceInKm = humanDistanceInUnits / 10;  // Update the global variable with the calculated value

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

    // Prepare the cities array for backend: include home city and user-selected cities
    const homeCityObj = cities[homeCityIndex];  // This gives the full city object (A to J)
    const selectedCityIds = playerRoute.map(city => city.id);
    const selectedCities = cities.filter(city => selectedCityIds.includes(city.id));
    const citiesForBackend = [homeCityObj, ...selectedCities];

    // Map the selected city IDs to letters (A, B, C, ...)
    const selectedCityChars = selectedCities.map(city => String.fromCharCode(65 + city.id));  // A to J

    // Map the home city to a letter (A, B, C, ...)
    const homeCityChar = String.fromCharCode(65 + homeCityObj.id);  // Convert to A, B, C...

    // Log the selected cities for debugging
    console.log("Selected Cities for Algorithms (with home):", citiesForBackend);

    try {
        const requestData = {
            cities: citiesForBackend,  // Send home city + user-selected cities
            player_name: playerName,
            home_city: homeCityChar,  // Send the home city as a character (A, B, C, etc.)
            human_route: selectedCityChars  // Send the human route with city letters (A, B, C, etc.)
        };
        console.log("Data being sent to the backend:", requestData);

        // Make the API call to compare the algorithms
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
            // Defensive: check for missing data
            if (!data || !data.nearest_neighbor || !data.brute_force || !data.held_karp) {
                console.error('Missing algorithm results in response:', data);
                alert('Error: Missing algorithm results.');
                return;
            }

            // Process results and display them
            document.getElementById("toggles").style.display = "block";

            if (data.nearest_neighbor && !data.nearest_neighbor.error) {
                console.log("Nearest Neighbor result:", data.nearest_neighbor);
                nnRoute = JSON.parse(data.nearest_neighbor.route);  // Parse route if it's JSON
                document.getElementById("nnResult").innerText =
                    `Nearest Neighbor: ${data.nearest_neighbor.distance.toFixed(1)} km (Time: ${(data.nearest_neighbor.time * 1000).toFixed(2)} ms)`;
                document.getElementById("nnResult").style.display = "block";
                document.getElementById("showNN").checked = true;
            }

            if (data.brute_force && !data.brute_force.error) {
                console.log("Brute Force result:", data.brute_force);
                bfRoute = JSON.parse(data.brute_force.route);  // Parse route if it's JSON
                document.getElementById("bfResult").innerText =
                    `Brute Force: ${data.brute_force.distance.toFixed(1)} km (Time: ${(data.brute_force.time * 1000).toFixed(2)} ms)`;
                document.getElementById("bfResult").style.display = "block";
                document.getElementById("showBF").checked = true;
            }

            if (data.held_karp && !data.held_karp.error) {
                console.log("Held-Karp result:", data.held_karp);
                hkRoute = JSON.parse(data.held_karp.route);  // Parse route if it's JSON
                document.getElementById("hkResult").innerText =
                    `Held-Karp: ${data.held_karp.distance.toFixed(1)} km (Time: ${(data.held_karp.time * 1000).toFixed(2)} ms)`;
                document.getElementById("hkResult").style.display = "block";
                document.getElementById("showHK").checked = true;
            }

            // Now compare the human distance with the algorithm distances
            // Inside compareWithAlgorithms()
            const humanDistance = humanDistanceInKm.toFixed(1); // Get the updated human distance from the frontend
            const nnDistance = parseFloat(data.nearest_neighbor.distance).toFixed(1);
            const bfDistance = parseFloat(data.brute_force.distance).toFixed(1);
            const hkDistance = parseFloat(data.held_karp.distance).toFixed(1);

            // Display the values for comparison in a popup
            const comparisonMessage = `
                1. Human Distance: ${humanDistance} km
                2. Nearest Neighbor Distance: ${nnDistance} km
                3. Brute Force Distance: ${bfDistance} km
                4. Held-Karp Distance: ${hkDistance} km
            `;
            alert(comparisonMessage); // Show the comparison in a popup

            // Fix comparison logic: Human route should only be considered as the best if it's shorter or equal
            let resultMessage = "";
            if (humanDistance <= nnDistance && humanDistance <= bfDistance && humanDistance <= hkDistance) {
                if (humanDistance < nnDistance || humanDistance < bfDistance || humanDistance < hkDistance) {
                    resultMessage = "Congratulations! You found the shortest route!";
                    saveWinToDatabase(data, humanDistance, selectedCityChars); // Trigger saving win data
                } else {
                    resultMessage = "Congratulations! You matched the best algorithm route!";
                    // Save the win data when the human matches or finds the best algorithm route
                    saveWinToDatabase(data, humanDistance, selectedCityChars); // Trigger saving win data
                }
            } else {
                resultMessage = "Nice try! The algorithm found a shorter route.";
                saveGameSessionToDatabase(data, selectedCityChars);  // Save the session after the comparison
            }

            // Display the result message
            document.getElementById("resultMessage").innerText = resultMessage;

            drawCities();  // Redraw the cities with the updated routes

            // Record the game session after the algorithms are compared
            
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

// Update initial load to add database viewer link
window.onload = function() {
    console.log("Generating cities...");
    generateCities();
    addDatabaseViewerLink();
}

function viewCityDistances() {
    if (!cities || cities.length < 2) {
        alert("No cities available to show distances.");
        return;
    }

    // Send current canvas cities to the backend
    fetch('http://127.0.0.1:5000/api/get_city_distances_from_existing', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ cities }), // Send current canvas city data
    })
    .then(response => response.json())
    .then(data => {
        const distances = data.distances;
        const coordinates = data.coordinates;

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
                    const dist = distances[i][j]?.toFixed(2) || "N/A";
                    html += `<td>${dist} km</td>`;
                }
            }
            html += "</tr>";
        }

        html += "</table>";
        tableDiv.innerHTML = html;
        document.getElementById('statsResult').style.display = 'block';
    })
    .catch(error => {
        console.error("Error fetching distances:", error);
        document.getElementById('statsContent').innerHTML =
            '<p class="error">Error loading statistics. Check console for details.</p>';
        document.getElementById('statsResult').style.display = 'block';
    });
}
