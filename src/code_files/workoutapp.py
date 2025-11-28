from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pandas as pd
import joblib
import mysql.connector
from datetime import datetime, date
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

model = joblib.load('readiness_model_multi.pkl')

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='Abhi@775',
        database='USER_WORKOUTS',
        port=3306
    )

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/baseline')
def serve_baseline():
    return send_from_directory('.', 'baseline.html')

@app.route('/daily')
def serve_daily():
    return send_from_directory('.', 'daily.html')

@app.route('/dashboard')
def serve_dashboard():
    return send_from_directory('.', 'dashboard.html')

@app.route('/workout')
def serve_workout():
    return send_from_directory('.', 'workout.html')

@app.route('/history')
def serve_history():
    return send_from_directory('.', 'history.html')

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT username, password_hash FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if not user:
            hashed = generate_password_hash(password)
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                (username, hashed)
            )
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'has_baseline': False})  

        if not check_password_hash(user['password_hash'], password):
            cursor.close()
            conn.close()
            return jsonify({'error': 'Wrong password'}), 401

        cursor.execute("SELECT COUNT(*) AS count FROM Workouts WHERE username = %s", (username,))
        has_baseline = cursor.fetchone()['count'] > 0

        cursor.close()
        conn.close()

        return jsonify({'has_baseline': has_baseline})

    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/save_baseline', methods=['POST'])
