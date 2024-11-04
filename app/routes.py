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
        user_full_name = usuario.val().get("nombre_completo")  # Agrega el nombre completo
        break

    if usuario_id is None:
        return "Usuario no encontrado", 404

    # Obtener las conferencias a las que está inscrito el usuario
    relaciones = db.child("usuario_conferencia").order_by_child("usuario_id").equal_to(usuario_id).get()
    conferences_by_day = {}

    for relacion in relaciones.each():
        conferencia_id = relacion.val().get("conferencia_id")
        asistio = relacion.val().get("asistio", False)
        
        # Obtiene el tema y el día de cada conferencia
        conferencia = db.child("conferencias").child(conferencia_id).get()
        if conferencia.val():
            dia = conferencia.val().get("Dia", "Sin especificar")  # Asegúrate de que el campo `Dia` esté disponible
            tema = conferencia.val().get("Tema")

            # Inicializar el día en el diccionario si no existe
            if dia not in conferences_by_day:
                conferences_by_day[dia] = []
            
            # Agregar la conferencia a la lista del día correspondiente
            conferences_by_day[dia].append({
                "id": relacion.key(),  # ID de la relación en `usuario_conferencia`
                "tema": tema,
                "asistio": asistio
            })

    # Renderizar el perfil con la información de conferencias
    return render_template(
        'profile.html',
        user_name=email,
        user_full_name=user_full_name,
        conferences_by_day=conferences_by_day
    )

# Ruta para actualizar el estado de asistencia
@app_routes.route('/update_assistance', methods=['POST'])
def update_assistance():
    data = request.get_json()
    relacion_id = data.get("relacion_id")
    attended = data.get("attended", True)  # Permite actualizar `attended` como True o False

    # Actualiza el campo `asistio` con el valor de `attended` para la relación especificada
    db.child("usuario_conferencia").child(relacion_id).update({"asistio": attended})
    return jsonify(success=True)
