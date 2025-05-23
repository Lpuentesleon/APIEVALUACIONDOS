from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv
import stripe
from datetime import datetime
from flasgger import Swagger

load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

BCCH_USER = os.getenv("BCCH_USER")
BCCH_PASS = os.getenv("BCCH_PASS")

app = Flask(__name__)
swagger = Swagger(app)

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
    """
    Autenticar usuario
    ---
    summary: inicio de sesión
    description: permite ingresar con nombre de usuario y contraseña.
    responses:
      200:
        description: usuario autenticado correctamente
      400:
        description: Faltan datos en la solicitud
      401:
        description: credenciales incorrectas
    """
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
    """
    Acceso exclusivo para administradores
    ---
    summary: Verificacion de rol administrador
    description: Devuelve el mensaje si el usuario autenticado tiene rol admin.
    responses:
      200:
        description: acceso permitido
      400:
        description: token invalido o ausente
      401:
        description: usuario no tiene permisos de administrador
    """
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

def manejar_respuesta(response, nombre_recurso="recurso"):
    if response.status_code == 404:
        return jsonify({"error": f"{nombre_recurso.capitalize()} no encontrado"}), 404
    try:
        if "application/json" in response.headers.get("Content-Type", ""):
            return jsonify(response.json()), response.status_code
        else:
            return jsonify({"error": "Respuesta inesperada del servidor externo"}), 502
    except Exception as e:
        return jsonify({"error": f"Error al procesar respuesta: {str(e)}"}), 500

@app.route('/articulos', methods=['GET'])
def obtener_articulos():
    """
    Obtener articulos
    ---
    summary: listar articulos
    description: devuelve todos los articulos disponibles desde FERREMAS.
    responses:
      200:
        description: lista de articulos
      500:
        description: error al conectar
    """
    url = f"{BASE_URL}/data/articulos"
    try:
        response = requests.get(url, headers=HEADERS_FERREMAS)
        return manejar_respuesta(response, "artículos")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/articulo/<articulo_id>', methods=['GET'])
def obtener_articulo(articulo_id):
    """
    Obtener articulo por ID
    ---
    summary: detalle de articulo
    description: devuelve los datos de un articulo especifico segun su ID.
    responses:
      200:
        description: articulo encontrado
      404:
        description: no encontrado
    """
    url = f"{BASE_URL}/data/articulos/{articulo_id}"
    try:
        response = requests.get(url, headers=HEADERS_FERREMAS)
        return manejar_respuesta(response, "artículo")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/sucursales', methods=['GET'])
def obtener_sucursales():
    """
    Obtener sucursales
    ---
    summary: listar sucursales
    description: retorna todas las sucursales registradas.
    responses:
      200:
        description: lista de sucursales
    """
    url = f"{BASE_URL}/data/sucursales"
    try:
        response = requests.get(url, headers=HEADERS_FERREMAS)
        return manejar_respuesta(response, "sucursales")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/sucursal/<sucursal_id>', methods=['GET'])
def obtener_sucursal(sucursal_id):
    """
    Obtener sucursal por ID
    ---
    summary: detalle de sucursal
    description: muestra la informacion de una sucursal especifica.
    responses:
      200:
        description: Datos de la sucursal
    """
    url = f"{BASE_URL}/data/sucursales/{sucursal_id}"
    try:
        response = requests.get(url, headers=HEADERS_FERREMAS)
        return manejar_respuesta(response, "sucursal")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/vendedores', methods=['GET'])
def obtener_vendedores():
    """
    Obtener vendedores
    ---
    summary: listar vendedores
    description: devuelve todos los vendedores registrados.
    responses:
      200:
        description: lista de vendedores
    """
    url = f"{BASE_URL}/data/vendedores"
    try:
        response = requests.get(url, headers=HEADERS_FERREMAS)
        return manejar_respuesta(response, "vendedores")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/vendedor/<vendedor_id>', methods=['GET'])
def obtener_vendedor(vendedor_id):
    """
    Obtener vendedor por ID
    ---
    summary: detalle de vendedor
    description: muestra informacion de un vendedor por su ID.
    responses:
      200:
        description: datos del vendedor
    """
    url = f"{BASE_URL}/data/vendedores/{vendedor_id}"
    try:
        response = requests.get(url, headers=HEADERS_FERREMAS)
        return manejar_respuesta(response, "vendedor")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/articulo/venta/<articulo_id>', methods=['PUT'])
