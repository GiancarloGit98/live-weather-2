import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

connection = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT")),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    ssl_disabled=False
)

cursor = connection.cursor()
cursor.execute("UPDATE users SET role_id = 2 WHERE email = '15giancarlomoreno@gmail.com'")
connection.commit()
print(f"✅ {cursor.rowcount} usuario actualizado a administrador")
cursor.close()
connection.close()