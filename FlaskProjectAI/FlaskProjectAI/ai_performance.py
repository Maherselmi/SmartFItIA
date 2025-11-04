import pandas as pd
from sklearn.linear_model import LinearRegression
from models import Performance

def train_performance_model():
    # Récupérer les performances depuis la DB
    performances = Performance.query.all()
    data = pd.DataFrame([p.to_dict() for p in performances])

    if data.empty:
        return None

    # Convertir rating en float et supprimer les lignes invalides
    data['rating'] = pd.to_numeric(data['rating'], errors='coerce')
    data = data.dropna(subset=['rating', 'client_count'])

    X = data[['client_count']].astype(float)
    y = data['rating'].astype(float)

    if X.empty or y.empty:
        return None

    model = LinearRegression()
    model.fit(X, y)
    return model

def predict_rating(client_count, model):
    if not model:
        return None
    # Créer un DataFrame avec le même nom de colonne que pour l'entraînement
    X_new = pd.DataFrame({'client_count': [float(client_count)]})
    rating_pred = model.predict(X_new)[0]
    return float(rating_pred)
