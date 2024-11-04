from flask import Blueprint, render_template, request, jsonify
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
        user_full_name = usuario.val().get("nombre_completo", "")
        break

    if usuario_id is None:
        return "Usuario no encontrado", 404

    # Obtener las conferencias a las que está inscrito el usuario
    relaciones = db.child("usuario_conferencia").order_by_child("usuario_id").equal_to(usuario_id).get()
    conferences_by_day = {}

    for relacion in relaciones.each():
        conferencia_id = relacion.val().get("conferencia_id")
        asistio = relacion.val().get("asistio", False)
        
        # Obtiene el tema de cada conferencia y el día
        conferencia = db.child("conferencias").child(conferencia_id).get()
        if conferencia.val():
            dia = conferencia.val().get("Dia", "")
            tema = conferencia.val().get("Tema", "")
            if dia not in conferences_by_day:
                conferences_by_day[dia] = []
            conferences_by_day[dia].append({
                "id": relacion.key(),
                "tema": tema,
                "asistio": asistio
            })

    # Definir el orden deseado de los días
    dia_orden = ["LUNES 4", "MARTES 5", "MIÉRCOLES 6", "JUEVES 7"]
    conferences_by_day = dict(sorted(conferences_by_day.items(), key=lambda x: dia_orden.index(x[0]) if x[0] in dia_orden else len(dia_orden)))

    # Renderizar el perfil con la información de conferencias ordenadas
    return render_template('profile.html', user_name=email, user_full_name=user_full_name, conferences_by_day=conferences_by_day)

# Ruta para actualizar el estado de asistencia
@app_routes.route('/update_assistance', methods=['POST'])
def update_assistance():
    data = request.get_json()
    relacion_id = data.get("relacion_id")
    attended = data.get("attended", False)

    # Actualiza el campo `asistio` con el valor especificado
    db.child("usuario_conferencia").child(relacion_id).update({"asistio": attended})
    return jsonify(success=True)
