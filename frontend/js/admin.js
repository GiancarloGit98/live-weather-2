const user = JSON.parse(localStorage.getItem('user'));
if (!user || user.role_id !== 2) {
    window.location.href = 'home.html';
}

const API_URL = 'http://localhost:5000/api';

let allTickets = [];
let allUsers = [];
let currentFilter = 'all';

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

// ── Tab switching ──────────────────────────────────────
function switchAdminTab(tab) {
    document.querySelectorAll('.admin-tab').forEach(t => t.classList.remove('active'));
    event.target.classList.add('active');
    
    document.getElementById('ticketsSection').classList.add('hidden');
    document.getElementById('usersSection').classList.add('hidden');
    
    if (tab === 'tickets') {
        document.getElementById('ticketsSection').classList.remove('hidden');
        loadTickets();
    } else {
        document.getElementById('usersSection').classList.remove('hidden');
        loadUsers();
    }
}

// ── TICKETS ────────────────────────────────────────────
async function loadTickets() {
    try {
        const response = await fetch(`${API_URL}/admin/tickets`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({user_id: user.id})
        });
        const data = await response.json();
        if (response.ok && data.tickets) {
            allTickets = data.tickets;
            displayTickets();
        }
    } catch (error) {
        console.error('Error al cargar tickets:', error);
    }
}

function filterTickets(status, e) {
    currentFilter = status;
    document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
    if (e) e.target.classList.add('active');
    displayTickets();
}

function displayTickets() {
    const ticketsList = document.getElementById('adminTicketsList');
    const ticketCounter = document.getElementById('ticketCounter');
    
    let filtered = allTickets;
    if (currentFilter !== 'all') {
        filtered = allTickets.filter(t => t.status === currentFilter);
    }
    
    const pendientes = allTickets.filter(t => t.status === 'pendiente').length;
    const atendidos = allTickets.filter(t => t.status === 'atendido').length;
    const cerrados = allTickets.filter(t => t.status === 'cerrado').length;
    ticketCounter.textContent = `Total: ${allTickets.length} | Pendientes: ${pendientes} | Atendidos: ${atendidos} | Cerrados: ${cerrados}`;
    
    if (filtered.length === 0) {
        ticketsList.innerHTML = '<p class="no-tickets">No hay solicitudes en esta categoría</p>';
        return;
    }
    
    ticketsList.innerHTML = '';
    
    filtered.forEach(ticket => {
        const date = new Date(ticket.created_at);
        const formattedDate = date.toLocaleDateString('es-ES', {
            year: 'numeric', month: 'long', day: 'numeric',
            hour: '2-digit', minute: '2-digit'
        });
        
        const statusText = statusTranslations[ticket.status] || ticket.status;
        const statusColor = statusColors[ticket.status] || '#999';
        
        let actionsHTML = '';
        if (ticket.status === 'pendiente') {
            actionsHTML = `
                <div class="response-area">
                    <textarea id="response-${ticket.id}" class="response-input" placeholder="Escribe tu respuesta al usuario..." rows="3"></textarea>
                    <button class="action-btn atender" onclick="updateStatus(${ticket.id}, 'atendido')">✅ Responder y Atender</button>
                </div>
            `;
        } else if (ticket.status === 'atendido') {
            actionsHTML = `
                <div class="admin-response-display">
                    <strong>📝 Respuesta:</strong>
                    <p>${ticket.response || 'Sin respuesta'}</p>
                </div>
                <button class="action-btn cerrar" onclick="updateStatus(${ticket.id}, 'cerrado')">🔒 Cerrar caso</button>
            `;
        } else {
            actionsHTML = `
                <div class="admin-response-display">
                    <strong>📝 Respuesta:</strong>
                    <p>${ticket.response || 'Sin respuesta'}</p>
                </div>
                <span class="closed-label">Caso cerrado</span>
            `;
        }
        
        const card = document.createElement('div');
        card.className = 'ticket-card';
        card.innerHTML = `
            <div class="ticket-header">
                <span class="ticket-id">#${ticket.id}</span>
                <span class="ticket-status" style="background: ${statusColor}">${statusText}</span>
            </div>
            <div class="ticket-user-info">
                <span>👤 ${ticket.full_name}</span>
                <span>📧 ${ticket.email}</span>
            </div>
            <div class="ticket-body">
                <p class="ticket-message">${ticket.message}</p>
                <p class="ticket-phone">📞 ${ticket.phone}</p>
            </div>
            <div class="ticket-footer">
                <span class="ticket-date">${formattedDate}</span>
                <div class="ticket-actions">${actionsHTML}</div>
            </div>
        `;
        ticketsList.appendChild(card);
    });
}

