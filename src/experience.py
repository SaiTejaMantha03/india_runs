import math


def experience_fit_score(years_of_experience: float) -> float:
    ideal_center = 7.0
    
    if 5.0 <= years_of_experience <= 9.0:
        return 1.0
    distance = min(abs(years_of_experience - 5.0), abs(years_of_experience - 9.0))
    
    score = 1.0 - 0.08 * distance
    return max(0.2, score)


def applied_ml_tenure_fraction(career_history: list, current_industry_titles_hint: set = None) -> float:
    
    ml_title_keywords = [
        "ml", "machine learning", "ai", "nlp", "data scientist",
        "data engineer", "applied scientist", "recommendation",
        "search engineer", "computer vision",
    ]
    total = sum(ch.get("duration_months", 0) for ch in career_history)
    if total == 0:
        return 0.0
    ml_months = sum(
        ch.get("duration_months", 0)
        for ch in career_history
        if any(kw in ch.get("title", "").lower() for kw in ml_title_keywords)
    )
    return ml_months / total
