import pandas as pd
from firebase_config import db

# Cargar el archivo Excel
file_path = "app/static/documents/EXPOSITORES.xlsx"  # Cambia esto a la ruta de tu archivo Excel
excel_data = pd.read_excel(file_path)

# Iterar sobre cada fila y subir los datos a Firebase
for index, row in excel_data.iterrows():
    conferencia_data = {
        "Dia": row["DIA"] if not pd.isna(row["DIA"]) else "",  # Asegurarse de que no sea NaN
        "Hora": row["HORA"] if not pd.isna(row["HORA"]) else "",
        "Expositor": row["EXPOSITOR"] if not pd.isna(row["EXPOSITOR"]) else "",
        "Tema": row["TEMA"] if not pd.isna(row["TEMA"]) else "",
        "Lugar": row["LUGAR"] if not pd.isna(row["LUGAR"]) else "",
        "Biografia": row["BIO"] if not pd.isna(row["BIO"]) else ""
    }

    # Subir cada conferencia a Firebase
    db.child("conferencias").push(conferencia_data)

print("Datos cargados exitosamente a Firebase")
