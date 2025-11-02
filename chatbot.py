from flask import Flask, request, jsonify
from flask_cors import CORS
import ollama
import json
import re
import mysql.connector
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)


# ⚙️ Configuration MySQL avec gestion d'erreur
def get_db_connection():
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",  # ton mot de passe MySQL ici
            database="smartfitdb"
        )
        return db
    except mysql.connector.Error as err:
        print(f"Erreur de connexion à la base de données: {err}")
        return None


def detect_intention(message):
    """Détecte l'intention de l'utilisateur"""
    message_lower = message.lower()

    intentions = {
        "recherche_coach": any(keyword in message_lower for keyword in [
            "coach", "disponible", "dispo", "disponibilité", "qui est disponible",
            "quels coachs", "liste des coachs", "coachs pour", "cherche coach"
        ]),
        "reservation": any(keyword in message_lower for keyword in [
            "réserver", "reserver", "booking", "book", "prendre rendez-vous",
            "planifier", "séance", "seance", "créneau"
        ]),
        "annulation": any(keyword in message_lower for keyword in [
            "annuler", "supprimer", "cancel", "retirer"
        ])
    }

    # Détection du type d'activité
    activites = {
        "musculation": "musculation" in message_lower,
        "yoga": "yoga" in message_lower,
        "cardio": "cardio" in message_lower,
        "crossfit": "crossfit" in message_lower,
        "pilates": "pilates" in message_lower,
        "Fitness": "Fitness" in message_lower

    }

    activite_demandee = None
    for activite, present in activites.items():
        if present:
            activite_demandee = activite
            break

    return intentions, activite_demandee


def get_available_coachs(activite=None, jour=None):
    """Récupère les coachs disponibles selon l'activité et le jour"""
    db = get_db_connection()
    if not db:
        return {"error": "Erreur de connexion à la base de données"}

    try:
        cursor = db.cursor(dictionary=True)

        query = """
            SELECT DISTINCT c.id, c.nom, c.specialite, c.telephone
            FROM coachs c
            WHERE 1=1
        """
        params = []

        if activite:
            query += " AND (c.specialite LIKE %s)"
            params.append(f"%{activite}%")

        if jour:
            jours = {
                "lundi": 0, "mardi": 1, "mercredi": 2, "jeudi": 3,
                "vendredi": 4, "samedi": 5, "dimanche": 6
            }
            if jour.lower() in jours:
                query += """
                    AND c.id NOT IN (
                        SELECT DISTINCT p.coach_id 
                        FROM plannings p 
                        WHERE DAYOFWEEK(p.date_debut) = %s
                        AND p.date_debut > NOW()
                    )
                """
                params.append(jours[jour.lower()] + 1)

        cursor.execute(query, params)
        coachs = cursor.fetchall()

        result = [
            {
                "id": c["id"],
                "nom": c["nom"],
                "specialite": c["specialite"],
                "telephone": c["telephone"]
            }
            for c in coachs
        ]

        return result

    except mysql.connector.Error as err:
        return {"error": f"Erreur base de données: {err}"}
    finally:
        cursor.close()
        db.close()


