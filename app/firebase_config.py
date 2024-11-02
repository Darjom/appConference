import pyrebase

# Configuración de Firebase
firebase_config = {
    "apiKey": "AIzaSyD4lCysT933MW815wH2lNzcfPM7HM5Vmos",
    "authDomain": "app-iie.firebaseapp.com",
    "databaseURL": "https://app-iie-default-rtdb.firebaseio.com/",
    "projectId": "app-iie",
    "storageBucket": "app-iie.firebasestorage.app",
    "messagingSenderId": "413177366841",
    "appId": "1:413177366841:web:aaab3ead83fc13c5b940e8",
    "measurementId": "G-SMBH5XWZN1"
}

# Inicializar Firebase
firebase = pyrebase.initialize_app(firebase_config)
db = firebase.database()  # Conexión a Firestore
auth = firebase.auth()    # Conexión a Authentication
