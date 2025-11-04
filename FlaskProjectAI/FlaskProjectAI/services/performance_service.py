from models import Performance

def get_coach_average_rating(coach_id):
    performances = Performance.query.filter_by(coach_id=coach_id).all()
    if not performances:
        return 0
    return sum(p.rating or 0 for p in performances) / len(performances)
