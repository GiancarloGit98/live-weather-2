from flask import Flask, request, jsonify
from flask_cors import CORS
from backend.models.users import create_user, authenticate_user, get_all_users, update_user_role, delete_user
from backend.models.favorites import add_favorite, get_user_favorites, delete_favorite
from backend.models.support import create_support_ticket, get_user_tickets, get_all_tickets, update_ticket_status
from backend.utils.weather import get_weather_by_city, get_forecast_by_city, get_current_weather, get_recommendation, get_hourly_forecast_by_city

app = Flask(__name__)
CORS(app, origins="*", supports_credentials=False)


# ── Auth ──────────────────────────────────────────────
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not all(k in data for k in ['email', 'password', 'full_name']):
        return jsonify({"error": "Faltan campos requeridos"}), 400
    result = create_user(
        email=data['email'],
        password=data['password'],
        full_name=data['full_name'],
        role_id=data.get('role_id', 1)
    )
    if result['success']:
        return jsonify({"message": "Usuario registrado exitosamente", "user_id": result['user_id']}), 201
    return jsonify({"error": result['error']}), 400


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not all(k in data for k in ['email', 'password']):
        return jsonify({"error": "Faltan campos requeridos"}), 400
    result = authenticate_user(data['email'], data['password'])
    if result['success']:
        return jsonify({"message": "Autenticacion exitosa", "user": result['user']}), 200
    return jsonify({"error": result['error']}), 401


# ── Weather ───────────────────────────────────────────
@app.route('/api/weather', methods=['POST'])
def weather():
    data = request.get_json()
    if not data or 'city' not in data:
        return jsonify({"error": "Falta el nombre de la ciudad"}), 400
    result = get_weather_by_city(data['city'])
    if result['success']:
        return jsonify(result), 200
    return jsonify({"error": result['error']}), 404


@app.route('/api/forecast', methods=['POST'])
def forecast():
    data = request.get_json()
    if not data or 'city' not in data:
        return jsonify({"error": "Falta el nombre de la ciudad"}), 400
    result = get_forecast_by_city(data['city'], data.get('days', 7), data.get('start_date'))
    if result['success']:
        return jsonify(result), 200
    return jsonify({"error": result['error']}), 404


@app.route('/api/hourly', methods=['POST'])
def hourly():
    data = request.get_json()
    if not data or not all(k in data for k in ['city', 'date']):
        return jsonify({"error": "Faltan ciudad y fecha"}), 400
    result = get_hourly_forecast_by_city(data['city'], data['date'])
    if result['success']:
        return jsonify(result), 200
    return jsonify({"error": result['error']}), 404


# ── Favorites ─────────────────────────────────────────
@app.route('/api/favorites/add', methods=['POST'])
def favorites_add():
    data = request.get_json()
    if not data or not all(k in data for k in ['user_id', 'city_name', 'country', 'latitude', 'longitude']):
        return jsonify({"error": "Faltan campos requeridos"}), 400
    result = add_favorite(data['user_id'], data['city_name'], data['country'], data['latitude'], data['longitude'])
    if result['success']:
        return jsonify({"message": "Favorito agregado", "favorite_id": result['favorite_id']}), 201
    return jsonify({"error": result['error']}), 400


@app.route('/api/favorites/list', methods=['POST'])
def favorites_list():
    data = request.get_json()
    if not data or 'user_id' not in data:
        return jsonify({"error": "Falta user_id"}), 400
    result = get_user_favorites(data['user_id'])
    if not result['success']:
        return jsonify({"error": result['error']}), 500
    favorites_with_weather = []
    for fav in result['favorites']:
        weather = get_current_weather(fav['latitude'], fav['longitude'])
        if weather['success']:
            recommendation = get_recommendation(
                weather['temperature'], weather['humidity'],
                weather['wind_speed'], weather['weather_code'], 60
            )
            favorites_with_weather.append({
                "id": fav['id'], "city": fav['city_name'], "country": fav['country'],
                "temperature": weather['temperature'], "apparent_temperature": weather['apparent_temperature'],
                "humidity": weather['humidity'], "wind_speed": weather['wind_speed'],
                "wind_direction": weather['wind_direction'], "uv_index": weather['uv_index'],
                "precipitation": weather['precipitation'], "pressure": weather['pressure'],
                "weather_code": weather['weather_code'], "is_day": weather['is_day'],
                "time": weather['time'], "recommendation": recommendation
            })
    return jsonify({"favorites": favorites_with_weather}), 200


