# model.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

# === 1️⃣ Chargement du dataset ===
dataset_path = r"C:\Users\Miria\PycharmProjects\PythonProject\Client\health_fitness_dataset.csv"
df = pd.read_csv(dataset_path)

print("✅ Dataset chargé avec succès :", df.shape)

# === 2️⃣ Suppression des colonnes non utiles ===
columns_to_drop = ['participant_id', 'date']
for col in columns_to_drop:
    if col in df.columns:
        df.drop(columns=[col], inplace=True)

# === 3️⃣ Encodage automatique des colonnes non numériques ===
le = LabelEncoder()
for col in df.select_dtypes(include=['object']).columns:
    df[col] = le.fit_transform(df[col].astype(str))

# === 4️⃣ Vérification de la colonne cible ===
if 'fitness_level' not in df.columns:
    raise Exception("❌ La colonne 'fitness_level' n'existe pas dans ton dataset.")

# === 5️⃣ Séparation des features et de la cible ===
X = df.drop(columns=['fitness_level'])
y = df['fitness_level']

# === 6️⃣ Normalisation ===
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# === 7️⃣ Division train/test ===
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# === 8️⃣ Entraînement du modèle ===
model = LinearRegression()
model.fit(X_train, y_train)

# === 9️⃣ Évaluation ===
y_pred = model.predict(X_test)
print("📊 MAE:", mean_absolute_error(y_test, y_pred))
print("📈 R²:", r2_score(y_test, y_pred))

# === 🔟 Sauvegarde du modèle et du scaler ===
joblib.dump(model, "fitness_model.pkl")
joblib.dump(scaler, "scaler.pkl")

print("✅ Modèle entraîné et sauvegardé avec succès.")
