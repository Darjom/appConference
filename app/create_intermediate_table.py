from firebase_config import db

# Paso 1: Obtener el ID del usuario
# Consulta el ID del usuario con el email "danijorequem@gmail.com"
usuarios = db.child("usuarios").order_by_child("email").equal_to("danijorequem@gmail.com").get()
usuario_id = None

for usuario in usuarios.each():
    usuario_id = usuario.key()  # Obtener el ID del usuario
    break

# Comprobar si el usuario existe
if usuario_id is None:
    print("No se encontró el usuario con el correo especificado.")
else:
    # Paso 2: Obtener los IDs de las conferencias deseadas
    temas_deseados = [
        "Más que Trabajo: Creando Experiencias Memorables para el Equipo",
        "Mi aventura en la ruta del emprendimiento",
        "Triple impacto en Bolivia. Caso Mamut"
    ]
    
    conferencias = db.child("conferencias").get()
    conferencia_ids = []

    # Agregamos prints para depuración
    print("Temas deseados:", temas_deseados)
    print("Conferencias encontradas en Firebase:")

    for conferencia in conferencias.each():
        tema_conferencia = conferencia.val().get("Tema")
        print(f"Revisando tema de conferencia: {tema_conferencia}")
        
        # Verificar si el tema de la conferencia está en temas_deseados
        if tema_conferencia in temas_deseados:
            conferencia_ids.append(conferencia.key())
            print(f"Conferencia encontrada: {tema_conferencia} con ID: {conferencia.key()}")

    # Verificar los IDs de conferencia obtenidos
    print("Conferencia IDs encontrados:", conferencia_ids)

    # Paso 3: Crear la tabla intermedia y hacer push de cada registro
    for conferencia_id in conferencia_ids:
        registro = {
            "usuario_id": usuario_id,
            "conferencia_id": conferencia_id,
            "asistio": False
        }
        # Hacer push de cada registro para asegurarse de que se crea una entrada única
        result = db.child("usuario_conferencia").push(registro)
        print("Registro añadido con ID:", result['name'])

    print("Tabla intermedia creada y datos insertados exitosamente.")
