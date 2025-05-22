from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <h1>API EVALUACIÓN 2 - FERREMAS</h1>
    <p>Desarrollada por Luis Puentes y Alejandro Ruiz</p>
    <p>Endpoints disponibles: /autenticarUsuario, /productos, /pagos/crearIntento, /conversionDivisas, etc.</p>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8000)))
