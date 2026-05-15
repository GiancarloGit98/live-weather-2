const user = JSON.parse(localStorage.getItem('user'));
if (!user) {
    window.location.href = 'index.html';
}

const API_URL = 'https://live-weather-2.onrender.com/api';

const supportForm = document.getElementById('supportForm');
const messageEl = document.getElementById('statusMessage');
const ticketsList = document.getElementById('ticketsList');

const statusTranslations = {
    'pendiente': '🕐 Pendiente',
    'atendido': '✅ Atendido',
    'cerrado': '🔒 Cerrado'
};

const statusColors = {
    'pendiente': '#f39c12',
    'atendido': '#3498db',
    'cerrado': '#2ecc71'
};

async function loadTickets() {
    console.log('Cargando tickets para user_id:', user.id);
    
    try {
        const response = await fetch(`${API_URL}/support/list`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({user_id: user.id})
        });
        
        const data = await response.json();
        console.log('Respuesta del servidor:', data);
        
        if (response.ok && data.tickets) {
            console.log('Tickets recibidos:', data.tickets.length);
            displayTickets(data.tickets);
        } else {
            console.error('Error en respuesta:', data);
        }
    } catch (error) {
        console.error('Error al cargar tickets:', error);
    }
}

function displayTickets(tickets) {
    if (tickets.length === 0) {
        ticketsList.innerHTML = '<p class="no-tickets">No tienes solicitudes registradas</p>';
        return;
    }
    
    ticketsList.innerHTML = '';
    
    tickets.forEach(ticket => {
        const date = new Date(ticket.created_at);
        const formattedDate = date.toLocaleDateString('es-ES', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
        
        const statusText = statusTranslations[ticket.status] || ticket.status;
        const statusColor = statusColors[ticket.status] || '#999';
        
        const card = document.createElement('div');
        card.className = 'ticket-card';
        card.innerHTML = `
            <div class="ticket-header">
                <span class="ticket-id">#${ticket.id}</span>
                <span class="ticket-status" style="background: ${statusColor}">${statusText}</span>
            </div>
            <div class="ticket-body">
                <p class="ticket-message">${ticket.message}</p>
                <p class="ticket-phone">📞 ${ticket.phone}</p>
            </div>
            ${ticket.response ? `
                <div class="admin-response-display">
                    <strong>📝 Respuesta del equipo:</strong>
                    <p>${ticket.response}</p>
                </div>
            ` : ''}
            <div class="ticket-footer">
                <span class="ticket-date">${formattedDate}</span>
            </div>
        `;
        
        ticketsList.appendChild(card);
    });
}

supportForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const phone = document.getElementById('phone').value;
    const message = document.getElementById('supportMessage').value;
    
    messageEl.textContent = '';
    
    try {
        const response = await fetch(`${API_URL}/support/submit`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                user_id: user.id,
                phone: phone,
                message: message
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            messageEl.textContent = '✅ Solicitud enviada exitosamente. Te contactaremos pronto.';
            messageEl.className = 'message success';
            supportForm.reset();
            loadTickets();
        } else {
            messageEl.textContent = data.error || 'Error al enviar solicitud';
            messageEl.className = 'message error';
        }
    } catch (error) {
        messageEl.textContent = 'Error al conectar con el servidor';
        messageEl.className = 'message error';
    }
});

loadTickets();