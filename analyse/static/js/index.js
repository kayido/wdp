const fileInput = document.querySelector('input[type="file"]');
const preview = document.getElementById('preview');

fileInput.addEventListener('change', function() {
    preview.innerHTML = '';
    const file = this.files[0];
    if (file && file.type.startsWith('image/')) {
        const img = document.createElement('img');
        img.src = URL.createObjectURL(file);
        img.style.maxWidth = '300px';
        img.style.marginTop = '15px';
        preview.appendChild(img);
    }
});

document.querySelector("form input+p label").innerHTML = 
`
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" fill="#000000" height="800px" width="800px" version="1.1" id="Capa_1" viewBox="0 0 486.3 486.3" xml:space="preserve">
    <g>
    <g>
        <path d="M395.5,135.8c-5.2-30.9-20.5-59.1-43.9-80.5c-26-23.8-59.8-36.9-95-36.9c-27.2,0-53.7,7.8-76.4,22.5    c-18.9,12.2-34.6,28.7-45.7,48.1c-4.8-0.9-9.8-1.4-14.8-1.4c-42.5,0-77.1,34.6-77.1,77.1c0,5.5,0.6,10.8,1.6,16    C16.7,200.7,0,232.9,0,267.2c0,27.7,10.3,54.6,29.1,75.9c19.3,21.8,44.8,34.7,72,36.2c0.3,0,0.5,0,0.8,0h86    c7.5,0,13.5-6,13.5-13.5s-6-13.5-13.5-13.5h-85.6C61.4,349.8,27,310.9,27,267.1c0-28.3,15.2-54.7,39.7-69    c5.7-3.3,8.1-10.2,5.9-16.4c-2-5.4-3-11.1-3-17.2c0-27.6,22.5-50.1,50.1-50.1c5.9,0,11.7,1,17.1,3c6.6,2.4,13.9-0.6,16.9-6.9    c18.7-39.7,59.1-65.3,103-65.3c59,0,107.7,44.2,113.3,102.8c0.6,6.1,5.2,11,11.2,12c44.5,7.6,78.1,48.7,78.1,95.6    c0,49.7-39.1,92.9-87.3,96.6h-73.7c-7.5,0-13.5,6-13.5,13.5s6,13.5,13.5,13.5h74.2c0.3,0,0.6,0,1,0c30.5-2.2,59-16.2,80.2-39.6    c21.1-23.2,32.6-53,32.6-84C486.2,199.5,447.9,149.6,395.5,135.8z"/>
        <path d="M324.2,280c5.3-5.3,5.3-13.8,0-19.1l-71.5-71.5c-2.5-2.5-6-4-9.5-4s-7,1.4-9.5,4l-71.5,71.5c-5.3,5.3-5.3,13.8,0,19.1    c2.6,2.6,6.1,4,9.5,4s6.9-1.3,9.5-4l48.5-48.5v222.9c0,7.5,6,13.5,13.5,13.5s13.5-6,13.5-13.5V231.5l48.5,48.5    C310.4,285.3,318.9,285.3,324.2,280z"/>
    </g>
    </g>
</svg>
`

let marker;

// Autocomplete
const search = document.getElementById('search');
const suggestions = document.getElementById('suggestions');

function clearSuggestions() {
    suggestions.innerHTML = '';
    suggestions.style.display = 'none';
}

function showSuggestions(results) {
    suggestions.innerHTML = '';
    results.forEach(item => {
        const div = document.createElement('div');
        div.className = 'autocomplete-suggestion';
        div.textContent = item.display_name;
        div.onclick = () => {
            search.value = item.display_name;
            clearSuggestions();
            map.setView([item.lat, item.lon], 16);
            if (marker) marker.remove();
            marker = L.marker([item.lat, item.lon]).addTo(map)
                .bindPopup(item.display_name).openPopup();
        };
        suggestions.appendChild(div);
    });
    suggestions.style.display = results.length ? 'block' : 'none';
}

let lastTimeout = null;
search.addEventListener('keyup', function(e) {
    const v = search.value.trim();
    if (lastTimeout) clearTimeout(lastTimeout);
    if (!v) return clearSuggestions();
    lastTimeout = setTimeout(() => {
        fetch(`https://nominatim.openstreetmap.org/search?format=jsonv2&limit=5&q=${encodeURIComponent(v)}`)
            .then(r => r.json())
            .then((data) =>  {
                showSuggestions(data) 
            }
                
            )
            .catch(() => clearSuggestions());
    }, 250); // Limite le nombre de requêtes
    getPlaceInfo(document.getElementById("search").value).then(info => {
    if (info) {
        console.log("Place ID :", info.place_id);
        console.log("Latitude :", info.lat);
        console.log("Longitude :", info.lon);
        document.getElementById("lat").value = info.lat
        document.getElementById("long").value = info.lon
    } else {
        console.log("Aucun résultat trouvé.");
    }
    });
});

// Fermer suggestions si clic ailleurs
document.addEventListener('click', function(e) {
    if (!suggestions.contains(e.target) && e.target !== search) {
        clearSuggestions();
    }
});


async function getPlaceInfo(lieu) {
    const url = `https://nominatim.openstreetmap.org/search?format=json&limit=1&q=${encodeURIComponent(lieu)}`;
    try {
        const response = await fetch(url, {
            headers: {
                'Accept-Language': 'fr' // Optionnel : pour des résultats en français
            }
        });
        const data = await response.json();
        if (data.length > 0) {
            return {
                place_id: data[0].place_id,
                lat: data[0].lat,
                lon: data[0].lon
            };
        } else {
            return null;
        }
    } catch (err) {
        console.error("Erreur lors de la recherche :", err);
        return null;
    }
}
