#script para manejar usuarios en la base de datos, incluyendo creación y autenticación

from backend.config.database import get_db_connection
from backend.utils.auth import hash_password, verify_password

# Función para crear un nuevo usuario
def create_user(email, password, full_name, role_id=1):
    conn = get_db_connection()
    if not conn:
        return {"success": False, "error": "No se pudo conectar a la base de datos"}
    
    try:
        cursor = conn.cursor()
        
        # Verificar si el email ya existe
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            return {"success": False, "error": "El correo ya está registrado"}
        
        # Hashear la contraseña y crear el usuario
        password_hash = hash_password(password)
        query = """
            INSERT INTO users (email, password_hash, full_name, role_id)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (email, password_hash, full_name, role_id))
        conn.commit()
        
        user_id = cursor.lastrowid
        cursor.close()
        conn.close()
        
        return {"success": True, "user_id": user_id}
    
    except Exception as e:
        return {"success": False, "error": str(e)}

# Función para obtener un usuario por su email
def get_user_by_email(email):
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        return user
    
    except Exception as e:
        print(f"Error al obtener usuario: {e}")
        return None

# Función para autenticar un usuario
def authenticate_user(email, password):
    user = get_user_by_email(email)
    
    if not user:
        return {"success": False, "error": "Credenciales incorrectas"}
    
    if verify_password(password, user['password_hash']):
        return {
            "success": True,
            "user": {
                "id": user['id'],
                "email": user['email'],
                "full_name": user['full_name'],
                "role_id": user['role_id']
            }
        }
    
    return {"success": False, "error": "Credenciales incorrectas"}


if __name__ == "__main__":
    # Prueba: crear un usuario
    print("Creando usuario de prueba...")
    result = create_user(
        email="prueba@test.com",
        password="12345",
        full_name="Usuario de Prueba"
    )
    print(f"Resultado: {result}")
    
    if result['success']:
        # Prueba: autenticar con credenciales correctas
        print("\nProbando autenticacion correcta...")
        auth = authenticate_user("prueba@test.com", "12345")
        print(f"Resultado: {auth}")
        
        # Prueba: autenticar con credenciales incorrectas
        print("\nProbando autenticacion incorrecta...")
        auth_fail = authenticate_user("prueba@test.com", "incorrecta")
        print(f"Resultado: {auth_fail}")

def get_all_users():
    conn = get_db_connection()
    if not conn:
        return {"success": False, "error": "No se pudo conectar a la base de datos"}
    
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT u.id, u.email, u.full_name, u.role_id, u.created_at,
                   r.name as role_name
            FROM users u
            JOIN roles r ON u.role_id = r.id
            ORDER BY u.created_at DESC
        """
        cursor.execute(query)
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        
        for user in users:
            if 'created_at' in user and user['created_at']:
                user['created_at'] = str(user['created_at'])
        
        return {"success": True, "users": users}
    except Exception as e:
        return {"success": False, "error": str(e)}


def update_user_role(user_id, role_id):
    conn = get_db_connection()
    if not conn:
        return {"success": False, "error": "No se pudo conectar a la base de datos"}
    
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET role_id = %s WHERE id = %s",
            (role_id, user_id)
        )
        conn.commit()
        updated = cursor.rowcount > 0
        cursor.close()
        conn.close()
        
        if updated:
            return {"success": True}
        return {"success": False, "error": "Usuario no encontrado"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def delete_user(user_id):
    conn = get_db_connection()
    if not conn:
        return {"success": False, "error": "No se pudo conectar a la base de datos"}
    
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        deleted = cursor.rowcount > 0
        cursor.close()
        conn.close()
        
        if deleted:
            return {"success": True}
        return {"success": False, "error": "Usuario no encontrado"}
    except Exception as e:
        return {"success": False, "error": str(e)}