from backend.config.database import get_db_connection


def add_favorite(user_id, city_name, country, latitude, longitude):
    conn = get_db_connection()
    if not conn:
        return {"success": False, "error": "No se pudo conectar a la base de datos"}
    
    try:
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id FROM favorite_locations WHERE user_id = %s AND city_name = %s",
            (user_id, city_name)
        )
        if cursor.fetchone():
            return {"success": False, "error": "Esta ciudad ya está en tus favoritos"}
        
        query = """
            INSERT INTO favorite_locations (user_id, city_name, country, latitude, longitude)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (user_id, city_name, country, latitude, longitude))
        conn.commit()
        
        favorite_id = cursor.lastrowid
        cursor.close()
        conn.close()
        
        return {"success": True, "favorite_id": favorite_id}
    
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_user_favorites(user_id):
    conn = get_db_connection()
    if not conn:
        return {"success": False, "error": "No se pudo conectar a la base de datos"}
    
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM favorite_locations WHERE user_id = %s ORDER BY created_at DESC"
        cursor.execute(query, (user_id,))
        favorites = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return {"success": True, "favorites": favorites}
    
    except Exception as e:
        return {"success": False, "error": str(e)}


def delete_favorite(favorite_id, user_id):
    conn = get_db_connection()
    if not conn:
        return {"success": False, "error": "No se pudo conectar a la base de datos"}
    
    try:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM favorite_locations WHERE id = %s AND user_id = %s",
            (favorite_id, user_id)
        )
        conn.commit()
        
        deleted = cursor.rowcount > 0
        cursor.close()
        conn.close()
        
        if deleted:
            return {"success": True}
        return {"success": False, "error": "Favorito no encontrado"}
    
    except Exception as e:
        return {"success": False, "error": str(e)}