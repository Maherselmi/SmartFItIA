from flask import Blueprint, jsonify, request
from models import Coach, Planning
from ai_planning import generate_smart_planning
from ai_performance import train_performance_model, predict_rating
import pandas as pd
from database import db

ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')

@ai_bp.route('/generate_planning', methods=['GET'])
def smart_planning():
    try:
        coaches = [c.to_dict() for c in Coach.query.all()]
        planning = generate_smart_planning(coaches)
        return jsonify(planning), 200
    except Exception as e:
        return jsonify({"error": f"Erreur génération planning: {str(e)}"}), 500

@ai_bp.route('/predict_performance', methods=['POST'])
def predict_performance():
    try:
        data = request.get_json()
        client_count = data.get('client_count')
        if client_count is None:
            return jsonify({"error": "client_count is required"}), 400

        model = train_performance_model()
        X_new = pd.DataFrame({"client_count": [client_count]})
        rating_pred = model.predict(X_new)[0]

        return jsonify({"predicted_rating": rating_pred}), 200
    except Exception as e:
        return jsonify({"error": f"Erreur prédiction: {str(e)}"}), 500

@ai_bp.route('/generate_planning/<int:coach_id>', methods=['GET'])
def smart_planning_coach(coach_id):
    try:
        coach = Coach.query.get(coach_id)
        if not coach:
            return jsonify({"error": "Coach not found"}), 404

        # Vérifier si le coach est disponible (si le champ existe)
        if hasattr(coach, 'is_available') and not coach.is_available:
            return jsonify({"error": "Coach non disponible"}), 400

        planning = generate_smart_planning([coach.to_dict()])

        return jsonify({
            "message": "Planning généré avec succès",
            "coach_id": coach_id,
            "planning": planning
        }), 200

    except Exception as e:
        return jsonify({"error": f"Erreur lors de la génération: {str(e)}"}), 500