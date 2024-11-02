import qrcode

def generate_qr(email):
    # Crear un objeto QR Code con la información del email
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    # Agregar el email al código QR
    qr.add_data(email)
    qr.make(fit=True)

    # Crear una imagen del QR
    img = qr.make_image(fill="black", back_color="white")

    # Guardar la imagen con el email como nombre del archivo
    file_name = f"app/qrs/{email}_qr.png"
    img.save(file_name)
    print(f"Código QR generado y guardado como {file_name}")

email = "danijorequem@gmail.com"
generate_qr(email)