@app.route('/api/favorites/delete', methods=['POST'])
def favorites_delete():
    data = request.get_json()
    if not data or not all(k in data for k in ['favorite_id', 'user_id']):
        return jsonify({"error": "Faltan campos requeridos"}), 400
    result = delete_favorite(data['favorite_id'], data['user_id'])
    if result['success']:
        return jsonify({"message": "Favorito eliminado"}), 200
    return jsonify({"error": result['error']}), 404


# ── Support ───────────────────────────────────────────
@app.route('/api/support/submit', methods=['POST'])
def support_submit():
    data = request.get_json()
    if not data or not all(k in data for k in ['user_id', 'phone', 'message']):
        return jsonify({"error": "Faltan campos requeridos"}), 400
    result = create_support_ticket(data['user_id'], data['phone'], data['message'])
    if result['success']:
        return jsonify({"message": "Solicitud enviada exitosamente", "ticket_id": result['ticket_id']}), 201
    return jsonify({"error": result['error']}), 500


@app.route('/api/support/list', methods=['POST'])
def support_list():
    data = request.get_json()
    if not data or 'user_id' not in data:
        return jsonify({"error": "Falta user_id"}), 400
    result = get_user_tickets(data['user_id'])
    if not result['success']:
        return jsonify({"error": result['error']}), 500
    tickets = result['tickets']
    for ticket in tickets:
        if 'created_at' in ticket and ticket['created_at']:
            ticket['created_at'] = str(ticket['created_at'])
    return jsonify({"tickets": tickets}), 200


# ── Admin ─────────────────────────────────────────────
@app.route('/api/admin/tickets', methods=['POST'])
def admin_tickets():
    result = get_all_tickets()
    if not result['success']:
        return jsonify({"error": result['error']}), 500
    tickets = result['tickets']
    for ticket in tickets:
        if 'created_at' in ticket and ticket['created_at']:
            ticket['created_at'] = str(ticket['created_at'])
    return jsonify({"tickets": tickets}), 200


@app.route('/api/admin/tickets/update', methods=['POST'])
def admin_tickets_update():
    data = request.get_json()
    if not data or not all(k in data for k in ['ticket_id', 'status']):
        return jsonify({"error": "Faltan campos requeridos"}), 400
    if data['status'] not in ['pendiente', 'atendido', 'cerrado']:
        return jsonify({"error": "Estado no válido"}), 400
    result = update_ticket_status(data['ticket_id'], data['status'], data.get('response'))
    if result['success']:
        return jsonify({"message": "Estado actualizado"}), 200
    return jsonify({"error": result['error']}), 404


@app.route('/api/admin/users', methods=['POST'])
def admin_users():
    result = get_all_users()
    if result['success']:
        return jsonify({"users": result['users']}), 200
    return jsonify({"error": result['error']}), 500


@app.route('/api/admin/users/role', methods=['POST'])
def admin_users_role():
    data = request.get_json()
    if not data or not all(k in data for k in ['target_user_id', 'role_id']):
        return jsonify({"error": "Faltan campos requeridos"}), 400
    result = update_user_role(data['target_user_id'], data['role_id'])
    if result['success']:
        return jsonify({"message": "Rol actualizado"}), 200
    return jsonify({"error": result['error']}), 404


@app.route('/api/admin/users/delete', methods=['POST'])
def admin_users_delete():
    data = request.get_json()
    if not data or not all(k in data for k in ['admin_id', 'target_user_id']):
        return jsonify({"error": "Faltan campos requeridos"}), 400
    if data['admin_id'] == data['target_user_id']:
        return jsonify({"error": "No puedes eliminarte a ti mismo"}), 400
    result = delete_user(data['target_user_id'])
    if result['success']:
        return jsonify({"message": "Usuario eliminado"}), 200
    return jsonify({"error": result['error']}), 404


if __name__ == '__main__':
    app.run(debug=False, port=5000)