const canvas = document.getElementById("cityCanvas");
const ctx = canvas.getContext("2d");

let gameOver = false;
if (!ctx) {
    console.error("Canvas context not available");
    alert("Your browser doesn't support canvas operations!");
}

let cities = [];
let playerRoute = [];
let nnRoute = [];
let bbRoute = [];
let hkRoute = [];
let distanceMatrix = {};
let playerPathSegments = [];

let playerName = "Anonymous";
let homeCity = "Unknown";

const cityRadius = 8;
const numCities = 10;
let humanDistanceInKm = 0;
let homeCityIndex = Math.floor(Math.random() * numCities);

// Track path visibility for each card
const pathVisible = {
    human: true, // Human path visible by default
    nn: false,
    bb: false,
    hk: false
};

function getHomeChar() {
    return String.fromCharCode(65 + homeCityIndex);
}

function generateCities() {
    playerRoute = [];
    nnRoute = [];
    bbRoute = [];
    hkRoute = [];
    playerPathSegments = [];
    firstPathDrawn = false;
    gameOver = false;

    // Reset path visibility
    pathVisible.human = true;
    pathVisible.nn = false;
    pathVisible.bb = false;
    pathVisible.hk = false;

    fetch('http://127.0.0.1:5000/api/get_city_distances')
        .then(res => res.json())
        .then(data => {
            if (!data || !data.cities || !data.distances) {
                console.error("Invalid city data:", data);
                return;
            }

            cities = data.cities;
            distanceMatrix = data.distances;

            const padding = 100;
            const maxRadius = Math.min(canvas.width, canvas.height) / 2 - 30;
            const centerX = canvas.width / 2;
            const centerY = canvas.height / 2;
            const minDistance = 120;

            cities.forEach((city, index) => {
                let validPosition = false;
                while (!validPosition) {
                    const angle = Math.random() * 2 * Math.PI;
                    const radius = Math.random() * maxRadius;
                    const x = centerX + radius * Math.cos(angle);
                    const y = centerY + radius * Math.sin(angle);
                    let tooClose = cities.some(other =>
                        other.x !== undefined &&
                        Math.hypot(other.x - x, other.y - y) < minDistance
                    );
                    if (!tooClose) {
                        city.x = x;
                        city.y = y;
                        validPosition = true;
                    }
                }
            });

            homeCityIndex = Math.floor(Math.random() * cities.length);
            const homeCityElement = document.getElementById("homeCity");
            if (homeCityElement) {
                homeCityElement.innerText =
                    `Home City: City ${String.fromCharCode(65 + homeCityIndex)}`;
            } else {
                console.warn("Element with ID 'homeCity' not found in DOM");
            }

            // Reset UI elements for card layout
            const humanDistanceElement = document.getElementById("humanDistance");
            if (humanDistanceElement) {
                humanDistanceElement.innerText = "N/A";
                humanDistanceElement.style.display = "inline";
            } else {
                console.warn("Element with ID 'humanDistance' not found in DOM");
            }
            const nnDistanceElement = document.getElementById("nnDistance");
            const bbDistanceElement = document.getElementById("bbDistance");
            const hkDistanceElement = document.getElementById("hkDistance");
            if (nnDistanceElement) {
                nnDistanceElement.innerText = "N/A";
                nnDistanceElement.style.display = "inline";
            }
            if (bbDistanceElement) {
                bbDistanceElement.innerText = "N/A";
                bbDistanceElement.style.display = "inline";
            }
            if (hkDistanceElement) {
                hkDistanceElement.innerText = "N/A";
                hkDistanceElement.style.display = "inline";
            }
            const nnCard = document.getElementById("nnCard");
            const bbCard = document.getElementById("bbCard");
            const hkCard = document.getElementById("hkCard");
            if (nnCard) nnCard.classList.add("hidden-result");
            if (bbCard) bbCard.classList.add("hidden-result");
            if (hkCard) hkCard.classList.add("hidden-result");

            // Reset card active states
            document.getElementById("humanCard").classList.add("path-active");
            document.getElementById("nnCard").classList.remove("path-active");
            document.getElementById("bbCard").classList.remove("path-active");
            document.getElementById("hkCard").classList.remove("path-active");

            drawCities();
        })
        .catch(err => {
            console.error("Error generating cities:", err);
            alert("Failed to load city data. Please try again.");
        });
}

