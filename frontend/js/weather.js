const user = JSON.parse(localStorage.getItem('user'));
if (!user) window.location.href = 'index.html';

const API_URL = 'http://localhost:5000/api';

const weatherForm = document.getElementById('weatherForm');
const weatherResult = document.getElementById('weatherResult');
const errorMessage = document.getElementById('errorMessage');

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

weatherForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const city = document.getElementById('cityInput').value;
    weatherResult.classList.add('hidden');
    errorMessage.textContent = '';

    try {
        const response = await fetch(`${API_URL}/weather`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({city})
        });
        const data = await response.json();

        if (response.ok && data.success) {
            displayWeather(data);
        } else {
            errorMessage.textContent = data.error || 'No se pudo obtener el clima';
            errorMessage.className = 'message error';
        }
    } catch (error) {
        errorMessage.textContent = 'Error al conectar con el servidor';
        errorMessage.className = 'message error';
    }
});

function displayWeather(data) {
    const dt = new Date(data.time);

    document.getElementById('cityName').textContent = `${data.city}, ${data.country}`;
    document.getElementById('weatherDay').textContent = daysES[dt.getDay()];
    document.getElementById('weatherDate').textContent = `${dt.getDate()} de ${monthsES[dt.getMonth()]} de ${dt.getFullYear()}`;
    document.getElementById('weatherTime').textContent = dt.toLocaleTimeString('es-ES', {hour: '2-digit', minute: '2-digit'});
    
    document.getElementById('temperature').textContent = `${Math.round(data.temperature)}°C`;
    document.getElementById('apparentTemp').textContent = `${Math.round(data.apparent_temperature)}°C`;
    document.getElementById('weatherIcon').textContent = weatherIcons[data.weather_code] || '🌤️';
    
    document.getElementById('humidity').textContent = `${data.humidity}%`;
    document.getElementById('windSpeed').textContent = `${data.wind_speed} km/h`;
    document.getElementById('windDirection').textContent = `Dirección: ${getWindDirection(data.wind_direction)}`;
    document.getElementById('uvIndex').textContent = data.uv_index;
    document.getElementById('uvLabel').textContent = getUVLabel(data.uv_index);
    document.getElementById('precipitation').textContent = `${data.precipitation} mm`;
    document.getElementById('pressure').textContent = `${data.pressure} hPa`;
    document.getElementById('updateTime').textContent = dt.toLocaleTimeString('es-ES', {hour: '2-digit', minute: '2-digit'});

    weatherResult.classList.remove('hidden');
}