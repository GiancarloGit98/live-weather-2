from backend.config.database import get_db_connection


def create_support_ticket(user_id, phone, message):
    conn = get_db_connection()
    if not conn:
        return {"success": False, "error": "No se pudo conectar a la base de datos"}
    
    try:
        cursor = conn.cursor()
        query = """
            INSERT INTO support_tickets (user_id, phone, message, status)
            VALUES (%s, %s, %s, 'pendiente')
        """
        cursor.execute(query, (user_id, phone, message))
        conn.commit()
        
        ticket_id = cursor.lastrowid
        cursor.close()
        conn.close()
        
        return {"success": True, "ticket_id": ticket_id}
    
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_user_tickets(user_id):
    conn = get_db_connection()
    if not conn:
        return {"success": False, "error": "No se pudo conectar a la base de datos"}
    
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT id, phone, message, status, response, created_at
            FROM support_tickets
            WHERE user_id = %s
            ORDER BY created_at DESC
        """
        cursor.execute(query, (user_id,))
        tickets = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return {"success": True, "tickets": tickets}
    
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_all_tickets():
    conn = get_db_connection()
    if not conn:
        return {"success": False, "error": "No se pudo conectar a la base de datos"}
    
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT st.id, st.phone, st.message, st.status, st.created_at,
                   u.full_name, u.email
            FROM support_tickets st
            JOIN users u ON st.user_id = u.id
            ORDER BY st.created_at DESC
        """
        cursor.execute(query)
        tickets = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return {"success": True, "tickets": tickets}
    
    except Exception as e:
        return {"success": False, "error": str(e)}


def update_ticket_status(ticket_id, new_status, response=None):
    conn = get_db_connection()
    if not conn:
        return {"success": False, "error": "No se pudo conectar a la base de datos"}
    
    try:
        cursor = conn.cursor()
        
        if response:
            cursor.execute(
                "UPDATE support_tickets SET status = %s, response = %s WHERE id = %s",
                (new_status, response, ticket_id)
            )
        else:
            cursor.execute(
                "UPDATE support_tickets SET status = %s WHERE id = %s",
                (new_status, ticket_id)
            )
        
        conn.commit()
        
        updated = cursor.rowcount > 0
        cursor.close()
        conn.close()
        
        if updated:
            return {"success": True}
        return {"success": False, "error": "Ticket no encontrado"}
    
    except Exception as e:
        return {"success": False, "error": str(e)}