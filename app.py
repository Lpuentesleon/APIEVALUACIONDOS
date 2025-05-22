from flask import Flask, request, jsonify
import os

app = Flask(__name__)

usuarios = {
    "javier_thompson": {
        "password": "aONF4d6aNBIxRjlgjBRRzrS",
        "rol": "admin"
    },
    "ignacio_tapia": {
        "password": "f7rWChmQS1JYfThT",
        "rol": "client"
    },
    "stripe_sa": {
        "password": "dzkQqDL9XZH33YDzhmsf",
        "rol": "service_account"
    }
}

def validar_token(request):
    token = request.headers.get("Authorization")
    if not token:
        return None

    token = token.replace("Bearer ", "")
    return tokens_activos.get(token)

tokens_activos = {}

@app.route('/')
def home():
    return '''
    <h1>API EVALUACIÓN 2 - FERREMAS</h1>
    <p>Desarrollada por Luis Puentes y Alejandro Ruiz</p>
    <p>Endpoints disponibles: /autenticarUsuario, /productos, /pagos/crearIntento, /conversionDivisas, etc.</p>
    '''

@app.route('/autenticarUsuario', methods=['POST'])
def autenticar_usuario():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Faltan datos"}), 400

    user = usuarios.get(username)
    if not user or user["password"] != password:
        return jsonify({"error": "Credenciales inválidas"}), 401

    token = f"token-{username}"
    tokens_activos[token] = {
        "usuario": username,
        "rol": user["rol"]
    }

    return jsonify({
        "token": token,
        "usuario": username,
        "rol": user["rol"]
    })

@app.route('/soloAdmin', methods=['GET'])
def solo_admin():
    user_info = validar_token(request)
    if not user_info:
        return jsonify({"error": "Token inválido o ausente"}), 401

    if user_info["rol"] != "admin":
        return jsonify({"error": "Acceso denegado: no eres admin"}), 403

    return jsonify({"mensaje": "Acceso permitido solo a administradores."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8000)))
