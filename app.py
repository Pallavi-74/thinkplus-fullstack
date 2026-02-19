from flask import Flask, request, jsonify
from database_config import get_connection
import random 
from recommendations import get_next_recommendation 
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/dashboard/<int:user_id>', methods=['GET'])
def get_dashboard(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True, buffered=True) 
    try:
        cursor.execute("SELECT IFNULL(AVG(score), 0) as avg, COUNT(*) as count FROM quiz_attempts WHERE user_id = %s", (user_id,))
        stats = cursor.fetchone()
        cursor.execute("SELECT recommended_topic_id FROM recommendations WHERE user_id = %s ORDER BY id DESC LIMIT 1", (user_id,))
        rec_row = cursor.fetchone()
        topic_id = rec_row['recommended_topic_id'] if rec_row else 1
        topic_name = "HTML" if topic_id==2 else "python"

        from recommendations import analyze_student_performance
        ai_analysis = analyze_student_performance(user_id, stats['avg'], stats['count'])

        response_data = {
            "student_id": ai_analysis['student_id'],
            "current_level": ai_analysis['current_level'],
            "difficulty_adjustment": ai_analysis['difficulty_adjustment'],
            "recommended_topic": { "topic_id": topic_id ,"topic_name": topic_name},
            "stats": {
                "avg": float(stats['avg']),
                "count" : int(stats['count'])}
        }
        return jsonify(response_data)
    except Exception as e:
        print(f"DEBUG ERROR: {e}")
        return jsonify({
            "recommendation":{"topic_id":1,"topic_name":"pyhton"},
            "stats":{"avg":0,"count":0},
            "current_level":"Beginner",
            "difficulty_adjustment":"Maintain"
        })
    finally:
        cursor.close()
        conn.close()


@app.route('/api/submit_quiz', methods=['POST'])
def submit_quiz():
    data = request.json
    conn = get_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)
    
    try:
        cursor.execute("INSERT INTO quiz_attempts (user_id, topic_id, score) VALUES (%s, %s, %s)", 
                       (data['user_id'], data['topic_id'], data['score']))
        
        new_rec_id = get_next_recommendation(data['user_id'], data['topic_id'], data['score'])
        cursor.execute("""
            INSERT INTO recommendations (user_id, recommended_topic_id) 
            VALUES (%s, %s) 
            ON DUPLICATE KEY UPDATE recommended_topic_id = VALUES(recommended_topic_id)
        """, (data['user_id'], new_rec_id))

        conn.commit()
        return jsonify({"status": "success", "new_recommendation": new_rec_id}), 201
    finally:
        cursor.close()
        conn.close()
 
@app.route('/api/login', methods=['POST'])
def login():
    conn = None
    try:
        data = request.json
        conn = get_connection()
        cursor = conn.cursor(dictionary=True, buffered=True) 
        
        # Select username as well as id
        query = "SELECT id, username, role FROM users WHERE username = %s AND email = %s"
        cursor.execute(query, (data['username'], data['email']))
        user = cursor.fetchone()
        
        cursor.close()
        if user:
            return jsonify({
                "user_id": user['id'],
                "username": user['username'], # Return the username
                "role": user['role']
            }), 200
        else:
            return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        print(f"SQL Error: {e}") # Check your terminal for this!
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/get_questions/<string:subject_name>', methods=['GET'])
def get_questions(subject_name):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True, buffered=True) # Use buffered to avoid Unread Result error

    tid = 2 if subject_name == "HTML" else 1
    cursor.execute("SELECT * FROM questions WHERE topic_id = %s ORDER BY RAND() LIMIT 3", (tid,))
    questions = cursor.fetchall()

    # Get distractors from the database
    cursor.execute("SELECT DISTINCT correct_answer FROM questions")
    all_ans = [r['correct_answer'] for r in cursor.fetchall()]

    formatted = []
    import random
    for q in questions:
        wrong = random.sample([a for a in all_ans if a != q['correct_answer']], 2)
        opts = [q['correct_answer']] + wrong
        random.shuffle(opts)
        formatted.append({
            "question_text": q['question_text'],
            "options": opts,
            "correct_idx": opts.index(q['correct_answer']),
            "topic_id": tid
        })

    cursor.close()
    conn.close()
    return jsonify(formatted)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
