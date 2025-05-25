from flask import Blueprint, request, jsonify
from flask_cors import CORS
from app.services import create_evaluation, get_evaluation_details_by_software_id, get_evaluated_softwares_by_user, get_characteristic_summary_by_software

evaluation_routes = Blueprint('evaluation_routes', __name__)

CORS(evaluation_routes,
     origins=["http://localhost:5173", "http://127.0.0.1:5173"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"],
     supports_credentials=True)

@evaluation_routes.route('/evaluar', methods=['OPTIONS'])
def options_evaluar():
    response = jsonify({"status": "ok"})
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response, 200

@evaluation_routes.route('/evaluar', methods=['POST'])
def create_evaluation_route():
    try:
        data = request.get_json()
        evaluation, error = create_evaluation(data)
        print("Datos recibidos en /evaluar:", data)
        if error:
            print("Error en create_evaluation:", error)
            response = jsonify({'message': 'Error guardando la evaluación', 'error': error})
            response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
            return response, 400
        
        response = jsonify({'message': 'Evaluación guardada exitosamente', 'evaluation_id': evaluation.id})
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
        return response, 201
    except Exception as e:
        print("Excepción en /evaluar:", str(e))  
        response = jsonify({'message': 'Error interno del servidor', 'error': str(e)})
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
        return response, 500

@evaluation_routes.route('/detalle/<int:software_id>', methods=['GET'])
def get_evaluation_details(software_id):
    try:
        data = get_evaluation_details_by_software_id(software_id)
        if not data:
            return jsonify({'success': False, 'message': 'No se encontraron evaluaciones para este software'}), 404
        return jsonify(data), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@evaluation_routes.route('/software-evaluados/<int:user_id>', methods=['GET'])
def get_evaluated_softwares(user_id):
    try:
        data = get_evaluated_softwares_by_user(user_id)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@evaluation_routes.route('/resultados/<int:software_id>/<int:evaluation_id>', methods=['GET', 'OPTIONS'])
def get_software_characteristic_summary(software_id, evaluation_id):
    if request.method == 'OPTIONS':
        response = jsonify({"status": "ok"})
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response, 200
        
    try:
        data = get_characteristic_summary_by_software(software_id, evaluation_id)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500