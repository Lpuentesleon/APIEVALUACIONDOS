from flask import Flask, request, jsonify
import requests
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

tokens_activos = {}

def validar_token(request):
    token = request.headers.get("Authorization")
    if not token:
        return None

    token = token.replace("Bearer ", "")
    return tokens_activos.get(token)

@app.route('/')
def home():
    return '''
    <h1>API EVALUACIÓN 2 - FERREMAS</h1>
    <p>Desarrollada por Luis Puentes y Alejandro Ruiz</p>
    <p>Endpoints disponibles: /autenticarUsuario, /articulos, /pedido, etc.</p>
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

BASE_URL = "https://ea2p2assets-production.up.railway.app"
FERREMAS_TOKEN = "SaGrP9ojGS39hU9ljqbXxQ=="
HEADERS_FERREMAS = {
    "x-authentication": FERREMAS_TOKEN
}

@app.route('/articulos', methods=['GET'])
def obtener_articulos():
    url = f"{BASE_URL}/data/articulos"
    response = requests.get(url, headers=HEADERS_FERREMAS)
    return jsonify(response.json()), response.status_code

@app.route('/articulo/<int:articulo_id>', methods=['GET'])
def obtener_articulo(articulo_id):
    url = f"{BASE_URL}/data/articulos/{articulo_id}"
    response = requests.get(url, headers=HEADERS_FERREMAS)
    return jsonify(response.json()), response.status_code

@app.route('/sucursales', methods=['GET'])
def obtener_sucursales():
    url = f"{BASE_URL}/data/sucursales"
    response = requests.get(url, headers=HEADERS_FERREMAS)
    return jsonify(response.json()), response.status_code

@app.route('/sucursal/<int:sucursal_id>', methods=['GET'])
def obtener_sucursal(sucursal_id):
    url = f"{BASE_URL}/data/sucursales/{sucursal_id}"
    response = requests.get(url, headers=HEADERS_FERREMAS)
    return jsonify(response.json()), response.status_code

@app.route('/vendedores', methods=['GET'])
def obtener_vendedores():
    url = f"{BASE_URL}/data/vendedores"
    response = requests.get(url, headers=HEADERS_FERREMAS)
    return jsonify(response.json()), response.status_code

@app.route('/vendedor/<int:vendedor_id>', methods=['GET'])
def obtener_vendedor(vendedor_id):
    url = f"{BASE_URL}/data/vendedores/{vendedor_id}"
    response = requests.get(url, headers=HEADERS_FERREMAS)
    return jsonify(response.json()), response.status_code

@app.route('/articulo/venta/<int:articulo_id>', methods=['PUT'])
def marcar_articulo_vendido(articulo_id):
    url = f"{BASE_URL}/data/articulos/venta/{articulo_id}"
    response = requests.put(url, headers=HEADERS_FERREMAS)
    return jsonify(response.json()), response.status_code

@app.route('/pedido', methods=['POST'])
def crear_pedido():
    data = request.json
    url = f"{BASE_URL}/data/pedidos/nuevo"
    headers = {
        "x-authentication": FERREMAS_TOKEN,
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, json=data)
    return jsonify(response.json()), response.status_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8000)))
