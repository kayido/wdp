fetch(`/getZones/`)
.then(res => res.json())
.then(data => {
    console.log(data)
    let points = []
    let occurs = []
    let zone_list = document.querySelector(".zonesRisques-list");
    data.forEach(({ libelle, latitude, longitude, Adresse, occur, date_fin}) => {
      points.push([latitude, longitude]);
      occurs.push([latitude, longitude])


      let zone_item = document.createElement("div");
        zone_item.classList.add("zone-item", "risk-high");

        let zone_span = document.createElement("span");
        zone_span.classList.add("dot", "risk-high");

        let zone_span2 = document.createElement("span");
        zone_span2.classList.add("zone-label");
        zone_span2.textContent = libelle+ " à "+Adresse + " jusqu'au "+ date_fin;

        let zone_span3 = document.createElement("span");
        zone_span3.classList.add("zone-count");
        zone_span3.innerText = occur;

        zone_item.appendChild(zone_span);
        zone_item.appendChild(zone_span2);
        zone_item.appendChild(zone_span3);

        zone_list.appendChild(zone_item);
    });
    mapper(occurs)
    
})


fetch(`/zone_5/`)
.then(res => res.json())
.then(data => {
    console.log(data)
    let zone_list = document.querySelector(".zones-list");
    data.forEach(({ lat, long, occur, adresse }) => {
        let zone_item = document.createElement("div");
        zone_item.classList.add("zone-item", "risk-high");

        let zone_span = document.createElement("span");
        zone_span.classList.add("dot", "risk-high");

        let zone_span2 = document.createElement("span");
        zone_span2.classList.add("zone-label");
        zone_span2.textContent = adresse;

        let zone_span3 = document.createElement("span");
        zone_span3.classList.add("zone-count");
        zone_span3.innerText = occur;

        zone_item.appendChild(zone_span);
        zone_item.appendChild(zone_span2);
        zone_item.appendChild(zone_span3);

        zone_list.appendChild(zone_item);
    });
    
    
})


// Icône personnalisée simple
const icon = L.icon({
    iconUrl: "https://img.icons8.com/color/48/high-priority.png",
    iconSize: [32,32],
    iconAnchor: [16,32],
    popupAnchor: [0,-28]
});

const redalert = L.icon({
    iconUrl: "https://img.icons8.com/clouds/100/empty-trash.png",
    iconSize: [32,32],
    iconAnchor: [16,32],
    popupAnchor: [0,-28]
});

function initCart(){
    
    document.getElementById("map").style.display = "none" ? "block" : "none";
    document.getElementById("map2").style.display = "block" ? "none" : "block";

    const map = L.map('map').setView([48.7904, 2.4606], 12);
    
    L.tileLayer('https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors',
        maxZoom: 18
    }).addTo(map);

        
    fetch(`/signalements_items/`)
    .then(res => res.json())
    .then(data => {
        // console.log(data)
        let points = []
        let occurs = []
        data.forEach(({ lat, long, occur }) => {
            points.push([lat, long]);
            occurs.push([lat, long, occur])
        });
        mapperRed(occurs, map)
    })
    return map

}
// Carte centrée sur Val-de-Marne
const map = initCart()
document.getElementById("allzone").addEventListener("click", initCart)


// Fonction de reverse geocoding avec Nominatim
function getLieu(lat, lon, callback) {
    fetch(`https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${lat}&lon=${lon}`)
        .then(r => r.json())
        .then(data => {
            let name = data.display_name || "Lieu inconnu";
            callback(name);
        })
        .catch(() => callback("Erreur lors de la recherche du lieu"));
}

// Ajout des points sur la carte
function mapper(points){
    points.forEach(mt => {
        const pt = [mt[0], mt[1]]
     
        const marker = L.marker(pt, {icon}).addTo(map);
        marker.on('click', function() {
        marker.bindPopup("Chargement des infos...").openPopup();
        getLieu(pt[0], pt[1], function(lieu) {
            marker.setPopupContent(
                `<b>Coordonnées :</b> ${pt[0].toFixed(5)}, ${pt[1].toFixed(5)}<br>` +
                `<b>Lieu :</b> ${lieu}`
            );
            let block_lieu = lieu.split(",")
            let place = block_lieu[0]+", "+block_lieu[1]+", "+block_lieu[block_lieu.length-2]+", "+block_lieu[block_lieu.length-1]
            document.querySelector(".details-card").innerHTML = `
            <b>Lieu :</b> ${place}
            <b>Nombre de signalements :</b> ${mt[2]}
            `
        });
    });
});

}

/********************************************************* */

function mapperRed(points, map){
    points.forEach(mt => {
        const pt = [mt[0], mt[1]]
     
        const marker = L.marker(pt, {redalert}).addTo(map);
        marker.on('click', function() {
        marker.bindPopup("Chargement des infos...").openPopup();
        getLieu(pt[0], pt[1], function(lieu) {
            marker.setPopupContent(
                `<b>Coordonnées :</b> ${pt[0].toFixed(5)}, ${pt[1].toFixed(5)}<br>` +
                `<b>Lieu :</b> ${lieu}`
            );
            let block_lieu = lieu.split(",")
            let place = block_lieu[0]+", "+block_lieu[1]+", "+block_lieu[block_lieu.length-2]+", "+block_lieu[block_lieu.length-1]
            document.querySelector(".details-card").innerHTML = `
            <b>Lieu :</b> ${place}
            <b>Nombre de signalements :</b> ${mt[2]}
            `
        });
    });
});

}
/******************************************************* */

fetch(`/signalements_items/`)
.then(res => res.json())
.then(data => {
    // console.log(data)
    let points = []
    let occurs = []
     data.forEach(({ lat, long, occur }) => {
      points.push([lat, long]);
      occurs.push([lat, long, occur])
    });
    mapperRed(occurs, map)
})

function CartographierZoneRisque(){
    console.log("clické")

    document.getElementById("map2").style.display = "none" ? "block" : "none";
    document.getElementById("map").style.display = "block" ? "none" : "block";

    const map2 = L.map('map2').setView([48.7904, 2.4606], 12);
    L.tileLayer('https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors',
        maxZoom: 18
    }).addTo(map2); 

    fetch(`/zone_5/`)
    .then(res => res.json())
    .then(data => {
        let points = []
        let occurs = []
        data.forEach(({ lat, long, occur }) => {
        points.push([lat, long]);
        occurs.push([lat, long, occur])
        });
        mapperFilter(points, map2)  
    })

    
}
document.getElementById("rh").addEventListener("click", CartographierZoneRisque)

function mapperFilter(points, map){
    points.forEach(mt => {
        const pt = [mt[0], mt[1]]
     
        const marker = L.marker(pt, {redalert}).addTo(map);
        marker.on('click', function() {
        marker.bindPopup("Chargement des infos...").openPopup();
        getLieu(pt[0], pt[1], function(lieu) {
            marker.setPopupContent(
                `<b>Coordonnées :</b> ${pt[0].toFixed(5)}, ${pt[1].toFixed(5)}<br>` +
                `<b>Lieu :</b> ${lieu}`
            );
            let block_lieu = lieu.split(",")
            let place = block_lieu[0]+", "+block_lieu[1]+", "+block_lieu[block_lieu.length-2]+", "+block_lieu[block_lieu.length-1]
            document.querySelector(".details-card").innerHTML = `
            <b>Lieu :</b> ${place}
            <b>Nombre de signalements :</b> ${mt[2]}
            `
        });
    });
});

}
