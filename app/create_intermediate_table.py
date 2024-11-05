import pandas as pd
import qrcode
import smtplib
import os
from dotenv import load_dotenv
from firebase_config import db
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

# Obtener la ruta absoluta al directorio actual del script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construir la ruta al archivo .env en la raíz del proyecto
dotenv_path = os.path.join(current_dir, '..', '.env')

# Cargar las variables de entorno desde .env
load_dotenv()



# Ruta para almacenar los QR generados
QR_DIR = "qrs/"
os.makedirs(QR_DIR, exist_ok=True)

# Configuración del servidor SMTP desde variables de entorno
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

print(f"SMTP_SERVER: {SMTP_SERVER}")
print(f"SMTP_PORT: {SMTP_PORT}")
print(f"SMTP_USER: {SMTP_USER}")
print(f"SMTP_PASSWORD: {SMTP_PASSWORD}")


# Leer el archivo Excel
def obtener_datos_inscripcion(ruta_excel):
    return pd.read_excel(ruta_excel)

# Función para verificar si existe la conexión en la tabla intermedia
def existe_conexion(usuario_id, conferencia_id):
    registros = db.child("usuario_conferencia").order_by_child("usuario_id").equal_to(usuario_id).get()
    for registro in registros.each():
        if registro.val().get("conferencia_id") == conferencia_id:
            return True
    return False

# Función para generar y guardar el código QR
def generar_qr(email):
    qr = qrcode.make(email)
    qr_path = os.path.join(QR_DIR, f"{email}.png")
    qr.save(qr_path)
    return qr_path

# Función para enviar el correo con el QR adjunto
def enviar_correo(correo_destino, qr_path):
    mensaje = MIMEMultipart()
    mensaje["From"] = SMTP_USER
    mensaje["To"] = correo_destino
    mensaje["Subject"] = "Confirmación de inscripción - Semana Empresarial"

    # Cuerpo del correo
    cuerpo = """
    Estimado/a participante,

    Su inscripción para la Semana Empresarial ha sido confirmada exitosamente.
    Adjunto encontrará un código QR que funcionará como su pase de entrada.

    Por favor, presente este código QR en la entrada del evento para acceder.

    ¡Gracias por ser parte de este evento!

    Saludos cordiales,
    Centro Estudiantil Kainos
    """
    mensaje.attach(MIMEText(cuerpo, "plain"))

    # Adjuntar el QR
    with open(qr_path, "rb") as qr_file:
        img = MIMEImage(qr_file.read())
        img.add_header("Content-Disposition", f"attachment; filename={os.path.basename(qr_path)}")
        mensaje.attach(img)

    # Enviar el correo
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, correo_destino, mensaje.as_string())
        print(f"Correo enviado a {correo_destino}")
    except Exception as e:
        print(f"Error al enviar correo a {correo_destino}: {e}")

# Función principal para registrar usuarios y conferencias
def registrar_usuarios_conferencias(ruta_excel):
    inscripciones = obtener_datos_inscripcion(ruta_excel)

    for _, inscripcion_data in inscripciones.iterrows():
        email = inscripcion_data["Correo electrónico"]
        nombre_completo = inscripcion_data["Nombre Completo"]
        celular = str(inscripcion_data["Celular"])
        tipo_inscripcion = inscripcion_data["A cuantas conferencias desea inscribirse?"]
        dia = inscripcion_data.get("¿Que día de la Semana Empresarial asistiras?", None)
        conferencia_deseada = inscripcion_data.get("¿Qué conferencia deseas inscribirte?", None)

        # Paso 1: Verificar si el usuario ya existe en Firebase
        usuarios = db.child("usuarios").order_by_child("email").equal_to(email).get()
        usuario_id = None

        for usuario in usuarios.each():
            usuario_id = usuario.key()
            break

        if usuario_id is None:
            # Si el usuario no existe, agregarlo a la base de datos
            nuevo_usuario = {
                "email": email,
                "nombre_completo": nombre_completo,
                "celular": celular
            }
            usuario_id = db.child("usuarios").push(nuevo_usuario)["name"]
            print(f"Nuevo usuario agregado con ID: {usuario_id}")

            # Generar y guardar el QR
            qr_path = generar_qr(email)
            print(f"Código QR generado en: {qr_path}")

            # Enviar correo con el QR adjunto
            enviar_correo(email, qr_path)
        else:
            print(f"Usuario ya existe con ID: {usuario_id}")

        # Procesar el tipo de inscripción
        if tipo_inscripcion == "Una sola conferencia" and conferencia_deseada:
            expositor_tema = conferencia_deseada.split(":")[0].strip()
            expositor_tema = expositor_tema.replace("’", "´")  # Normalizar el nombre del expositor
            print(f"Buscando conferencias para el expositor: {expositor_tema}")

            conferencias = db.child("conferencias").order_by_child("Expositor").equal_to(expositor_tema).get()
            for conferencia in conferencias.each():
                conferencia_id = conferencia.key()
                print(f"Conferencia encontrada - ID: {conferencia_id}, Expositor: {conferencia.val().get('Expositor')}")
                if not existe_conexion(usuario_id, conferencia_id):
                    registro = {
                        "usuario_id": usuario_id,
                        "conferencia_id": conferencia_id,
                        "asistio": False
                    }
                    result = db.child("usuario_conferencia").push(registro)
                    print("Registro añadido con ID:", result['name'])
                else:
                    print(f"Conexión ya existe para usuario {usuario_id} y conferencia {conferencia_id}")

        elif tipo_inscripcion == "Pase completo por toda la Semana Empresarial":
            # Obtener todas las conferencias e inscribir al usuario en todas
            conferencias = db.child("conferencias").get()
            for conferencia in conferencias.each():
                conferencia_id = conferencia.key()
                if not existe_conexion(usuario_id, conferencia_id):
                    registro = {
                        "usuario_id": usuario_id,
                        "conferencia_id": conferencia_id,
                        "asistio": False
                    }
                    result = db.child("usuario_conferencia").push(registro)
                    print("Registro añadido con ID:", result['name'])
                else:
                    print(f"Conexión ya existe para usuario {usuario_id} y conferencia {conferencia_id}")

        elif tipo_inscripcion == "Pase completo por día" and dia:
            # Convertir el valor del día al formato esperado en Firebase (e.g., "LUNES 4")
            dia_split = dia.split(" ")
            dia_formato = f"{dia_split[0].upper()} {dia_split[1]}"
            print(f"Buscando conferencias para el día: {dia_formato}")

            # Obtener todas las conferencias que coincidan con el día
            conferencias = db.child("conferencias").order_by_child("Dia").equal_to(dia_formato).get()
            
            if conferencias.each() is None:
                print(f"No se encontraron conferencias para el día: {dia_formato}")
            else:
                for conferencia in conferencias.each():
                    conferencia_id = conferencia.key()
                    print(f"Conferencia encontrada - ID: {conferencia_id}, Día: {conferencia.val().get('Dia')}")
                    if not existe_conexion(usuario_id, conferencia_id):
                        registro = {
                            "usuario_id": usuario_id,
                            "conferencia_id": conferencia_id,
                            "asistio": False
                        }
                        result = db.child("usuario_conferencia").push(registro)
                        print("Registro añadido con ID:", result['name'])
                    else:
                        print(f"Conexión ya existe para usuario {usuario_id} y conferencia {conferencia_id}")



# Ejecuta la función principal con la ruta del archivo Excel
ruta_excel = "app/static/documents/inscripciones.xlsx"
registrar_usuarios_conferencias(ruta_excel)
