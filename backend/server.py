import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from backend.models.users import create_user, authenticate_user, get_all_users, update_user_role, delete_user
from backend.models.favorites import add_favorite, get_user_favorites, delete_favorite
from backend.models.support import create_support_ticket, get_user_tickets, get_all_tickets, update_ticket_status
from backend.utils.weather import get_weather_by_city, get_forecast_by_city, get_current_weather, get_recommendation, get_hourly_forecast_by_city

PORT = 5000


class RequestHandler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        if self.path == '/api/register':
            self.handle_register()
        elif self.path == '/api/login':
            self.handle_login()
        elif self.path == '/api/weather':
            self.handle_weather()
        elif self.path == '/api/forecast':
            self.handle_forecast()
        elif self.path == '/api/hourly':
            self.handle_hourly()
        elif self.path == '/api/favorites/add':
            self.handle_add_favorite()
        elif self.path == '/api/favorites/list':
            self.handle_list_favorites()
        elif self.path == '/api/favorites/delete':
            self.handle_delete_favorite()
        elif self.path == '/api/support/submit':
            self.handle_submit_support()
        elif self.path == '/api/support/list':
            self.handle_list_support()
        elif self.path == '/api/admin/tickets':
            self.handle_admin_tickets()
        elif self.path == '/api/admin/tickets/update':
            self.handle_update_ticket()
        elif self.path == '/api/admin/users':
            self.handle_admin_users()
        elif self.path == '/api/admin/users/role':
            self.handle_update_role()
        elif self.path == '/api/admin/users/delete':
            self.handle_delete_user()
        else:
            self.send_json_response(404, {"error": "Ruta no encontrada"})

    def handle_register(self):
        data = self.get_json_body()
        if not data or not all(k in data for k in ['email', 'password', 'full_name']):
            self.send_json_response(400, {"error": "Faltan campos requeridos"})
            return
        result = create_user(
            email=data['email'],
            password=data['password'],
            full_name=data['full_name'],
            role_id=data.get('role_id', 1)
        )
        if result['success']:
            self.send_json_response(201, {"message": "Usuario registrado exitosamente", "user_id": result['user_id']})
        else:
            self.send_json_response(400, {"error": result['error']})

    def handle_login(self):
        data = self.get_json_body()
        if not data or not all(k in data for k in ['email', 'password']):
            self.send_json_response(400, {"error": "Faltan campos requeridos"})
            return
        result = authenticate_user(data['email'], data['password'])
        if result['success']:
            self.send_json_response(200, {"message": "Autenticacion exitosa", "user": result['user']})
        else:
            self.send_json_response(401, {"error": result['error']})

    def handle_weather(self):
        data = self.get_json_body()
        if not data or 'city' not in data:
            self.send_json_response(400, {"error": "Falta el nombre de la ciudad"})
            return
        result = get_weather_by_city(data['city'])
        if result['success']:
            self.send_json_response(200, result)
        else:
            self.send_json_response(404, {"error": result['error']})

    def handle_forecast(self):
        data = self.get_json_body()
        if not data or 'city' not in data:
            self.send_json_response(400, {"error": "Falta el nombre de la ciudad"})
            return
        days = data.get('days', 7)
        start_date = data.get('start_date', None)
        result = get_forecast_by_city(data['city'], days, start_date)
        if result['success']:
            self.send_json_response(200, result)
        else:
            self.send_json_response(404, {"error": result['error']})

    def handle_hourly(self):
        data = self.get_json_body()
        if not data or not all(k in data for k in ['city', 'date']):
            self.send_json_response(400, {"error": "Faltan ciudad y fecha"})
            return
        result = get_hourly_forecast_by_city(data['city'], data['date'])
        if result['success']:
            self.send_json_response(200, result)
        else:
            self.send_json_response(404, {"error": result['error']})

    def handle_add_favorite(self):
        data = self.get_json_body()
        if not data or not all(k in data for k in ['user_id', 'city_name', 'country', 'latitude', 'longitude']):
            self.send_json_response(400, {"error": "Faltan campos requeridos"})
            return
        result = add_favorite(
            data['user_id'],
            data['city_name'],
            data['country'],
            data['latitude'],
            data['longitude']
        )
        if result['success']:
            self.send_json_response(201, {"message": "Favorito agregado", "favorite_id": result['favorite_id']})
        else:
            self.send_json_response(400, {"error": result['error']})

    def handle_list_favorites(self):
        data = self.get_json_body()
        if not data or 'user_id' not in data:
            self.send_json_response(400, {"error": "Falta user_id"})
            return
        result = get_user_favorites(data['user_id'])
        if not result['success']:
            self.send_json_response(500, {"error": result['error']})
            return
        favorites_with_weather = []
        for fav in result['favorites']:
            weather = get_current_weather(fav['latitude'], fav['longitude'])
            if weather['success']:
                recommendation = get_recommendation(
                    weather['temperature'],
                    weather['humidity'],
                    weather['wind_speed'],
                    weather['weather_code'],
                    60
                )
                favorites_with_weather.append({
                    "id": fav['id'],
                    "city": fav['city_name'],
                    "country": fav['country'],
                    "temperature": weather['temperature'],
                    "apparent_temperature": weather['apparent_temperature'],
                    "humidity": weather['humidity'],
                    "wind_speed": weather['wind_speed'],
                    "wind_direction": weather['wind_direction'],
                    "uv_index": weather['uv_index'],
                    "precipitation": weather['precipitation'],
                    "pressure": weather['pressure'],
                    "weather_code": weather['weather_code'],
                    "is_day": weather['is_day'],
                    "time": weather['time'],
                    "recommendation": recommendation
                })
        self.send_json_response(200, {"favorites": favorites_with_weather})

    def handle_delete_favorite(self):
        data = self.get_json_body()
        if not data or not all(k in data for k in ['favorite_id', 'user_id']):
            self.send_json_response(400, {"error": "Faltan campos requeridos"})
            return
        result = delete_favorite(data['favorite_id'], data['user_id'])
        if result['success']:
            self.send_json_response(200, {"message": "Favorito eliminado"})
        else:
            self.send_json_response(404, {"error": result['error']})

    def handle_submit_support(self):
        data = self.get_json_body()
        if not data or not all(k in data for k in ['user_id', 'phone', 'message']):
            self.send_json_response(400, {"error": "Faltan campos requeridos"})
            return
        result = create_support_ticket(data['user_id'], data['phone'], data['message'])
        if result['success']:
            self.send_json_response(201, {"message": "Solicitud enviada exitosamente", "ticket_id": result['ticket_id']})
        else:
            self.send_json_response(500, {"error": result['error']})

    def handle_list_support(self):
        data = self.get_json_body()
        if not data or 'user_id' not in data:
            self.send_json_response(400, {"error": "Falta user_id"})
            return
        try:
            result = get_user_tickets(data['user_id'])
            if result['success']:
                tickets = result['tickets']
                for ticket in tickets:
                    if 'created_at' in ticket and ticket['created_at']:
                        ticket['created_at'] = str(ticket['created_at'])
                self.send_json_response(200, {"tickets": tickets})
            else:
                self.send_json_response(500, {"error": result['error']})
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})

    def handle_admin_tickets(self):
        data = self.get_json_body()
        if not data or 'user_id' not in data:
            self.send_json_response(400, {"error": "Falta user_id"})
            return
        try:
            result = get_all_tickets()
            if result['success']:
                tickets = result['tickets']
                for ticket in tickets:
                    if 'created_at' in ticket and ticket['created_at']:
                        ticket['created_at'] = str(ticket['created_at'])
                self.send_json_response(200, {"tickets": tickets})
            else:
                self.send_json_response(500, {"error": result['error']})
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})

    def handle_update_ticket(self):
        data = self.get_json_body()
        if not data or not all(k in data for k in ['ticket_id', 'status']):
            self.send_json_response(400, {"error": "Faltan campos requeridos"})
            return
        valid_statuses = ['pendiente', 'atendido', 'cerrado']
        if data['status'] not in valid_statuses:
            self.send_json_response(400, {"error": "Estado no válido"})
            return
        response = data.get('response', None)
        result = update_ticket_status(data['ticket_id'], data['status'], response)
        if result['success']:
            self.send_json_response(200, {"message": "Estado actualizado"})
        else:
            self.send_json_response(404, {"error": result['error']})

    def handle_admin_users(self):
        data = self.get_json_body()
        if not data or 'user_id' not in data:
            self.send_json_response(400, {"error": "Falta user_id"})
            return
        result = get_all_users()
        if result['success']:
            self.send_json_response(200, {"users": result['users']})
        else:
            self.send_json_response(500, {"error": result['error']})

    def handle_update_role(self):
        data = self.get_json_body()
        if not data or not all(k in data for k in ['target_user_id', 'role_id']):
            self.send_json_response(400, {"error": "Faltan campos requeridos"})
            return
        if data['role_id'] not in [1, 2]:
            self.send_json_response(400, {"error": "Rol no válido"})
            return
        result = update_user_role(data['target_user_id'], data['role_id'])
        if result['success']:
            self.send_json_response(200, {"message": "Rol actualizado"})
        else:
            self.send_json_response(404, {"error": result['error']})

    def handle_delete_user(self):
        data = self.get_json_body()
        if not data or not all(k in data for k in ['admin_id', 'target_user_id']):
            self.send_json_response(400, {"error": "Faltan campos requeridos"})
            return
        if data['admin_id'] == data['target_user_id']:
            self.send_json_response(400, {"error": "No puedes eliminarte a ti mismo"})
            return
        result = delete_user(data['target_user_id'])
        if result['success']:
            self.send_json_response(200, {"message": "Usuario eliminado"})
        else:
            self.send_json_response(404, {"error": result['error']})

    def get_json_body(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            return json.loads(body.decode('utf-8'))
        except:
            return None

    def send_json_response(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def log_message(self, format, *args):
        print(f"{self.address_string()} - {format % args}")


def run_server():
    server = HTTPServer(('localhost', PORT), RequestHandler)
    print(f"Servidor corriendo en http://localhost:{PORT}")
    print("Presiona Ctrl+C para detener")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido")
        server.shutdown()


if __name__ == "__main__":
    run_server()