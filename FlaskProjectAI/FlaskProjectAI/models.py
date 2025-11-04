from database import db
from datetime import datetime


class Coach(db.Model):
    __tablename__ = "coachs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    specialite = db.Column(db.String(100))
    email = db.Column(db.String(100), nullable=False, unique=True)
    telephone = db.Column(db.String(20))

    # Relations optionnelles
    performances = db.relationship('Performance', backref='coach', lazy=True)
    plannings = db.relationship('Planning', backref='coach', lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "nom": self.nom,
            "prenom": self.prenom,
            "specialite": self.specialite,
            "email": self.email,
            "telephone": self.telephone
        }

class Planning(db.Model):
    __tablename__ = "planning"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 🔹 Ajout autoincrement
    date = db.Column(db.DateTime, nullable=False)
    session = db.Column(db.String(50), nullable=False)
    coach_id = db.Column(db.Integer, db.ForeignKey('coachs.id'), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date.isoformat(),
            "session": self.session,
            "coach_id": self.coach_id
        }

class Performance(db.Model):
    __tablename__ = "performances"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    client_count = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Float)
    coach_id = db.Column(db.Integer, db.ForeignKey('coachs.id'), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date.isoformat(),
            "client_count": self.client_count,
            "rating": self.rating,
            "coach_id": self.coach_id
        }