def save_baseline():
    try:
        data = request.get_json()
        username = data['username']
        baseline = data['baseline']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("INSERT IGNORE INTO users (username) VALUES (%s)", (username,))

        for exercise_name, values in baseline.items():
            weight = float(str(values['weight']))
            reps = int(str(values['reps']))

            cursor.execute("""
                INSERT INTO Workouts (username, exercise_name, base_weight, base_reps)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    base_weight = VALUES(base_weight),
                    base_reps = VALUES(base_reps)
            """, (username, exercise_name, weight, reps))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'message': 'Baseline saved successfully!'})
    except Exception as e:
        print(f"Error in save_baseline: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/get_workout', methods=['POST'])
def get_workout():
    try:
        data = request.get_json()
        username = data['username']
        sleep_quality = data['sleep_quality']
        readiness = data['readiness']
        stress = data['stress']
        soreness = data['soreness']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        log_date = str(date.today())
        cursor.execute("""
            INSERT INTO DailyWellness (username, log_date, sleep_quality, readiness, stress, soreness)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                sleep_quality=VALUES(sleep_quality),
                readiness=VALUES(readiness),
                stress=VALUES(stress),
                soreness=VALUES(soreness)
        """, (username, log_date, sleep_quality, readiness, stress, soreness))

        cursor.execute("""
            SELECT exercise_name, 
                   CAST(base_weight AS DECIMAL(10,2)) as base_weight, 
                   CAST(base_reps AS SIGNED) as base_reps
            FROM Workouts
            WHERE username = %s
        """, (username,))
        baseline_data = cursor.fetchall()

        if not baseline_data:
            cursor.close()
            conn.close()
            return jsonify({'error': 'No baseline data found. Please set your baseline first.'}), 400

        cursor.execute("INSERT INTO WorkoutSessions (username) VALUES (%s)", (username,))
        session_id = cursor.lastrowid
        conn.commit()
        
        cursor.close()
        conn.close()

        features = pd.DataFrame([{
            'sleep_quality': sleep_quality,
            'readiness': readiness,
            'stress': stress,
            'soreness': soreness
        }])
        readiness_score = float(model.predict(features)[0])

        workout_plan = []
        for exercise in baseline_data:
            base_weight = float(str(exercise['base_weight']))
            base_reps = int(str(exercise['base_reps']))
            
            if readiness_score >= 8:
                weight_multiplier = 1.0
                target_reps = base_reps
            elif readiness_score >= 6:
                weight_multiplier = 0.9
                target_reps = base_reps
            else:
                weight_multiplier = 0.8
                target_reps = max(base_reps - 2, 5)

            recommended_weight = round(base_weight * weight_multiplier, 1)

            workout_plan.append({
                'exercise_name': str(exercise['exercise_name']),
                'recommended_weight': float(recommended_weight),
                'recommended_reps': int(target_reps),
                'message': f"Readiness score: {readiness_score:.1f}/10"
            })

        return jsonify({
            'session_id': int(session_id),
            'readiness_score': float(readiness_score),
            'workout_plan': workout_plan
        })
    except Exception as e:
        print(f"Error in get_workout: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/get_next_set', methods=['POST'])
def get_next_set():
    try:
        data = request.get_json()
        username = data['username']
        session_id = data['session_id']
        exercise_name = data['exercise_name']
        set_number = data['set_number']
        reps_done = data['reps_done']
        rpe_logged = data['rpe_logged']
        weight_lifted = data['weight_lifted']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO PerformedSets (session_id, username, exercise_name, set_number, performed_reps, performed_weight, performed_rpe)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (session_id, username, exercise_name, set_number, reps_done, weight_lifted, rpe_logged))

        conn.commit()
        cursor.close()
        conn.close()

        current_weight = float(weight_lifted)
        rpe = int(rpe_logged)
        
        if rpe <= 3:
            next_weight = round(current_weight + 5.0, 1)
            message = "Way too easy! Adding +5 kg next set"
        elif 4 <= rpe <= 5:
            next_weight = round(current_weight + 2.5, 1)
            message = "Felt light – bumping +2.5 kg"
        elif 6 <= rpe <= 7:
            next_weight = current_weight
            message = "Perfect intensity – same weight"
        elif rpe == 8 or rpe == 9:
            next_weight = round(current_weight - 2.5, 1)
            message = "Tough set – dropping 2.5 kg to keep quality high"
        elif rpe == 10:
            next_weight = round(current_weight - 5.0, 1)
            message = "Grinder! Dropping 5 kg for better reps & form"
        else:
            next_weight = current_weight
            message = "Solid work – staying the same"

        return jsonify({
            'next_weight': next_weight,
            'message': message
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/user_stats/<username>', methods=['GET'])
def get_user_stats(username):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT 
                exercise_name,
                COUNT(*) as total_sets,
                AVG(performed_rpe) as average_rpe
            FROM PerformedSets
            WHERE username = %s AND performed_rpe IS NOT NULL
            GROUP BY exercise_name
            ORDER BY exercise_name
        """, (username,))

        stats = cursor.fetchall()
        cursor.close()
        conn.close()

        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/session_history/<username>', methods=['GET'])
def get_session_history(username):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT 
                ws.session_id,
                ws.session_date,
                COUNT(ps.set_id) as sets_performed
            FROM WorkoutSessions ws
            LEFT JOIN PerformedSets ps ON ws.session_id = ps.session_id
            WHERE ws.username = %s
            GROUP BY ws.session_id, ws.session_date
            ORDER BY ws.session_date DESC
        """, (username,))

        history = cursor.fetchall()
        cursor.close()
        conn.close()

        return jsonify(history)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict', methods=['POST'])
def predict_readiness():
    try:
        data = request.get_json()
        features = pd.DataFrame([data])
        prediction = model.predict(features)
        return jsonify({'readiness_score': float(prediction[0])})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/create_user', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        username = data['username']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()

        if not result:
            cursor.execute("INSERT INTO users (username) VALUES (%s)", (username,))
            conn.commit()

        cursor.close()
        conn.close()
        return jsonify({'message': 'User verified or created successfully!'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/log_workout', methods=['POST'])
def log_workout():
    try:
        data = request.get_json()
        username = data['username']
        sets = data['sets']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("INSERT IGNORE INTO users (username) VALUES (%s)", (username,))
        cursor.execute("INSERT INTO WorkoutSessions (username) VALUES (%s)", (username,))
        session_id = cursor.lastrowid

        for s in sets:
            cursor.execute("""
                INSERT INTO PerformedSets (session_id, username, exercise_name, set_number, performed_reps, performed_weight, performed_rpe)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                session_id,
                username,
                s['exercise_name'],
                s['set_number'],
                s.get('performed_reps'),
                s.get('performed_weight'),
                s.get('performed_rpe')
            ))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'message': 'Workout logged successfully!', 'session_id': session_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/workouts', methods=['GET'])
def get_workouts():
    try:
        username = request.args.get('username')

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT ws.session_id, ws.session_date, ps.exercise_name, ps.set_number,
                   ps.performed_reps, ps.performed_weight, ps.performed_rpe
            FROM WorkoutSessions ws
            JOIN PerformedSets ps ON ws.session_id = ps.session_id
            WHERE ws.username = %s
            ORDER BY ws.session_date DESC, ps.set_number ASC
        """, (username,))

        records = cursor.fetchall()
        cursor.close()
        conn.close()

        return jsonify(records)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/wellness', methods=['POST'])
def log_wellness():
    try:
        data = request.get_json()
        username = data['username']
        log_date = data.get('log_date', str(date.today()))
        sleep_quality = data.get('sleep_quality')
        readiness = data.get('readiness')
        stress = data.get('stress')
        soreness = data.get('soreness')

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO DailyWellness (username, log_date, sleep_quality, readiness, stress, soreness)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                sleep_quality=VALUES(sleep_quality),
                readiness=VALUES(readiness),
                stress=VALUES(stress),
                soreness=VALUES(soreness)
        """, (username, log_date, sleep_quality, readiness, stress, soreness))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'message': 'Wellness log saved successfully!'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True)