async function updateStatus(ticketId, newStatus) {
    let response = null;
    if (newStatus === 'atendido') {
        const textarea = document.getElementById(`response-${ticketId}`);
        if (textarea) {
            response = textarea.value.trim();
            if (!response) {
                alert('Por favor escribe una respuesta antes de atender el ticket');
                return;
            }
        }
    }
    try {
        const fetchResponse = await fetch(`${API_URL}/admin/tickets/update`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ticket_id: ticketId, status: newStatus, response: response})
        });
        if (fetchResponse.ok) loadTickets();
    } catch (error) {
        console.error('Error al actualizar ticket:', error);
    }
}

// ── USERS ──────────────────────────────────────────────
async function loadUsers() {
    try {
        const response = await fetch(`${API_URL}/admin/users`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({user_id: user.id})
        });
        const data = await response.json();
        if (response.ok && data.users) {
            allUsers = data.users;
            displayUsers();
        }
    } catch (error) {
        console.error('Error al cargar usuarios:', error);
    }
}

function displayUsers() {
    const usersList = document.getElementById('adminUsersList');
    const userCounter = document.getElementById('userCounter');
    
    const admins = allUsers.filter(u => u.role_id === 2).length;
    const normals = allUsers.filter(u => u.role_id === 1).length;
    userCounter.textContent = `Total: ${allUsers.length} | Administradores: ${admins} | Usuarios: ${normals}`;
    
    usersList.innerHTML = '';
    
    allUsers.forEach(u => {
        const isAdmin = u.role_id === 2;
        const isCurrentUser = u.id === user.id;
        const date = new Date(u.created_at);
        const formattedDate = date.toLocaleDateString('es-ES', {
            year: 'numeric', month: 'long', day: 'numeric'
        });
        
        const card = document.createElement('div');
        card.className = 'user-card';
        card.innerHTML = `
            <div class="user-card-header">
                <div class="user-info">
                    <span class="user-avatar">${u.full_name.charAt(0).toUpperCase()}</span>
                    <div>
                        <div class="user-name">
                            ${u.full_name}
                            ${isCurrentUser ? '<span class="you-badge">Tú</span>' : ''}
                        </div>
                        <div class="user-email">📧 ${u.email}</div>
                        <div class="user-date">📅 Registrado: ${formattedDate}</div>
                    </div>
                </div>
                <span class="user-role-badge ${isAdmin ? 'admin' : 'normal'}">
                    ${isAdmin ? '⚙️ Admin' : '👤 Usuario'}
                </span>
            </div>
            ${!isCurrentUser ? `
                <div class="user-actions">
                    ${isAdmin
                        ? `<button class="role-btn demote" onclick="updateRole(${u.id}, 1)">↓ Quitar Admin</button>`
                        : `<button class="role-btn promote" onclick="updateRole(${u.id}, 2)">↑ Hacer Admin</button>`
                    }
                    <button class="role-btn delete-user" onclick="deleteUser(${u.id}, '${u.full_name}')">🗑️ Eliminar</button>
                </div>
            ` : '<div class="user-actions"><span class="closed-label">No puedes modificar tu propio rol</span></div>'}
        `;
        usersList.appendChild(card);
    });
}

async function updateRole(targetUserId, roleId) {
    const action = roleId === 2 ? 'hacer administrador' : 'quitar permisos de administrador a';
    if (!confirm(`¿Estás seguro de ${action} este usuario?`)) return;
    
    try {
        const response = await fetch(`${API_URL}/admin/users/role`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({target_user_id: targetUserId, role_id: roleId})
        });
        if (response.ok) loadUsers();
    } catch (error) {
        console.error('Error al actualizar rol:', error);
    }
}

// Cargar tickets al inicio
loadTickets();

async function deleteUser(targetUserId, userName) {
    if (!confirm(`¿Estás seguro de eliminar al usuario "${userName}"? Esta acción no se puede deshacer.`)) return;
    
    try {
        const response = await fetch(`${API_URL}/admin/users/delete`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({admin_id: user.id, target_user_id: targetUserId})
        });
        
        if (response.ok) {
            loadUsers();
        } else {
            const data = await response.json();
            alert(data.error || 'Error al eliminar usuario');
        }
    } catch (error) {
        console.error('Error al eliminar usuario:', error);
    }
}