function getCityChar(cityId) {
    return String.fromCharCode(65 + cityId);
}

function collectPlayerInfo() {
    playerName = prompt("Please enter your name:", "Anonymous");
    if (!playerName) playerName = "Anonymous";
}

function drawCities() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    ctx.save();
    ctx.strokeStyle = 'rgba(150, 150, 150, 0.37)';
    ctx.setLineDash([4, 6]);

    for (let i = 0; i < cities.length; i++) {
        for (let j = i + 1; j < cities.length; j++) {
            const cityA = cities[i];
            const cityB = cities[j];

            ctx.beginPath();
            ctx.moveTo(cityA.x, cityA.y);
            ctx.lineTo(cityB.x, cityB.y);
            ctx.stroke();
        }
    }

    ctx.setLineDash([]);
    ctx.restore();

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

    if (pathVisible.nn && nnRoute.length > 1) {
        drawPath([cities[homeCityIndex], ...nnRoute, cities[homeCityIndex]], "green", true);
    }
    if (pathVisible.bb && bbRoute.length > 1) {
        drawPath([cities[homeCityIndex], ...bbRoute, cities[homeCityIndex]], "purple", true);
    }
    if (pathVisible.hk && hkRoute.length > 1) {
        drawPath([cities[homeCityIndex], ...hkRoute, cities[homeCityIndex]], "orange", true);
    }
    if (pathVisible.human) {
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
    console.log(`Drawing path from ${route[0].id} to ${route[1].id}`);

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

let firstPathDrawn = false;

canvas.addEventListener("click", (event) => {
    if (gameOver) return;

    const rect = canvas.getBoundingClientRect();
    const mouseX = event.clientX - rect.left;
    const mouseY = event.clientY - rect.top;

    for (let city of cities) {
        const dx = city.x - mouseX;
        const dy = city.y - mouseY;
        if (Math.sqrt(dx * dx + dy * dy) < cityRadius * 2) {
            console.log(`Clicked on city with id: ${city.id}`);

            if (city.id === homeCityIndex) {
                console.log("Home city clicked, submitting route.");
                submitRoute();
                return;
            }

            if (playerRoute.length === 0 && !firstPathDrawn) {
                console.log(`First city clicked: Drawing path from home city (id: ${homeCityIndex}) to city ${city.id}`);

                if (cities[homeCityIndex] && city) {
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                    drawCities();
                    playerPathSegments.push({ from: cities[homeCityIndex], to: city });
                    playerRoute.push(city);
                    firstPathDrawn = true;
                    
                    drawCities();
                    
                    console.log(`City ${city.id} added to player route.`);
                    return;
                }
            }

            if (!playerRoute.includes(city)) {
                playerRoute.push(city);
                console.log(`City ${city.id} added to player route.`);
                if (playerRoute.length > 1) {
                    console.log(`Drawing path from city ${playerRoute[playerRoute.length - 2].id} to city ${playerRoute[playerRoute.length - 1].id}`);
                    const from = playerRoute[playerRoute.length - 2];
                    const to = playerRoute[playerRoute.length - 1];
                    playerPathSegments.push({ from, to });
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

function submitRoute() {
    if (playerRoute.length < 1) {
        alert("Please visit at least one city!");
        return;
    }

    const fullHumanRoute = [cities[homeCityIndex], ...playerRoute, cities[homeCityIndex]];

    if (playerRoute.length > 0) {
        drawPath([playerRoute[playerRoute.length - 1], cities[homeCityIndex]], "blue", false);
    }
    const from = playerRoute[playerRoute.length - 1];
    const to = cities[homeCityIndex];
    playerPathSegments.push({ from, to });

    const humanDistanceInUnits = calculateTotalDistance(fullHumanRoute);
    humanDistanceInKm = humanDistanceInUnits;

    console.log(`Full Human Route: `, fullHumanRoute);
    console.log(`Human Distance: `, humanDistanceInKm);

    const humanDistanceElement = document.getElementById("humanDistance");
    if (humanDistanceElement) {
        humanDistanceElement.innerText = `${humanDistanceInKm.toFixed(1)} km`;
        humanDistanceElement.style.display = "inline";
    } else {
        console.warn("Element with ID 'humanDistance' not found in DOM");
    }

    const nnCard = document.getElementById("nnCard");
    const bbCard = document.getElementById("bbCard");
    const hkCard = document.getElementById("hkCard");
    if (nnCard) nnCard.classList.add("hidden-result");
    if (bbCard) bbCard.classList.add("hidden-result");
    if (hkCard) hkCard.classList.add("hidden-result");

    stopGame();

    drawCities();
}

function compareWithAlgorithms() {
    console.log("Compare with Algorithms clicked");
    submitRoute();
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
        console.log("API response:", data);
        const idToCity = (c) => typeof c === 'object' ? cities.find(city => city.id === c.id) : cities.find(city => city.id === c);

        if (data.nearest_neighbor && !data.nearest_neighbor.error) {
            nnRoute = data.nearest_neighbor.route.map(idToCity);
            const nnDistanceElement = document.getElementById("nnDistance");
            const nnTimeElement = document.getElementById("nnTime");
            const nnCard = document.getElementById("nnCard");
            const nnDistance = data.nearest_neighbor.distance;
            console.log("NN Distance:", nnDistance);
            if (nnDistanceElement) {
                nnDistanceElement.innerText = nnDistance != null && !isNaN(nnDistance) ? `${parseFloat(nnDistance).toFixed(1)} km` : "N/A";
                nnDistanceElement.style.display = "inline";
            }
            if (nnTimeElement) {
                nnTimeElement.innerText = data.nearest_neighbor.time != null ? `${data.nearest_neighbor.time.toFixed(3)} s` : "N/A";
                nnTimeElement.style.display = "inline";
            }
            if (nnCard) {
                nnCard.classList.remove("hidden-result");
                pathVisible.nn = true;
                nnCard.classList.add("path-active");
            }
        }

        if (data.branch_bound && !data.branch_bound.error) {
            bbRoute = data.branch_bound.route.map(idToCity);
            const bbDistanceElement = document.getElementById("bbDistance");
            const bbTimeElement = document.getElementById("bbTime");
            const bbCard = document.getElementById("bbCard");
            const bbDistance = data.branch_bound.distance;
            console.log("BB Distance:", bbDistance);
            if (bbDistanceElement) {
                bbDistanceElement.innerText = bbDistance != null && !isNaN(bbDistance) ? `${parseFloat(bbDistance).toFixed(1)} km` : "N/A";
                bbDistanceElement.style.display = "inline";
            }
            if (bbTimeElement) {
                bbTimeElement.innerText = data.branch_bound.time != null ? `${data.branch_bound.time.toFixed(3)} s` : "N/A";
                bbTimeElement.style.display = "inline";
            }
            if (bbCard) {
                bbCard.classList.remove("hidden-result");
                pathVisible.bb = true;
                bbCard.classList.add("path-active");
            }
        }

        if (data.held_karp && !data.held_karp.error) {
            hkRoute = data.held_karp.route.map(idToCity);
            const hkDistanceElement = document.getElementById("hkDistance");
            const hkTimeElement = document.getElementById("hkTime");
            const hkCard = document.getElementById("hkCard");
            const hkDistance = data.held_karp.distance;
            console.log("HK Distance:", hkDistance);
            if (hkDistanceElement) {
                hkDistanceElement.innerText = hkDistance != null && !isNaN(hkDistance) ? `${parseFloat(hkDistance).toFixed(1)} km` : "N/A";
                hkDistanceElement.style.display = "inline";
            }
            if (hkTimeElement) {
                hkTimeElement.innerText = data.held_karp.time != null ? `${data.held_karp.time.toFixed(3)} s` : "N/A";
                hkTimeElement.style.display = "inline";
            }
            if (hkCard) {
                hkCard.classList.remove("hidden-result");
                pathVisible.hk = true;
                hkCard.classList.add("path-active");
            }
        }

        const humanDistance = humanDistanceInKm.toFixed(1);
        const nnDistance = data.nearest_neighbor.distance != null ? parseFloat(data.nearest_neighbor.distance).toFixed(1) : "N/A";
        const bbDistance = data.branch_bound.distance != null ? parseFloat(data.branch_bound.distance).toFixed(1) : "N/A";
        const hkDistance = data.held_karp.distance != null ? parseFloat(data.held_karp.distance).toFixed(1) : "N/A";

        let resultMessage = "";
        if (humanDistance <= nnDistance && humanDistance <= bbDistance && humanDistance <= hkDistance) {
            resultMessage = humanDistance < nnDistance || humanDistance < bbDistance || humanDistance < hkDistance
                ? "Congratulations! You found the shortest route!"
                : "Congratulations! You matched the best algorithm route!";
            saveWinToDatabase(data, humanDistance, selectedCityChars);
        } else {
            resultMessage = "Nice try! The algorithm found a shorter route.";
            saveGameSessionToDatabase(data, selectedCityChars);
        }

        // Display the result in the modal
        const resultModalMessage = document.getElementById("resultModalMessage");
        const resultModal = document.getElementById("resultModal");
        if (resultModalMessage && resultModal) {
            resultModalMessage.innerText = resultMessage;
            resultModal.style.display = "flex";
        } else {
            console.warn("Modal elements not found in DOM");
        }

        drawCities();
    })
    .catch(error => {
        console.error('Error during algorithm comparison:', error);
        alert('Error comparing algorithms. Check the console for more details.');
    });
}

function toCharRoute(route) {
    return [
        String.fromCharCode(65 + homeCityIndex),
        ...route.map(c => String.fromCharCode(65 + c.id)),
        String.fromCharCode(65 + homeCityIndex)
    ];
}

function saveGameSessionToDatabase(data, selectedCityIds) {
    const requestData = {
        player_name: playerName,
        home_city: getHomeChar(),
        selected_cities: selectedCityIds,
        nn_distance: data.nearest_neighbor.distance,
        bb_distance: data.branch_bound.distance,
        hk_distance: data.held_karp.distance,
        nn_time: data.nearest_neighbor.time,
        bb_time: data.branch_bound.time,
        hk_time: data.held_karp.time,
        nn_route: data.nearest_neighbor.route.map(c => String.fromCharCode(65 + c.id)),
        bb_route: data.branch_bound.route.map(c => String.fromCharCode(65 + c.id)),
        hk_route: data.held_karp.route.map(c => String.fromCharCode(65 + c.id)),
    };

    fetch('http://127.0.0.1:5000/api/save_game_session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
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

function saveWinToDatabase(data, humanDistance, humanRoute) {
    const requestData = {
        session_id: data.session_id,
        player_name: playerName,
        selected_cities: humanRoute,
        home_city: getHomeChar(),
        human_route: [getHomeChar(), ...humanRoute, getHomeChar()],
        human_distance: humanDistance,
        nn_distance: data.nearest_neighbor.distance,
        bb_distance: data.branch_bound.distance,
        hk_distance: data.held_karp.distance,
        nn_time: data.nearest_neighbor.time,
        bb_time: data.branch_bound.time,
        hk_time: data.held_karp.time,
        nn_route: data.nearest_neighbor.route.map(c => String.fromCharCode(65 + c.id)),
        bb_route: data.branch_bound.route.map(c => String.fromCharCode(65 + c.id)),
        hk_route: data.held_karp.route.map(c => String.fromCharCode(65 + c.id)),
    };

    fetch('http://127.0.0.1:5000/api/save_win', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
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

function permute(arr) {
    if (arr.length === 0) return [[]];
    return arr.flatMap((v, i) =>
        permute([...arr.slice(0, i), ...arr.slice(i + 1)]).map(p => [v, ...p])
    );
}

function resetGame() {
    playerName = prompt("Please enter your name:", playerName) || playerName;

    gameOver = false;
    playerRoute = [];
    nnRoute = [];
    bbRoute = [];
    hkRoute = [];
    playerPathSegments = [];
    firstPathDrawn = false;
    humanDistanceInKm = 0;

    // Reset path visibility
    pathVisible.human = true;
    pathVisible.nn = false;
    pathVisible.bb = false;
    pathVisible.hk = false;

    // Reset UI elements
    const humanDistanceElement = document.getElementById("humanDistance");
    const nnDistanceElement = document.getElementById("nnDistance");
    const nnTimeElement = document.getElementById("nnTime");
    const bbDistanceElement = document.getElementById("bbDistance");
    const bbTimeElement = document.getElementById("bbTime");
    const hkDistanceElement = document.getElementById("hkDistance");
    const hkTimeElement = document.getElementById("hkTime");
    if (humanDistanceElement) {
        humanDistanceElement.innerText = "N/A";
        humanDistanceElement.style.display = "inline";
    }
    if (nnDistanceElement) {
        nnDistanceElement.innerText = "N/A";
        nnDistanceElement.style.display = "inline";
    }
    if (nnTimeElement) {
        nnTimeElement.innerText = "N/A";
        nnTimeElement.style.display = "inline";
    }
    if (bbDistanceElement) {
        bbDistanceElement.innerText = "N/A";
        bbDistanceElement.style.display = "inline";
    }
    if (bbTimeElement) {
        bbTimeElement.innerText = "N/A";
        bbTimeElement.style.display = "inline";
    }
    if (hkDistanceElement) {
        hkDistanceElement.innerText = "N/A";
        hkDistanceElement.style.display = "inline";
    }
    if (hkTimeElement) {
        hkTimeElement.innerText = "N/A";
        hkTimeElement.style.display = "inline";
    }

    // Hide the modal if it's open
    const resultModal = document.getElementById("resultModal");
    if (resultModal) resultModal.style.display = "none";

    // Reset card active states
    const humanCard = document.getElementById("humanCard");
    const nnCard = document.getElementById("nnCard");
    const bbCard = document.getElementById("bbCard");
    const hkCard = document.getElementById("hkCard");
    if (humanCard) humanCard.classList.add("path-active");
    if (nnCard) {
        nnCard.classList.remove("path-active");
        nnCard.classList.add("hidden-result");
    }
    if (bbCard) {
        bbCard.classList.remove("path-active");
        bbCard.classList.add("hidden-result");
    }
    if (hkCard) {
        hkCard.classList.remove("path-active");
        hkCard.classList.add("hidden-result");
    }

    setTimeout(generateCities, 50);
}

function stopGame() {
    gameOver = true;
    const humanDistanceElement = document.getElementById("humanDistance");
    if (humanDistanceElement && !humanDistanceElement.innerText.includes("(Game Over)")) {
        humanDistanceElement.innerText += " (Game Over)";
        humanDistanceElement.style.display = "inline";
    }
}

function setupModalListeners() {
    const closeModalBtn = document.getElementById("closeModal");
    const resultModal = document.getElementById("resultModal");
    if (closeModalBtn && resultModal) {
        closeModalBtn.addEventListener("click", () => {
            resultModal.style.display = "none";
        });
    } else {
        console.warn("Modal close button or modal not found in DOM");
    }
}

function addDatabaseViewerLink() {
    const link = document.createElement('a');
    link.href = 'http://127.0.0.1:5000/api/db_viewer';
    link.target = '_blank';
    link.innerText = 'View Database Contents';
    link.style.display = 'block';
    link.style.marginTop = '20px';
    link.style.textAlign = 'center';
    link.style.textDecoration = 'underline';
    link.style.color = '#007bff';
    const content = document.getElementById('content');
    if (content) {
        content.appendChild(link);
    } else {
        console.warn("Element with ID 'content' not found, appending link to body");
        document.body.appendChild(link);
    }
}

// Add click event listeners for cards
function setupCardListeners() {
    const cards = [
        { id: "humanCard", key: "human" },
        { id: "nnCard", key: "nn" },
        { id: "bbCard", key: "bb" },
        { id: "hkCard", key: "hk" }
    ];

    cards.forEach(({ id, key }) => {
        const card = document.getElementById(id);
        if (card) {
            card.addEventListener("click", () => {
                // Toggle path visibility only if card is not hidden
                if (!card.classList.contains("hidden-result")) {
                    pathVisible[key] = !pathVisible[key];
                    if (pathVisible[key]) {
                        card.classList.add("path-active");
                    } else {
                        card.classList.remove("path-active");
                    }
                    drawCities();
                }
            });
        }
    });
}


function viewAlgorithmStats() {
    window.open('tsp_assets/algorithm_stats.html', '_blank');
}

document.addEventListener("DOMContentLoaded", () => {
    console.log("DOM fully loaded. Initializing game...");
    playerName = prompt("Please enter your name:", "Anonymous") || "Anonymous";
    generateCities();
    addDatabaseViewerLink();
    setupCardListeners();
    setupModalListeners();
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
    const statsResult = document.getElementById('statsResult');
    if (statsResult) statsResult.style.display = 'block';
}