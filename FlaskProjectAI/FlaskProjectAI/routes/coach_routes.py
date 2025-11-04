from flask import Blueprint, jsonify, request
from database import db
from models import Coach

coach_bp = Blueprint('coach', __name__, url_prefix='/api/coachs')

@coach_bp.route('/', methods=['GET'])
def get_all_coachs():
    return jsonify([c.to_dict() for c in Coach.query.all()])

@coach_bp.route('/', methods=['POST'])
def create_coach():
    data = request.json
    new_coach = Coach(**data)
    db.session.add(new_coach)
    db.session.commit()
    return jsonify(new_coach.to_dict()), 201
