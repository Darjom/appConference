from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from .firebase_config import db

app_routes = Blueprint("app_routes", __name__)

@app_routes.route('/')
def scan_qr():
    return render_template('scan_qr.html')

@app_routes.route('/profile/<email>')
def profile(email):
    # Busca el usuario en Firebase con el correo escaneado
    usuarios = db.child("usuarios").order_by_child("email").equal_to(email).get()
    usuario_id = None

    for usuario in usuarios.each():
        usuario_id = usuario.key()  # Extrae el ID del usuario
        break

    if usuario_id is None:
        return "Usuario no encontrado", 404

    # Obtener las conferencias a las que está inscrito el usuario
    relaciones = db.child("usuario_conferencia").order_by_child("usuario_id").equal_to(usuario_id).get()
    conferencias = []

    for relacion in relaciones.each():
        conferencia_id = relacion.val().get("conferencia_id")
        asistio = relacion.val().get("asistio", False)
        
        # Obtiene el tema de cada conferencia
        conferencia = db.child("conferencias").child(conferencia_id).get()
        if conferencia.val():
            conferencias.append({
                "id": relacion.key(),  # ID de la relación en `usuario_conferencia`
                "tema": conferencia.val().get("Tema"),
                "asistio": asistio
            })

    # Renderizar el perfil con la información de conferencias
    return render_template('profile.html', user_name=email, conferences=conferencias)

# Ruta para actualizar el estado de asistencia
@app_routes.route('/update_assistance', methods=['POST'])
def update_assistance():
    data = request.get_json()
    relacion_id = data.get("relacion_id")

    # Actualiza el campo `asistio` a true para la relación especificada
    db.child("usuario_conferencia").child(relacion_id).update({"asistio": True})
    return jsonify(success=True)
