const user = JSON.parse(localStorage.getItem('user'));
if (!user) window.location.href = 'index.html';

const API_URL = 'http://localhost:5000/api';

const forecastForm = document.getElementById('forecastForm');
const forecastResult = document.getElementById('forecastResult');
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

const monthsES = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
const daysES = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'];

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

forecastForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const city = document.getElementById('cityInput').value;
    const date = document.getElementById('dateInput').value;

    forecastResult.classList.add('hidden');
    errorMessage.textContent = '';

    try {
        const response = await fetch(`${API_URL}/hourly`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({city, date})
        });

        const data = await response.json();

        if (response.ok && data.success) {
            displayForecast(data, date);
        } else {
            errorMessage.textContent = data.error || 'No se pudo obtener el pronóstico';
            errorMessage.className = 'message error';
        }
    } catch (error) {
        errorMessage.textContent = 'Error al conectar con el servidor';
        errorMessage.className = 'message error';
    }
});

function displayForecast(data, dateStr) {
    const dt = new Date(dateStr + 'T00:00:00');
    const dayName = daysES[dt.getDay()];
    const dayNum = dt.getDate();
    const month = monthsES[dt.getMonth()];
    const year = dt.getFullYear();

    document.getElementById('cityName').textContent = `${data.city}, ${data.country} — ${dayName} ${dayNum} ${month} ${year}`;

    const s = data.summary;
    const summaryEl = document.getElementById('forecastSummary');
    summaryEl.innerHTML = `
        <div class="summary-grid">
            <div class="summary-card">
                <span class="sum-icon">🌡️</span>
                <span class="sum-label">Máx / Mín</span>
                <span class="sum-value">${Math.round(s.temp_max)}° / ${Math.round(s.temp_min)}°</span>
            </div>
            <div class="summary-card">
                <span class="sum-icon">🌅</span>
                <span class="sum-label">Amanecer</span>
                <span class="sum-value">${s.sunrise ? s.sunrise.split('T')[1].slice(0,5) : '--:--'}</span>
            </div>
            <div class="summary-card">
                <span class="sum-icon">🌇</span>
                <span class="sum-label">Atardecer</span>
                <span class="sum-value">${s.sunset ? s.sunset.split('T')[1].slice(0,5) : '--:--'}</span>
            </div>
            <div class="summary-card">
                <span class="sum-icon">🌧️</span>
                <span class="sum-label">Prob. lluvia</span>
                <span class="sum-value">${s.precipitation_max ?? 0}%</span>
            </div>
            <div class="summary-card">
                <span class="sum-icon">☀️</span>
                <span class="sum-label">UV máx</span>
                <span class="sum-value">${s.uv_max ?? 0} (${getUVLabel(s.uv_max ?? 0)})</span>
            </div>
            <div class="summary-card">
                <span class="sum-icon">💨</span>
                <span class="sum-label">Viento máx</span>
                <span class="sum-value">${s.wind_max ?? 0} km/h</span>
            </div>
        </div>
    `;

    const slider = document.getElementById('hoursSlider');
    slider.innerHTML = '';

    const now = new Date();
    let currentHourCard = null;

    data.hours.forEach((hour, index) => {
        const dt = new Date(hour.time);
        const hourStr = dt.toLocaleTimeString('es-ES', {hour: '2-digit', minute: '2-digit'});
        const icon = weatherIcons[hour.weather_code] || '🌤️';

        const card = document.createElement('div');
        card.className = 'hour-card';
        card.dataset.index = index;
        card.innerHTML = `
            <div class="hour-time">${hourStr}</div>
            <div class="hour-icon">${icon}</div>
            <div class="hour-temp">${Math.round(hour.temperature)}°C</div>
            <div class="hour-rain">💧${hour.precipitation_probability}%</div>
        `;

        card.addEventListener('click', () => {
            document.querySelectorAll('.hour-card').forEach(c => c.classList.remove('selected'));
            card.classList.add('selected');
            showHourDetail(hour, hourStr, icon);
        });

        slider.appendChild(card);

        if (Math.abs(dt - now) < 1800000) {
            currentHourCard = card;
        }
    });

    if (currentHourCard) {
        currentHourCard.classList.add('current-hour');
        setTimeout(() => {
            currentHourCard.scrollIntoView({behavior: 'smooth', block: 'nearest', inline: 'center'});
        }, 100);
    }

    forecastResult.classList.remove('hidden');
}

function showHourDetail(hour, hourStr, icon) {
    const detail = document.getElementById('hourDetail');
    detail.innerHTML = `
        <div class="hour-detail-content">
            <h3>${icon} ${hourStr}</h3>
            <div class="detail-grid">
                <div class="detail-item">
                    <span class="di-label">🌡️ Temperatura</span>
                    <span class="di-value">${Math.round(hour.temperature)}°C</span>
                </div>
                <div class="detail-item">
                    <span class="di-label">🤔 Sensación</span>
                    <span class="di-value">${Math.round(hour.apparent_temperature)}°C</span>
                </div>
                <div class="detail-item">
                    <span class="di-label">💧 Prob. lluvia</span>
                    <span class="di-value">${hour.precipitation_probability}%</span>
                </div>
                <div class="detail-item">
                    <span class="di-label">💨 Viento</span>
                    <span class="di-value">${hour.wind_speed} km/h ${getWindDirection(hour.wind_direction)}</span>
                </div>
                <div class="detail-item">
                    <span class="di-label">☀️ Índice UV</span>
                    <span class="di-value">${hour.uv_index} (${getUVLabel(hour.uv_index)})</span>
                </div>
            </div>
        </div>
    `;
    detail.classList.remove('hidden');
}