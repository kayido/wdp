// ==================== Constants ====================
const MAP_CENTER = [48.7904, 2.4606];
const TILE_URL = 'https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png';
const TILE_OPTS = { attribution: '&copy; OpenStreetMap contributors', maxZoom: 18 };

// const icon = L.icon({
//     iconUrl: "https://img.icons8.com/color/48/high-priority.png",
//     iconSize: [32, 32], iconAnchor: [16, 32], popupAnchor: [0, -28]
// });

const icon = L.icon({
    iconUrl: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Cpolygon points='16,4 2,28 30,28' fill='%23FFD700' stroke='%23B8860B' stroke-width='1.5' /%3E%3Ctext x='16' y='24' font-size='20' text-anchor='middle' fill='%238B5A00' font-weight='bold'%3E!%3C/text%3E%3C/svg%3E",
    iconSize: [32, 32], iconAnchor: [16, 32], popupAnchor: [0, -28]
});



const redalert = L.icon({
    iconUrl: "https://img.icons8.com/clouds/100/empty-trash.png",
    iconSize: [32, 32], iconAnchor: [16, 32], popupAnchor: [0, -28]
});

// ==================== Map singletons ====================
let mainMap = null;
let riskMap = null;

// ==================== Helpers ====================

function createZoneItem(labelText, countText) {
    const item = document.createElement("div");
    item.classList.add("zone-item", "risk-high");

    const dot = document.createElement("span");
    dot.classList.add("dot", "risk-high");

    const label = document.createElement("span");
    label.classList.add("zone-label");
    label.textContent = labelText;

    const count = document.createElement("span");
    count.classList.add("zone-count");
    count.textContent = String(countText);

    item.append(dot, label, count);
    return item;
}

async function getLieu(lat, lon) {
    try {
        const res = await fetch(
            `https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${lat}&lon=${lon}`
        );
        const data = await res.json();
        return data.display_name || "Lieu inconnu";
    } catch {
        return "Erreur lors de la recherche du lieu";
    }
}

function formatPlace(lieu) {
    const parts = lieu.split(",");
    return [parts[0], parts[1], parts[parts.length - 2], parts[parts.length - 1]]
        .filter(Boolean)
        .join(", ");
}

function updateDetailsCard(place, occur) {
    document.querySelector(".details-card").innerHTML =
        `<b>Lieu :</b> ${place}<br><b>Nombre de signalements :</b> ${occur}`;
}

async function fetchJSON(url) {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`Erreur réseau: ${res.status}`);
    return res.json();
}

function showMap(activeId, hiddenId) {
    document.getElementById(activeId).style.display = "block";
    document.getElementById(hiddenId).style.display = "none";
}

// ==================== Markers ====================

function addMarkers(points, targetMap, markerIcon) {
    points.forEach(([lat, lng, occur]) => {
        const marker = L.marker([lat, lng], { icon: markerIcon }).addTo(targetMap);
        marker.on("click", async () => {
            marker.bindPopup("Chargement des infos...").openPopup();
            const lieu = await getLieu(lat, lng);
            marker.setPopupContent(
                `<b>Coordonnées :</b> ${lat.toFixed(5)}, ${lng.toFixed(5)}<br>` +
                `<b>Lieu :</b> ${lieu}`
            );
            updateDetailsCard(formatPlace(lieu), occur);
        });
    });
}

// ==================== Map init ====================

async function initCart() {
    showMap("map", "map2");
    if (mainMap) return mainMap;

    mainMap = L.map("map").setView(MAP_CENTER, 12);
    L.tileLayer(TILE_URL, TILE_OPTS).addTo(mainMap);

    const data = await fetchJSON("/signalements_items/");
    const points = data.map(({ lat, long, occur }) => [lat, long, occur]);
    addMarkers(points, mainMap, redalert);
    return mainMap;
}

async function CartographierZoneRisque() {
    showMap("map2", "map");
    if (riskMap) return riskMap;

    riskMap = L.map("map2").setView(MAP_CENTER, 12);
    L.tileLayer(TILE_URL, TILE_OPTS).addTo(riskMap);

    const data = await fetchJSON("/zone_5/");
    const points = data.map(({ lat, long, occur }) => [lat, long, occur]);
    addMarkers(points, riskMap, redalert);
    return riskMap;
}

// ==================== Sidebar lists ====================

async function loadZonesRisques() {
    const data = await fetchJSON("/getZones/");
    const zoneList = document.querySelector(".zonesRisques-list");
    const points = data.map(({ libelle, latitude, longitude, Adresse, occur, date_fin }) => {
        zoneList.appendChild(
            createZoneItem(`${libelle} à ${Adresse} jusqu'au ${date_fin}`, occur)
        );
        return [latitude, longitude, occur];
    });
    addMarkers(points, mainMap, icon);
}

async function loadZone5List() {
    const data = await fetchJSON("/zone_5/");
    const zoneList = document.querySelector(".zones-list");
    data.forEach(({ adresse, occur }) => {
        zoneList.appendChild(createZoneItem(adresse, occur));
    });
}

// ==================== Bootstrap ====================

(async function init() {
    try {
        await initCart();
        await Promise.all([loadZonesRisques(), loadZone5List()]);
    } catch (err) {
        console.error("Erreur d'initialisation:", err);
    }

    document.getElementById("allzone").addEventListener("click", initCart);
    document.getElementById("rh").addEventListener("click", CartographierZoneRisque);
})();