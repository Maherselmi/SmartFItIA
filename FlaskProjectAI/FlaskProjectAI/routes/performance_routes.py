from flask import Blueprint, jsonify, request
from database import db
from models import Performance , Coach
from services.performance_service import get_coach_average_rating

performance_bp = Blueprint('performance', __name__, url_prefix='/api/performances')


@performance_bp.route('/', methods=['GET'])
def get_all_performances():
    coachs = Coach.query.all()



    performances = Performance.query.all()

    result = []
    for coach in coachs:
        coach_perfs = [
            {
                "date": p.date.isoformat(),
                "client_count": p.client_count,
                "rating": p.rating
            }
            for p in performances if p.coach_id == coach.id
        ]
        result.append({
            "coach_id": coach.id,
            "name": f"{coach.nom} {coach.prenom}",
            "performances": coach_perfs
        })

    return jsonify(result)


@performance_bp.route('/', methods=['POST'])
def add_performance():
    data = request.json
    perf = Performance(**data)
    db.session.add(perf)
    db.session.commit()
    return jsonify(perf.to_dict()), 201

@performance_bp.route('/average/<int:coach_id>', methods=['GET'])
def average_rating(coach_id):
    avg = get_coach_average_rating(coach_id)
    return jsonify({"coach_id": coach_id, "average_rating": avg})
