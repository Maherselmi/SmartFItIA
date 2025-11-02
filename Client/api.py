from flask import Flask, request, jsonify
import joblib
import numpy as np
import pandas as pd

# === 1️⃣ Initialisation de Flask ===
app = Flask(__name__)

# === 2️⃣ Chargement du modèle et du scaler ===
model = joblib.load("fitness_model.pkl")
scaler = joblib.load("scaler.pkl")

# === 3️⃣ Définition des features attendues ===
FEATURES = [
    "age", "gender", "height_cm", "weight_kg", "activity_type",
    "duration_minutes", "intensity", "calories_burned", "avg_heart_rate",
    "hours_sleep", "stress_level", "daily_steps", "hydration_level", "bmi",
    "resting_heart_rate", "blood_pressure_systolic", "blood_pressure_diastolic",
    "health_condition", "smoking_status"
]

# === 4️⃣ Route de prédiction ===
@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()

        # Vérifier que toutes les features sont présentes
        if not all(feature in data for feature in FEATURES):
            return jsonify({"error": "Certaines features manquent"}), 400

        # Conversion en DataFrame
        input_data = pd.DataFrame([data])

        # Conversion des valeurs texte en numériques si besoin
        for col in input_data.select_dtypes(include=['object']).columns:
            input_data[col] = input_data[col].astype('category').cat.codes

        # Normalisation
        input_scaled = scaler.transform(input_data)

        # Prédiction
        prediction = model.predict(input_scaled)[0]

        # 🔹 Interprétation simple de la prédiction
        if prediction < 0:
            interpretation = "Résultat faible selon les critères du modèle."
        elif prediction < 0.5:
            interpretation = "Résultat moyen, à surveiller."
        else:
            interpretation = "Résultat élevé, très bon indicateur !"

        return jsonify({
            "prediction": float(prediction),
            "interpretation": interpretation,
            "message": "✅ Prédiction effectuée avec succès"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# === 5️⃣ Lancement du serveur ===
if __name__ == "__main__":
    app.run(port=5001, debug=True)
