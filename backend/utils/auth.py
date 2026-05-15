#Script para manejar el hashing de contraseñas usando bcrypt

import bcrypt


def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

#verifica si la contraseña ingresada en texto plano coincide con el hash almacenado
def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


if __name__ == "__main__":
    # Prueba rapida
    test_password = "MiContraseña123"
    
    hashed = hash_password(test_password)
    print(f"Original: {test_password}")
    print(f"Hash: {hashed}")
    print(f"Verificacion correcta: {verify_password(test_password, hashed)}")
    print(f"Verificacion incorrecta: {verify_password('otra', hashed)}")