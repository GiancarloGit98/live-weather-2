const user = JSON.parse(localStorage.getItem('user'));

if (!user) {
    window.location.href = 'index.html';
}

document.getElementById('userName').textContent = user.full_name;

function logout() {
    localStorage.removeItem('user');
    window.location.href = 'index.html';
}

if (user && user.role_id === 2) {
    const adminBtn = document.createElement('a');
    adminBtn.href = 'admin.html';
    adminBtn.className = 'admin-float-btn';
    adminBtn.innerHTML = `
        <img src="assets/admin_logo.png" alt="Admin" class="menu-icon-img">
        <span>Admin Panel</span>
    `;
    document.body.appendChild(adminBtn);
}