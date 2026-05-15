#Informacion para acceder a la base de datos.

import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Configuracion de la base de datos
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT")),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
}

#Realiza la conexion a la base de datos.
def get_db_connection():

    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return None

#Funcion auxiliar, pueba que la conexión funciona y la cierra inmediatamente.
def test_connection():
  
    conn = get_db_connection()
    if conn and conn.is_connected():
        print("✓ Conexion a MySQL exitosa")
        conn.close()
        return True
    else:
        print("✗ No se pudo conectar a MySQL")
        return False


# Bloque que se ejecuta solo si se corre este archivo directamente
if __name__ == "__main__":
    print("Probando conexion a la base de datos...")
    test_connection()