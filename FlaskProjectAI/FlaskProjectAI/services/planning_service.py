from models import Planning, Coach, db
from datetime import datetime

def assign_coach(date, session):
    """
    Assigne automatiquement un coach à une séance
    en choisissant celui qui a le moins de sessions planifiées ce jour.
    """
    # Convertir date en datetime si nécessaire
    if isinstance(date, str):
        date = datetime.fromisoformat(date)

    # On prend le coach avec le moins de sessions ce jour-là
    coaches = Coach.query.all()
    best_coach = None
    min_sessions = float('inf')

    for c in coaches:
        # Compter toutes les séances du coach pour CE JOUR (ignore l'heure)
        sessions_count = Planning.query.filter(
            Planning.coach_id == c.id,
            db.func.date(Planning.date) == date.date()  # 🔹 comparaison sur la date seulement
        ).count()

        if sessions_count < min_sessions:
            min_sessions = sessions_count
            best_coach = c

    if best_coach:
        planning = Planning(date=date, session=session, coach_id=best_coach.id)
        db.session.add(planning)
        db.session.commit()
        return planning

    return None
