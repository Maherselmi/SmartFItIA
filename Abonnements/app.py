from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import joblib
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for Angular

# Load the trained model
MODEL_PATH = "gym_price_predictor.joblib"
try:
    model = joblib.load(MODEL_PATH)
    print(f"✅ Model loaded successfully from {MODEL_PATH}")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    model = None


@app.route('/predict', methods=['POST'])
def predict():
    """
    Predict subscription price based on:
    - Type d'abonnement (subscription type)
    - Date de début (start date)
    - Date de fin (end date)
    """
    if model is None:
        return jsonify({"error": "Model not loaded"}), 500
    
    try:
        # Get JSON data from request
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['type', 'date_debut', 'date_fin']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Extract input data
        subscription_type = data['type']
        date_debut_str = data['date_debut']
        date_fin_str = data['date_fin']
        
        # Parse dates
        try:
            date_debut = pd.to_datetime(date_debut_str)
            date_fin = pd.to_datetime(date_fin_str)
        except Exception as e:
            return jsonify({"error": f"Invalid date format: {str(e)}"}), 400
        
        # Feature engineering (same as in the notebook)
        period_days = (date_fin - date_debut).days
        start_month = date_debut.month
        start_year = date_debut.year
        start_weekday = date_debut.weekday()  # 0=Monday, 6=Sunday
        
        # Validate period_days
        if period_days < 0:
            return jsonify({"error": "End date must be after start date"}), 400
        
        # Create DataFrame with the same structure as training data
        features_df = pd.DataFrame({
            'type': [subscription_type],
            'period_days': [period_days],
            'start_month': [start_month],
            'start_year': [start_year],
            'start_weekday': [start_weekday]
        })
        
        # Make prediction
        predicted_price = model.predict(features_df)[0]
        
        # Return prediction
        return jsonify({
            "predicted_price": round(float(predicted_price), 2),
            "currency": "EUR",
            "features": {
                "type": subscription_type,
                "period_days": int(period_days),
                "start_month": int(start_month),
                "start_year": int(start_year),
                "start_weekday": int(start_weekday)
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5552)

