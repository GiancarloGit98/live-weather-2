#Script de prueba 


from backend.config.database import get_db_connection

print("Probando conexion usando el modulo de configuracion...")
print()

conn = get_db_connection()

if conn:
    print("✓ Conexion exitosa a MySQL.")
    print()
    
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM roles ORDER BY id;")
    resultados = cursor.fetchall()
    
    print("Roles encontrados:")
    for fila in resultados:
        print(f"  ID: {fila[0]}, Nombre: {fila[1]}")
    
    cursor.close()
    conn.close()
    print()
    print("✓ Conexion cerrada correctamente.")
else:
    print("✗ No se pudo conectar a la base de datos.")