const user = JSON.parse(localStorage.getItem('user'));
if (!user) {
    window.location.href = 'index.html';
}

const API_URL = 'http://localhost:5000/api';

const addFavoriteForm = document.getElementById('addFavoriteForm');
const favoritesList = document.getElementById('favoritesList');
const messageEl = document.getElementById('message');

const weatherIcons = {
    0: '☀️', 1: '🌤️', 2: '⛅', 3: '☁️',
    45: '🌫️', 48: '🌫️',
    51: '🌦️', 53: '🌦️', 55: '🌧️',
    61: '🌧️', 63: '🌧️', 65: '🌧️',
    71: '🌨️', 73: '🌨️', 75: '🌨️',
    80: '🌦️', 81: '🌦️', 82: '⛈️',
    95: '⛈️', 96: '⛈️', 99: '⛈️'
};

const daysES = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'];
const monthsES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'];

function getWindDirection(degrees) {
    const dirs = ['N', 'NE', 'E', 'SE', 'S', 'SO', 'O', 'NO'];
    return dirs[Math.round(degrees / 45) % 8];
}

function getUVLabel(uv) {
    if (uv <= 2) return 'Bajo';
    if (uv <= 5) return 'Moderado';
    if (uv <= 7) return 'Alto';
    if (uv <= 10) return 'Muy alto';
    return 'Extremo';
}

function getRecTagClass(text) {
    if (text.includes('paraguas') || text.includes('lluvia')) return 'rain';
    if (text.includes('frío') || text.includes('abrígate')) return 'cold';
    if (text.includes('calor') || text.includes('hidratado')) return 'hot';
    if (text.includes('Humedad') || text.includes('bochornoso')) return 'humid';
    if (text.includes('Vientos')) return 'wind';
    if (text.includes('despejado') || text.includes('aire libre')) return 'clear';
    return 'normal';
}

function formatRecommendations(recommendation) {
    const parts = recommendation.split(' | ');
    return parts.map(part => {
        const tagClass = getRecTagClass(part);
        return `<span class="rec-tag ${tagClass}">${part}</span>`;
    }).join('');
}

async function loadFavorites() {
    try {
        const response = await fetch(`${API_URL}/favorites/list`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({user_id: user.id})
        });
        
        const data = await response.json();
        
        if (response.ok && data.favorites) {
            displayFavorites(data.favorites);
        }
    } catch (error) {
        console.error('Error al cargar favoritos:', error);
    }
}

function displayFavorites(favorites) {
    if (favorites.length === 0) {
        favoritesList.innerHTML = '<p class="no-favorites">No tienes ubicaciones favoritas aún</p>';
        return;
    }
    
    favoritesList.innerHTML = '';
    
    favorites.forEach(fav => {
        const icon = weatherIcons[fav.weather_code] || '🌤️';
        const dt = new Date(fav.time);
        const dayName = daysES[dt.getDay()];
        const dateStr = `${dt.getDate()} de ${monthsES[dt.getMonth()]}`;
        const timeStr = dt.toLocaleTimeString('es-ES', {hour: '2-digit', minute: '2-digit'});
        
        const card = document.createElement('div');
        card.className = 'favorite-card';
        card.id = `fav-${fav.id}`;
        card.innerHTML = `
            <div class="fav-header">
                <div>
                    <h3>${fav.city}, ${fav.country}</h3>
                    <div class="fav-datetime">${dayName}, ${dateStr} · ${timeStr}</div>
                </div>
                <button class="delete-btn" onclick="deleteFavorite(${fav.id})">🗑️</button>
            </div>

            <div class="fav-main">
                <div class="fav-icon">${icon}</div>
                <div class="fav-temp-block">
                    <div class="fav-temp">${Math.round(fav.temperature)}°C</div>
                    <div class="fav-apparent">Sensación: ${Math.round(fav.apparent_temperature)}°C</div>
                </div>
            </div>

            <div class="fav-grid">
                <div class="fav-grid-item">
                    <span class="fgi-icon">💧</span>
                    <span class="fgi-label">Humedad</span>
                    <span class="fgi-value">${fav.humidity}%</span>
                </div>
                <div class="fav-grid-item">
                    <span class="fgi-icon">💨</span>
                    <span class="fgi-label">Viento</span>
                    <span class="fgi-value">${fav.wind_speed} km/h ${getWindDirection(fav.wind_direction)}</span>
                </div>
                <div class="fav-grid-item">
                    <span class="fgi-icon">☀️</span>
                    <span class="fgi-label">Índice UV</span>
                    <span class="fgi-value">${fav.uv_index} (${getUVLabel(fav.uv_index)})</span>
                </div>
                <div class="fav-grid-item">
                    <span class="fgi-icon">🌧️</span>
                    <span class="fgi-label">Precipitación</span>
                    <span class="fgi-value">${fav.precipitation} mm</span>
                </div>
                <div class="fav-grid-item">
                    <span class="fgi-icon">🔵</span>
                    <span class="fgi-label">Presión</span>
                    <span class="fgi-value">${fav.pressure} hPa</span>
                </div>
            </div>

            <div class="fav-recommendation">
                ${formatRecommendations(fav.recommendation)}
            </div>
        `;
        
        favoritesList.appendChild(card);
    });
    
    favoritesList.innerHTML += `<p class="favorites-counter">Tienes ${favorites.length} ubicación${favorites.length !== 1 ? 'es' : ''} guardada${favorites.length !== 1 ? 's' : ''}</p>`;
}

addFavoriteForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const cityName = document.getElementById('cityInput').value;
    messageEl.textContent = '';
    
    try {
        const coordsResponse = await fetch(`${API_URL}/weather`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({city: cityName})
        });
        
        const coordsData = await coordsResponse.json();
        
        if (!coordsResponse.ok || !coordsData.success) {
            messageEl.textContent = 'Ciudad no encontrada';
            messageEl.className = 'message error';
            return;
        }
        
        const addResponse = await fetch(`${API_URL}/favorites/add`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                user_id: user.id,
                city_name: coordsData.city,
                country: coordsData.country,
                latitude: coordsData.latitude,
                longitude: coordsData.longitude
            })
        });
        
        const addData = await addResponse.json();
        
        if (addResponse.ok) {
            messageEl.textContent = 'Ciudad agregada a favoritos';
            messageEl.className = 'message success';
            addFavoriteForm.reset();
            loadFavorites();
        } else {
            messageEl.textContent = addData.error;
            messageEl.className = 'message error';
        }
    } catch (error) {
        messageEl.textContent = 'Error al agregar favorito';
        messageEl.className = 'message error';
    }
});

async function deleteFavorite(favoriteId) {
    if (!confirm('¿Eliminar esta ubicación de favoritos?')) return;
    
    const card = document.getElementById(`fav-${favoriteId}`);
    if (card) card.classList.add('removing');
    
    setTimeout(async () => {
        try {
            const response = await fetch(`${API_URL}/favorites/delete`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({favorite_id: favoriteId, user_id: user.id})
            });
            
            if (response.ok) loadFavorites();
        } catch (error) {
            console.error('Error al eliminar favorito:', error);
        }
    }, 400);
}

loadFavorites();