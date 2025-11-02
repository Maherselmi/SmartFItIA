from flask import Flask, request, jsonify
import pandas as pd
import joblib
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# === 1️⃣ Charger le modèle et le scaler ===
model = joblib.load('fitness_model.pkl')
scaler = joblib.load('scaler.pkl')

# === 2️⃣ Définir les features ===
features = [
    "age",
    "gender",
    "height_cm",
    "weight_kg",
    "activity_type",
    "duration_minutes",
    "intensity",
    "calories_burned",
    "avg_heart_rate",
    "hours_sleep",
    "stress_level",
    "daily_steps",
    "hydration_level",
    "bmi",
    "resting_heart_rate",
    "blood_pressure_systolic",
    "blood_pressure_diastolic",
    "health_condition",
    "smoking_status"
]

# === 3️⃣ Fonction pour générer un message personnalisé ===
def generate_message(score):
    if score < 40:
        return (
            "Votre niveau de forme est faible. 💤 "
            "Essayez d'améliorer votre hygiène de vie : augmentez votre activité physique, dormez mieux et réduisez votre stress."
        )
    elif score < 70:
        return (
            "Votre forme est moyenne. ⚖️ "
            "Continuez vos efforts : un peu plus de régularité dans le sport et une meilleure hydratation peuvent faire la différence."
        )
    elif score < 85:
        return (
            "Votre niveau de forme est bon ! 💪 "
            "Pensez à maintenir vos habitudes saines et à équilibrer repos et activité."
        )
    else:
        return (
            "Excellente condition physique ! 🌟 "
            "Continuez ainsi, vous avez un mode de vie très sain et équilibré."
        )


# === 4️⃣ Route pour obtenir les questions ===
@app.route('/questions', methods=['GET'])
def get_questions():
    questions = [
        {"key": "age", "question": "Quel est votre âge ?"},
        {"key": "gender", "question": "Quel est votre genre (0 = homme, 1 = femme) ?"},
        {"key": "height_cm", "question": "Quelle est votre taille (en cm) ?"},
        {"key": "weight_kg", "question": "Quel est votre poids (en kg) ?"},
        {"key": "activity_type", "question": "Quel type d’activité pratiquez-vous ? (0 = aucune, 1 = cardio, 2 = muscu, etc.)"},
        {"key": "duration_minutes", "question": "Durée moyenne de vos séances (en minutes) ?"},
        {"key": "intensity", "question": "Intensité de votre activité (de 1 à 10) ?"},
        {"key": "calories_burned", "question": "Calories brûlées par séance ?"},
        {"key": "avg_heart_rate", "question": "Rythme cardiaque moyen pendant l’effort ?"},
        {"key": "hours_sleep", "question": "Combien d’heures dormez-vous par nuit ?"},
        {"key": "stress_level", "question": "Niveau de stress (1 à 10) ?"},
        {"key": "daily_steps", "question": "Nombre de pas par jour ?"},
        {"key": "hydration_level", "question": "Hydratation moyenne (en litres/jour) ?"},
        {"key": "bmi", "question": "Votre IMC (ou 0 si inconnu) ?"},
        {"key": "resting_heart_rate", "question": "Rythme cardiaque au repos ?"},
        {"key": "blood_pressure_systolic", "question": "Pression artérielle systolique ?"},
        {"key": "blood_pressure_diastolic", "question": "Pression artérielle diastolique ?"},
        {"key": "health_condition", "question": "Avez-vous une condition de santé chronique ? (0 = non, 1 = oui) ?"},
        {"key": "smoking_status", "question": "Fumez-vous ? (0 = non, 1 = occasionnel, 2 = régulier) ?"}
    ]
    return jsonify(questions)


# === 5️⃣ Route de prédiction robuste ===
@app.route('/predict', methods=['POST'])
def predict():
    try:
        input_data = request.get_json()

        # Vérification du format
        if not input_data or not isinstance(input_data, dict):
            return jsonify({'error': 'Aucune donnée reçue ou format invalide.'}), 400

        # Vérifier les champs manquants
        missing = [f for f in features if f not in input_data]
        if missing:
            return jsonify({'error': f'Champs manquants : {missing}'}), 400

        # Nettoyage et conversion des données
        cleaned_data = []
        for f in features:
            value = input_data.get(f, 0)

            # Si valeur vide, on remplace par 0
            if value == '' or value is None:
                value = 0

            # Conversion automatique en float si possible
            try:
                value = float(value)
            except ValueError:
                return jsonify({'error': f"Valeur invalide pour '{f}': {value}"}), 400

            cleaned_data.append(value)

        # Recalcul du BMI si possible
        height = cleaned_data[features.index("height_cm")]
        weight = cleaned_data[features.index("weight_kg")]
        bmi_index = features.index("bmi")

        if height > 0 and weight > 0 and cleaned_data[bmi_index] == 0:
            cleaned_data[bmi_index] = round(weight / ((height / 100) ** 2), 2)

        # Création du DataFrame
        df = pd.DataFrame([cleaned_data], columns=features)

        # Normalisation
        df_scaled = scaler.transform(df)

        # Prédiction brute
        raw_prediction = float(model.predict(df_scaled)[0])

        # Mise à l’échelle [0, 100]
        score = (raw_prediction - (-1)) / (1 - (-1)) * 100
        score = round(max(0, min(score, 100)), 2)

        # Générer message
        message = generate_message(score)

        return jsonify({
            "predicted_fitness_level": score,
            "message": message
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
