def get_next_recommendation(user_id, target_topic_id, avg_score):
    if avg_score >= 70:
        new_topic_id = 2 if target_topic_id == 1 else 1
    else:
        new_topic_id = target_topic_id
    return new_topic_id


def analyze_student_performance(user_id, avg_score, total_quizzes):   
    if total_quizzes == 0:
        level = "new student"
        adj = "baseline"
    elif avg_score >= 80:
        level = "Advanced"
        adj = "increase"
    elif avg_score >= 50:
        level = "Beginner"
        adj = "intermediate"
    else:
        level = "beginner"
        adj = "decrease"
    return {
        "student_id": f"U{user_id}",
        "current_level": level,
        "difficulty_adjustment": adj
    }