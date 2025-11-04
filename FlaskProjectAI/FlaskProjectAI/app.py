from flask import Flask
from flask_cors import CORS
from database import db
from config import Config
from routes.coach_routes import coach_bp
from routes.planning_routes import planning_bp
from routes.performance_routes import performance_bp
from routes.ai_routes import ai_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    # Initialiser db
    db.init_app(app)



    app.register_blueprint(coach_bp)
    app.register_blueprint(planning_bp)
    app.register_blueprint(performance_bp)
    app.register_blueprint(ai_bp, url_prefix='/api/ai')

    @app.route('/')
    def home():
        return "API SmartFit (Flask + MySQL) – Coach, Planning & Performance"

    # Créer les tables
    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True , port=5002)