def marcar_articulo_vendido(articulo_id):
    """
    Marcar articulo como vendido
    ---
    summary: registrar venta
    description: Marca un articulo como vendido segun la cantidad.
    responses:
      200:
        description: venta registrada
      400:
        description: falta el parametro cantidad
    """
    cantidad = request.args.get("cantidad")

    if not cantidad:
        return jsonify({"error": "El parámetro 'cantidad' es obligatorio"}), 400

    url = f"{BASE_URL}/data/articulos/venta/{articulo_id}?cantidad={cantidad}"
    try:
        response = requests.put(url, headers=HEADERS_FERREMAS)
        return manejar_respuesta(response, "venta")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/pedido', methods=['POST'])
def crear_pedido():
    """
    Crear pedido
    ---
    summary: nuevo pedido
    description: crea un pedido indicando sucursal, articulo y cantidad.
    responses:
      200:
        description: pedido creado
      400:
        description: faltan campos requeridos
    """
    data = request.json

    campos_obligatorios = ["sucursal", "articulo", "cantidad"]
    for campo in campos_obligatorios:
        if campo not in data:
            return jsonify({"error": f"Falta el campo obligatorio: {campo}"}), 400

    url = f"{BASE_URL}/data/pedidos/nuevo"
    headers = {
        "x-authentication": FERREMAS_TOKEN,
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        return manejar_respuesta(response, "pedido")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

from datetime import datetime
from flask import request

@app.route('/conversionDivisas', methods=['GET'])
def conversion_divisas():
    """
    Conversion CLP/USD
    ---
    summary: convertir divisas
    description: devuelve el valor CLP/USD actual y permite convertir montos.
    responses:
      200:
        description: conversion realizada
      400:
        description: tipo de conversoón no valido
    """
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")

    url = (
        f"https://si3.bcentral.cl/SieteRestWS/SieteRestWS.ashx?"
        f"user={BCCH_USER}&pass={BCCH_PASS}"
        f"&function=GetSeries&timeseries=F073.TCO.PRE.Z.D"
        f"&firstdate={fecha_hoy}&lastdate={fecha_hoy}"
    )

    try:
        response = requests.get(url)

        if response.status_code != 200:
            return jsonify({"error": "No se pudo obtener datos del BCCh"}), 502

        data = response.json()
        obs = data.get("Series", {}).get("Obs", [])

        if not obs:
            return jsonify({"error": "No hay datos disponibles para hoy"}), 404

        tasa = float(obs[0]["value"])

        monto = request.args.get("monto", type=float)
        tipo = request.args.get("tipo")

        resultado = {
            "moneda_origen": "CLP",
            "moneda_destino": "USD",
            "tasa": tasa
        }

        if monto and tipo:
            if tipo == "CLPtoUSD":
                resultado["monto_original"] = monto
                resultado["monto_convertido"] = round(monto / tasa, 2)
            elif tipo == "USDtoCLP":
                resultado["moneda_origen"] = "USD"
                resultado["moneda_destino"] = "CLP"
                resultado["monto_original"] = monto
                resultado["monto_convertido"] = round(monto * tasa, 2)
            else:
                return jsonify({"error": "Tipo de conversión no válido. Usa CLPtoUSD o USDtoCLP"}), 400

        return jsonify(resultado)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/pagos/crearIntento', methods=['POST'])
def crear_intento_pago():
    """
    Crear intento de pago
    ---
    summary: pago con stripe
    description: crea un intento de pago y devuelve el ID y client_secret.
    responses:
      200:
        description: intento de pago creado
      400:
        description: falta el monto
    """
    data = request.json
    monto = data.get("monto")

    if not monto:
        return jsonify({"error": "Debe enviar el monto"}), 400

    try:
        intento = stripe.PaymentIntent.create(
            amount=int(monto),
            currency="clp",
            payment_method_types=["card"]
        )

        return jsonify({
            "id": intento["id"],
            "client_secret": intento["client_secret"]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8000)))
