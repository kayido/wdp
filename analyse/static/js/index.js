const fileInput = document.querySelector('input[type="file"]');
const preview = document.getElementById('preview');
const uploadLabel = document.querySelector(".upload-dropzone");
const search = document.getElementById('search');
const suggestions = document.getElementById('suggestions');
const latitudeInput = document.getElementById('lat');
const longitudeInput = document.getElementById('long');
const locationStatus = document.getElementById('location-status');
const useLocationButton = document.getElementById('use-location');
const form = document.getElementById('report-form');
const submitButton = document.getElementById('submit-report');

let searchTimeout = null;
let activeSearchController = null;
let latestSearchId = 0;
let confirmedAddress = "";

function setLocationStatus(message, state = "neutral") {
    locationStatus.textContent = message;
    locationStatus.dataset.state = state;
}

function clearCoordinates() {
    latitudeInput.value = "";
    longitudeInput.value = "";
    confirmedAddress = "";
    setLocationStatus("Adresse non confirmée", "neutral");
}

function clearSuggestions() {
    suggestions.innerHTML = "";
    suggestions.style.display = "none";
}

function renderUploadLabel() {
    if (!uploadLabel) return;
    uploadLabel.innerHTML = `
        <span class="upload-icon">+</span>
        <strong>Ajouter une photo</strong>
        <small>Cliquez pour choisir une image</small>
    `;
}

function updatePreview(file) {
    preview.innerHTML = "";
    if (!file || !file.type.startsWith("image/")) {
        return;
    }

    const image = document.createElement("img");
    image.src = URL.createObjectURL(file);
    image.alt = "Aperçu de l'image sélectionnée";

    const caption = document.createElement("p");
    caption.textContent = file.name;

    preview.appendChild(image);
    preview.appendChild(caption);
}

function showSuggestions(results) {
    suggestions.innerHTML = "";

    if (!results.length) {
        const empty = document.createElement("div");
        empty.className = "autocomplete-empty";
        empty.textContent = "Aucune adresse trouvée. Essayez d'ajouter la ville.";
        suggestions.appendChild(empty);
        suggestions.style.display = "block";
        return;
    }

    results.forEach(item => {
        const option = document.createElement("button");
        option.type = "button";
        option.className = "autocomplete-suggestion";
        option.textContent = item.display_name;
        option.addEventListener("click", () => selectAddress(item));
        suggestions.appendChild(option);
    });

    suggestions.style.display = "block";
}

function selectAddress(item) {
    search.value = item.display_name;
    latitudeInput.value = item.lat;
    longitudeInput.value = item.lon;
    confirmedAddress = item.display_name;
    setLocationStatus("Adresse confirmée", "success");
    clearSuggestions();
}

async function searchAddress(query, searchId, signal) {
    const params = new URLSearchParams({
        format: "jsonv2",
        limit: "5",
        countrycodes: "fr",
        addressdetails: "1",
        q: query
    });

    const response = await fetch(`https://nominatim.openstreetmap.org/search?${params.toString()}`, {
        signal,
        headers: {
            "Accept-Language": "fr"
        }
    });

    if (!response.ok) {
        throw new Error("Adresse indisponible");
    }

    const data = await response.json();
    if (searchId === latestSearchId) {
        showSuggestions(data);
        setLocationStatus(data.length ? "Choisissez une adresse dans la liste" : "Adresse introuvable", data.length ? "pending" : "error");
    }
}

function scheduleAddressSearch() {
    const query = search.value.trim();

    if (search.value !== confirmedAddress) {
        clearCoordinates();
    }

    if (searchTimeout) {
        clearTimeout(searchTimeout);
    }

    if (activeSearchController) {
        activeSearchController.abort();
    }

    if (query.length < 3) {
        clearSuggestions();
        return;
    }

    setLocationStatus("Recherche d'adresse...", "pending");
    const searchId = ++latestSearchId;
    activeSearchController = new AbortController();

    searchTimeout = setTimeout(() => {
        searchAddress(query, searchId, activeSearchController.signal)
            .catch(error => {
                if (error.name === "AbortError") return;
                clearSuggestions();
                setLocationStatus("Recherche indisponible, réessayez ou utilisez votre position", "error");
            });
    }, 450);
}

async function reverseGeocode(latitude, longitude) {
    const params = new URLSearchParams({
        format: "jsonv2",
        lat: latitude,
        lon: longitude
    });

    const response = await fetch(`https://nominatim.openstreetmap.org/reverse?${params.toString()}`, {
        headers: {
            "Accept-Language": "fr"
        }
    });

    if (!response.ok) {
        throw new Error("Adresse introuvable");
    }

    return response.json();
}

function useCurrentLocation() {
    if (!navigator.geolocation) {
        setLocationStatus("La géolocalisation n'est pas disponible sur ce navigateur", "error");
        return;
    }

    setLocationStatus("Recherche de votre position...", "pending");
    useLocationButton.disabled = true;

    navigator.geolocation.getCurrentPosition(
        async position => {
            const { latitude, longitude } = position.coords;
            latitudeInput.value = latitude;
            longitudeInput.value = longitude;

            try {
                const data = await reverseGeocode(latitude, longitude);
                const address = data.display_name || `${latitude}, ${longitude}`;
                search.value = address;
                confirmedAddress = address;
                setLocationStatus("Position confirmée", "success");
            } catch {
                search.value = `${latitude}, ${longitude}`;
                confirmedAddress = search.value;
                setLocationStatus("Position confirmée sans adresse lisible", "success");
            } finally {
                clearSuggestions();
                useLocationButton.disabled = false;
            }
        },
        () => {
            setLocationStatus("Position refusée. Vous pouvez saisir l'adresse manuellement.", "error");
            useLocationButton.disabled = false;
        },
        {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 60000
        }
    );
}

if (fileInput) {
    fileInput.addEventListener("change", function() {
        updatePreview(this.files[0]);
    });
}

if (search) {
    search.addEventListener("input", scheduleAddressSearch);
    search.addEventListener("keydown", event => {
        if (event.key === "Escape") {
            clearSuggestions();
        }
    });
}

if (useLocationButton) {
    useLocationButton.addEventListener("click", useCurrentLocation);
}

document.addEventListener("click", event => {
    if (!suggestions.contains(event.target) && event.target !== search) {
        clearSuggestions();
    }
});

if (form) {
    form.addEventListener("submit", () => {
        submitButton.disabled = true;
        submitButton.textContent = "Envoi en cours...";
    });
}

renderUploadLabel();
