# 🌤️ Live Weather 2.0

Aplicación web de consulta climática desarrollada como proyecto académico para el SENA. Permite a los usuarios consultar el clima actual, ver pronósticos por horas, guardar ubicaciones favoritas y enviar solicitudes de soporte.

---

## 📋 Características

- **Autenticación** — Registro e inicio de sesión con contraseñas encriptadas (bcrypt)
- **Consulta de Clima** — Temperatura, humedad, viento, índice UV, presión atmosférica y más
- **Pronóstico por Horas** — Slider interactivo con datos hora a hora para cualquier fecha
- **Mis Ubicaciones** — Guarda ciudades favoritas con clima en tiempo real y recomendaciones automáticas
- **Servicio al Cliente** — Envío de PQR con seguimiento de estado
- **Panel de Administrador** — Gestión de tickets PQR y usuarios del sistema
- **Diseño Minimalista** — Interfaz con efecto glass, videos de fondo y tema oscuro

---

## 🛠️ Tecnologías

| Capa | Tecnología |
|------|-----------|
| Frontend | HTML5, CSS3, JavaScript (Vanilla) |
| Backend | Python 3.14 (http.server nativo) |
| Base de datos | MySQL 9.5 |
| API climática | Open-Meteo (gratuita, sin API key) |
| Seguridad | bcrypt para hashing de contraseñas |

---

## 📁 Estructura del Proyecto

Live Weather 2.0/
├── frontend/
│   ├── assets/          # Imágenes, videos y fuentes
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   ├── auth.js
│   │   ├── home.js
│   │   ├── weather.js
│   │   ├── forecast.js
│   │   ├── favorites.js
│   │   ├── support.js
│   │   └── admin.js
│   ├── index.html       # Login / Registro
│   ├── home.html        # Menú principal
│   ├── weather.html     # Consulta clima actual
│   ├── forecast.html    # Pronóstico por horas
│   ├── favorites.html   # Mis ubicaciones
│   ├── support.html     # Servicio al cliente
│   └── admin.html       # Panel de administrador
├── backend/
│   ├── config/
│   │   └── database.py  # Conexión a MySQL
│   ├── models/
│   │   ├── users.py
│   │   ├── favorites.py
│   │   └── support.py
│   ├── utils/
│   │   └── weather.py   # Integración con Open-Meteo
│   └── server.py        # Servidor HTTP y endpoints
├── .env                 # Variables de entorno (no incluido en Git)
├── .gitignore
├── requirements.txt
└── README.md

---

## ⚙️ Instalación y configuración

### Requisitos previos

- Python 3.10 o superior
- MySQL 8.0 o superior
- Git

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/live-weather-2.git
cd live-weather-2
```

### 2. Crear y activar el entorno virtual

```bash
python -m venv venv

# Windows
.\venv\Scripts\Activate

# Mac/Linux
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar la base de datos

Abre MySQL y ejecuta:

```sql
CREATE DATABASE live_weather_2;
USE live_weather_2;

CREATE TABLE roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

INSERT INTO roles (name) VALUES ('usuario'), ('administrador');

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(150) NOT NULL,
    role_id INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(id)
);

CREATE TABLE favorite_locations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    city_name VARCHAR(150) NOT NULL,
    country VARCHAR(100),
    latitude DECIMAL(10, 6),
    longitude DECIMAL(10, 6),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE support_tickets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    phone VARCHAR(20),
    message TEXT NOT NULL,
    response TEXT DEFAULT NULL,
    status ENUM('pendiente', 'atendido', 'cerrado') DEFAULT 'pendiente',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### 5. Crear el archivo `.env`

Crea un archivo `.env` en la raíz del proyecto con este contenido:

DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=tu_contraseña
DB_NAME=live_weather_2

### 6. Ejecutar el servidor

```bash
python -m backend.server
```

El servidor quedará corriendo en `https://live-weather-2.onrender.com`

### 7. Abrir el frontend

Abre `frontend/index.html` con Live Server en VS Code, o accede directamente a:
http://127.0.0.1:5500/frontend/index.html

---

## 👤 Roles de usuario

| Rol | Acceso |
|-----|--------|
| Usuario | Consulta clima, pronóstico, favoritos y PQR |
| Administrador | Todo lo anterior + panel de administración |

Para crear un administrador, desde el Panel Admin ve a **Gestión de Usuarios** y asigna el rol manualmente.

---

## 🌐 API Climática

Este proyecto utiliza [Open-Meteo](https://open-meteo.com/), una API meteorológica gratuita y de código abierto que no requiere registro ni API key.

---

## 📦 Dependencias

bcrypt
mysql-connector-python
requests
python-dotenv

---

## 👨‍💻 Autor

**Giancarlo Moreno**  
Proyecto académico — SENA  
2026