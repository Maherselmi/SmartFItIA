# ai_planning.py
from datetime import datetime, timedelta

def generate_smart_planning(coachs):
    """
    Génère un planning fictif pour chaque coach.
    Chaque coach reçoit 1 ou 2 sessions par jour.
    """
    planning_result = []

    for coach in coachs:
        # Créer des sessions fictives pour les 3 prochains jours
        sessions = []
        today = datetime.now()
        for i in range(3):  # 3 jours
            day = today + timedelta(days=i)
            # Simuler 1 ou 2 sessions par jour
            sessions.append({"date": day.replace(hour=10, minute=0, second=0).isoformat(),
                             "session": "Matin"})
            if i % 2 == 0:  # certains jours 2 sessions
                sessions.append({"date": day.replace(hour=14, minute=0, second=0).isoformat(),
                                 "session": "Après-midi"})

        planning_result.append({
            "coach_id": coach["id"],
            "name": f"{coach.get('nom', 'John')} {coach.get('prenom', 'Doe')}",
            "planning": sessions
        })

    return planning_result