@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    client_name = data.get('client_name', None)

    if not user_message:
        return jsonify({"error": "Aucun message fourni"}), 400
    if not client_name:
        return jsonify({"error": "Nom du client non fourni"}), 400

    # 🔍 Détection de l'intention
    intentions, activite_demandee = detect_intention(user_message)

    # Si l'utilisateur cherche des coachs disponibles
    if intentions["recherche_coach"]:
        # Extraction du jour depuis le message si mentionné
        jours_pattern = r"\b(lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche)\b"
        jour_match = re.search(jours_pattern, user_message.lower())
        jour_demande = jour_match.group(1) if jour_match else None

        # Recherche des coachs disponibles
        coachs_disponibles = get_available_coachs(activite_demandee, jour_demande)

        if "error" in coachs_disponibles:
            return jsonify({
                "reply": {
                    "type": "recherche_coach",
                    "message": f"Erreur lors de la recherche des coachs: {coachs_disponibles['error']}",
                    "coachs": []
                },
                "saved": False
            })

        # Construction du message de réponse
        if coachs_disponibles:
            message_reponse = f"Voici les coachs disponibles"
            if activite_demandee:
                message_reponse += f" en {activite_demandee}"
            if jour_demande:
                message_reponse += f" pour {jour_demande}"
            message_reponse += f" : {len(coachs_disponibles)} coach(s) trouvé(s)"
        else:
            message_reponse = f"Aucun coach disponible trouvé"
            if activite_demandee:
                message_reponse += f" en {activite_demandee}"
            if jour_demande:
                message_reponse += f" pour {jour_demande}"

        return jsonify({
            "reply": {
                "type": "recherche_coach",
                "message": message_reponse,
                "coachs": coachs_disponibles,
                "activite": activite_demandee,
                "jour": jour_demande
            },
            "saved": False
        })

    # 🔹 Prompt pour l'IA pour les réservations
    prompt = f"""
    Tu es un assistant de réservation sportif pour l'application SmartFit.
    Analyse la phrase suivante et retourne UNIQUEMENT un JSON au format :
    {{
        "coach": "nom du coach si mentionné sinon null",
        "jour": "jour mentionné sinon null",
        "heure_debut": "heure de début (ex: 09:00) sinon null",
        "heure_fin": "heure de fin (ex: 10:00) sinon null",
        "titre": "titre de la séance, exemple: Musculation",
        "description": "description courte de la séance"
    }}

    Phrase : "{user_message}"
    """

    try:
        # Appel modèle IA local
        response = ollama.chat(
            model='llama3',
            messages=[{'role': 'user', 'content': prompt}]
        )
        raw_output = response['message']['content']
    except Exception as e:
        return jsonify({"error": f"Erreur avec le modèle IA: {str(e)}"}), 500

    # Extraction JSON propre
    json_match = re.search(r'\{.*\}', raw_output, re.DOTALL)
    parsed_data = {}
    if json_match:
        try:
            parsed_data = json.loads(json_match.group())
        except json.JSONDecodeError:
            parsed_data = {"error": "Erreur d'analyse du JSON"}
    else:
        parsed_data = {"error": "Aucun JSON trouvé dans la réponse"}

    saved_to_db = False
    db_error = None

    if all(k in parsed_data for k in ("coach", "jour", "heure_debut", "heure_fin")):
        db = get_db_connection()
        if db:
            try:
                cursor = db.cursor(dictionary=True)

                # 🔹 Récupérer coach_id depuis le nom du coach
                cursor.execute("SELECT id FROM coachs WHERE nom = %s", (parsed_data["coach"],))
                coach_row = cursor.fetchone()
                if coach_row:
                    coach_id = coach_row["id"]
                else:
                    return jsonify({
                        "error": f"Coach '{parsed_data['coach']}' non trouvé",
                        "saved": False
                    }), 400

                # 🔹 Récupérer client_id depuis le nom du client
                cursor.execute("SELECT id FROM client WHERE nom = %s", (client_name,))
                client_row = cursor.fetchone()
                if client_row:
                    client_id = client_row["id"]
                else:
                    return jsonify({
                        "error": f"Client '{client_name}' non trouvé",
                        "saved": False
                    }), 400

                # 🔹 Conversion jour + heure en datetime
                jours = {
                    "lundi": 0, "mardi": 1, "mercredi": 2, "jeudi": 3,
                    "vendredi": 4, "samedi": 5, "dimanche": 6
                }

                today = datetime.today()
                jour_lower = parsed_data["jour"].lower()
                target_weekday = jours.get(jour_lower, today.weekday())

                days_ahead = target_weekday - today.weekday()
                if days_ahead < 0:
                    days_ahead += 7

                date_of_session = today + timedelta(days=days_ahead)

                date_debut = datetime.combine(
                    date_of_session.date(),
                    datetime.strptime(parsed_data["heure_debut"], "%H:%M").time()
                )
                date_fin = datetime.combine(
                    date_of_session.date(),
                    datetime.strptime(parsed_data["heure_fin"], "%H:%M").time()
                )

                # 🔹 Vérifier si le coach est disponible à ce créneau
                cursor.execute("""
                    SELECT id FROM plannings 
                    WHERE coach_id = %s 
                    AND ((date_debut BETWEEN %s AND %s) OR (date_fin BETWEEN %s AND %s))
                """, (coach_id, date_debut, date_fin, date_debut, date_fin))

                if cursor.fetchone():
                    return jsonify({
                        "error": f"Le coach {parsed_data['coach']} n'est pas disponible à ce créneau",
                        "saved": False
                    }), 400

                # 🔹 Insertion dans la table plannings
                sql = """
                    INSERT INTO plannings (date_debut, date_fin, titre, description, client_id, coach_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                values = (
                    date_debut,
                    date_fin,
                    parsed_data.get("titre", "Séance"),
                    parsed_data.get("description", ""),
                    client_id,
                    coach_id
                )
                cursor.execute(sql, values)
                db.commit()
                saved_to_db = True

            except mysql.connector.Error as err:
                db_error = f"Erreur base de données: {err}"
                saved_to_db = False
            except ValueError as e:
                db_error = f"Erreur de format de date/heure: {e}"
                saved_to_db = False
            finally:
                cursor.close()
                db.close()
        else:
            db_error = "Impossible de se connecter à la base de données"

    return jsonify({
        "reply": parsed_data,
        "saved": saved_to_db,
        "db_error": db_error,
        "raw": raw_output
    })


@app.route('/coachs', methods=['GET'])
def get_coachs():
    """Endpoint pour récupérer tous les coachs avec filtres"""
    activite = request.args.get('activite')
    jour = request.args.get('jour')

    coachs = get_available_coachs(activite, jour)

    if "error" in coachs:
        return jsonify({"error": coachs["error"]}), 500

    return jsonify({
        "coachs": coachs,
        "count": len(coachs),
        "filters": {
            "activite": activite,
            "jour": jour
        }
    })


@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint pour vérifier que l'API fonctionne"""
    db = get_db_connection()
    db_status = "connected" if db else "disconnected"
    if db:
        db.close()
    return jsonify({
        "status": "running",
        "database": db_status,
        "timestamp": datetime.now().isoformat()
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)