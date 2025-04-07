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

const cityRadius = 8;
const numCities = 6;

// Generate random cities
function generateCities() {
    cities = [];
    playerRoute = [];
    nnRoute = [];
    bfRoute = [];
    hkRoute = [];
    
    const margin = 20;
    const maxWidth = canvas.width - margin * 2;
    const maxHeight = canvas.height - margin * 2;
    
    for (let i = 0; i < numCities; i++) {
        const x = Math.random() * maxWidth + margin;
        const y = Math.random() * maxHeight + margin;
        
        cities.push({
            x: Math.min(Math.max(x, margin), canvas.width - margin),
            y: Math.min(Math.max(y, margin), canvas.height - margin),
            id: i
        });
    }

    // Reset UI elements
    document.getElementById("humanResult").innerText = "Human Distance: N/A";
    document.getElementById("nnResult").style.display = "none";
    document.getElementById("bfResult").style.display = "none";
    document.getElementById("hkResult").style.display = "none";
    document.getElementById("toggles").style.display = "none";
    
    drawCities();
}

function drawCities() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw cities
    cities.forEach(city => {
        ctx.beginPath();
        ctx.arc(city.x, city.y, cityRadius, 0, Math.PI * 2);
        ctx.fillStyle = "#ff4136";
        ctx.fill();
        ctx.stroke();
        ctx.fillStyle = "black";
        ctx.fillText(`C${city.id}`, city.x + 10, city.y);
    });

    // Draw routes based on toggles
    if (document.getElementById("showHuman")?.checked && playerRoute.length > 1) {
        drawPath(playerRoute, "blue", false); // false = don't close loop yet
    }

    if (document.getElementById("showNN")?.checked && nnRoute.length > 1) {
        drawPath(nnRoute, "green", true); // true = close loop
    }

    if (document.getElementById("showBF")?.checked && bfRoute.length > 1) {
        drawPath(bfRoute, "purple", true); // true = close loop
    }

    if (document.getElementById("showHK")?.checked && hkRoute.length > 1) {
        drawPath(hkRoute, "orange", true); // true = close loop
    }
}

// Updated drawPath with optional loop closure
function drawPath(route, color, closeLoop = false) {
    if (!route || route.length < 2) return;
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


canvas.addEventListener("click", (event) => {
    const rect = canvas.getBoundingClientRect();
    const mouseX = event.clientX - rect.left;
    const mouseY = event.clientY - rect.top;

    for (let city of cities) {
        const dx = city.x - mouseX;
        const dy = city.y - mouseY;
        if (Math.sqrt(dx * dx + dy * dy) < cityRadius * 2) {
            if (!playerRoute.includes(city)) {
                if (playerRoute.length < numCities) {
                    playerRoute.push(city);
                    drawCities();
                } else {
                    alert("You've already selected all cities!");
                }
            }
            break;
        }
    }
});

function getDistance(a, b) {
    return Math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2);
}

function calculateTotalDistance(route) {
    let dist = 0;
    for (let i = 0; i < route.length - 1; i++) {
        dist += getDistance(route[i], route[i + 1]);
    }
    return dist;
}

function submitRoute() {
    if (playerRoute.length < numCities) {
        alert("Please visit all cities!");
        return;
    }

    // Close loop
    playerRoute.push(playerRoute[0]);
    const humanDistance = calculateTotalDistance(playerRoute);

    document.getElementById("humanResult").innerText =
        `Human Distance: ${humanDistance.toFixed(2)} units`;

    // Hide algorithm results until "Compare" is clicked
    document.getElementById("nnResult").style.display = "none";
    document.getElementById("bfResult").style.display = "none";
    document.getElementById("toggles").style.display = "none";

    drawCities();
}

function compareWithAlgorithms() {
    if (playerRoute.length < numCities + 1) {
        alert("Please submit your route first!");
        return;
    }

    try {
        console.log('Making API call with cities:', cities);
        // Updated API endpoint URL
        fetch('http://127.0.0.1:5000/api/solve_tsp', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ cities: cities })
        })
        .then(response => {
            console.log('Response status:', response.status);
            return response.json().catch(err => {
                console.error('Error parsing JSON:', err);
                throw new Error('Failed to parse response');
            });
        })
        .then(data => {
            console.log('Received data:', data);
            
            // Nearest Neighbour
            nnRoute = data.nearest_neighbor.route;
            const nnDist = data.nearest_neighbor.distance;
            console.log('NN Route:', nnRoute);
            document.getElementById("nnResult").innerText =
                `Nearest Neighbour Distance: ${nnDist.toFixed(2)} units`;
            document.getElementById("nnResult").style.display = "block";

            // Brute Force
            if (cities.length <= 7) {
                bfRoute = data.brute_force.route;
                const bfDist = data.brute_force.distance;
                console.log('BF Route:', bfRoute);
                document.getElementById("bfResult").innerText =
                    `Brute Force Distance: ${bfDist.toFixed(2)} units`;
                document.getElementById("bfResult").style.display = "block";
            }

            // Held-Karp
            hkRoute = data.held_karp.route;
            const hkDist = data.held_karp.distance;
            console.log('HK Route:', hkRoute);
            document.getElementById("hkResult").innerText =
                `Held-Karp Distance: ${hkDist.toFixed(2)} units`;
            document.getElementById("hkResult").style.display = "block";

            document.getElementById("toggles").style.display = "block";
            drawCities();
        })
        .catch(error => {
            console.error("Error in API call:", error);
            console.error("Error stack:", error.stack);
            alert("An error occurred while comparing routes. Check console for details.");
        });
    } catch (error) {
        console.error("Error in compareWithAlgorithms:", error);
        console.error("Error stack:", error.stack);
        alert("An error occurred while comparing routes. Check console for details.");
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

function resetGame() {
    playerRoute = [];
    nnRoute = [];
    bfRoute = [];
    hkRoute = [];

    document.getElementById("humanResult").innerText = "Human Distance: N/A";
    document.getElementById("nnResult").style.display = "none";
    document.getElementById("bfResult").style.display = "none";
    document.getElementById("hkResult").style.display = "none";

    // Reset checkboxes with correct IDs
    document.getElementById("showHuman").checked = true;
    document.getElementById("showNN").checked = false;
    document.getElementById("showBF").checked = false;
    document.getElementById("showHK").checked = false;

    generateCities();
}


// Initial Load
generateCities();
