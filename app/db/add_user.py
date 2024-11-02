from firebase_config import db

# Define el correo del usuario
usuario_data = {
    "email": "danijorequem@gmail.com"
}

# Agrega el correo a la tabla 'usuarios' en Firebase
db.child("usuarios").push(usuario_data)

print("Usuario agregado exitosamente a Firebase")
