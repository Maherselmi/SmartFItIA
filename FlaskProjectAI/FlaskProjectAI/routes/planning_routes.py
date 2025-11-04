import datetime
from flask import Blueprint, jsonify, request
from database import db
from models import Planning, Coach
from sqlalchemy import desc

from services.planning_service import assign_coach

planning_bp = Blueprint('planning', __name__, url_prefix='/api/plannings')


# Récupérer tous les plannings d'un coach
@planning_bp.route('/<int:coach_id>', methods=['GET'])
def get_planning_by_coach(coach_id):
    try:
        print(f"🔍 Recherche planning pour coach_id: {coach_id}")

        coach = Coach.query.get(coach_id)
        if not coach:
            return jsonify({"success": False, "error": f"Coach avec ID {coach_id} non trouvé"}), 404

        plannings = Planning.query.filter_by(coach_id=coach_id).order_by(Planning.date.asc()).all()
        print(f"📊 Nombre de plannings trouvés: {len(plannings)}")

        planning_list = []
        for planning in plannings:
            print(f"📅 Planning ID: {planning.id}, Date: {planning.date}, Session: {planning.session}")
            planning_list.append({
                'id': planning.id,
                'date': planning.date.isoformat() if planning.date else None,
                'session': planning.session or 'Session non définie',
                'coach_id': planning.coach_id,
                'coach_nom': f"{coach.prenom} {coach.nom}"
            })

        return jsonify({
            "success": True,
            "coach_name": f"{coach.prenom} {coach.nom}",
            "count": len(planning_list),
            "plannings": planning_list
        }), 200

    except Exception as e:
        print(f"❌ Erreur récupération planning: {str(e)}")
        return jsonify({"success": False, "error": f"Erreur récupération planning: {str(e)}"}), 500


# Route pour debug - voir tous les plannings de la base
@planning_bp.route('/debug/all', methods=['GET'])
def debug_all_plannings():
    try:
        all_plannings = Planning.query.order_by(Planning.coach_id, Planning.date).all()
        result = []
        for p in all_plannings:
            coach = Coach.query.get(p.coach_id)
            result.append({
                'id': p.id,
                'date': p.date.isoformat() if p.date else None,
                'session': p.session,
                'coach_id': p.coach_id,
                'coach_name': f"{coach.prenom} {coach.nom}" if coach else 'Inconnu'
            })

        return jsonify({"total_plannings": len(all_plannings), "plannings_by_coach": result}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Route debug pour un coach spécifique
@planning_bp.route('/debug/coach/<int:coach_id>', methods=['GET'])
def debug_coach_plannings(coach_id):
    try:
        print(f"🔍 DEBUG - Recherche planning pour coach_id: {coach_id}")
        total_count = Planning.query.filter_by(coach_id=coach_id).count()
        print(f"📊 DEBUG - Total plannings en base: {total_count}")

        plannings = Planning.query.filter_by(coach_id=coach_id).all()
        planning_details = []
        for p in plannings:
            planning_details.append({
                'planning_id': p.id,
                'date': p.date.isoformat() if p.date else None,
                'session': p.session,
                'coach_id': p.coach_id
            })

        return jsonify({
            "coach_id": coach_id,
            "total_in_database": total_count,
            "plannings_retrieved": len(plannings),
            "plannings": planning_details
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@planning_bp.route('/detailed/<int:coach_id>', methods=['GET'])
def get_detailed_planning(coach_id):
    coach = Coach.query.get(coach_id)
    if not coach:
        return jsonify({"success": False, "error": "Coach non trouvé"}), 404

    # Récupérer toutes les séances du coach
    plannings = Planning.query.filter_by(coach_id=coach_id).order_by(Planning.date.asc()).all()
    planning_list = []

    # 🔹 Boucle corrigée pour gérer correctement la date
    from datetime import datetime
    for p in plannings:
        # Convertir la date en datetime si nécessaire
        if not isinstance(p.date, datetime):
            try:
                p_date = datetime.strptime(str(p.date), "%Y-%m-%d")
            except:
                p_date = None
        else:
            p_date = p.date

        date_str = p_date.strftime("%Y-%m-%d") if p_date else str(p.date)
        day_name = p_date.strftime("%A") if p_date else "Inconnu"

        planning_list.append({
            "Date": date_str,
            "Jour": day_name,
            "Session": p.session,
            "Type de Séance": coach.specialite or "Non défini",
            "Durée": "1h"
        })

    return jsonify({
        "coach_name": f"{coach.prenom} {coach.nom}",
        "total_seances": len(plannings),
        "planning": planning_list
    }), 200



@planning_bp.route('/assign', methods=['POST'])
def add_planning():
    """
    Ajoute une séance pour un coach automatiquement
    en choisissant le coach le moins chargé ce jour.
    """
    data = request.json

    # Vérifier les données reçues
    date_str = data.get("date")
    session = data.get("session")
    if not date_str or not session:
        return jsonify({"success": False, "error": "date et session requis"}), 400

    try:
        # Appel de la fonction assign_coach
        planning = assign_coach(date_str, session)
        if planning:
            return jsonify({
                "success": True,
                "planning": {
                    "id": planning.id,
                    "date": planning.date.isoformat(),
                    "session": planning.session,
                    "coach_id": planning.coach_id
                }
            }), 201
        else:
            return jsonify({"success": False, "error": "Aucun coach disponible"}), 400

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
