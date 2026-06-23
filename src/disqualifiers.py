from datetime import date

CONSULTING_FIRMS = {
    "TCS", "Infosys", "Wipro", "Accenture", "Cognizant", "Capgemini",
    "Tech Mahindra", "Mindtree", "HCL", "L&T Infotech", "Mphasis",
}

CV_SPEECH_ROBOTICS_TITLES = {"Computer Vision Engineer"}

PRODUCT_COMPANY_SIGNAL_TITLES_EXCLUDE_AS_PRODUCT = CONSULTING_FIRMS


def title_chaser_penalty(career_history: list) -> float:
    if len(career_history) < 3:
        return 1.0

    short_stints = sum(1 for ch in career_history if ch.get("duration_months", 999) < 18)

    ratio = short_stints / len(career_history)
    if len(career_history) >= 4 and ratio >= 0.75:
        return 0.65
    if len(career_history) >= 3 and ratio >= 0.6:
        return 0.8
    return 1.0


def consulting_only_penalty(career_history: list, years_of_experience: float) -> float:
    if not career_history:
        return 1.0

    companies = [ch.get("company", "") for ch in career_history]
    all_consulting = all(c in CONSULTING_FIRMS for c in companies)

    if all_consulting and years_of_experience >= 2:
        return 0.45  
                      
    return 1.0


def cv_speech_only_penalty(current_title: str, skills: list, career_history: list) -> float:
    if current_title not in CV_SPEECH_ROBOTICS_TITLES:
        return 1.0

    skill_names = {s["name"] for s in skills}
    nlp_ir_skills = {
        "NLP", "Information Retrieval", "BM25", "Elasticsearch",
        "OpenSearch", "Semantic Search", "Recommendation Systems",
        "Learning to Rank", "Search Backend",
    }
    has_nlp_ir_skill = bool(skill_names & nlp_ir_skills)

    text_blob = " ".join(ch.get("description", "") for ch in career_history).lower()
    nlp_ir_keywords = ["search", "retrieval", "ranking", "nlp", "recommendation", "relevance"]
    has_nlp_ir_text = any(kw in text_blob for kw in nlp_ir_keywords)

    if not has_nlp_ir_skill and not has_nlp_ir_text:
        return 0.4
    return 0.85  


def architecture_only_penalty(career_history: list) -> float:
    if not career_history:
        return 1.0

    current = next((ch for ch in career_history if ch.get("is_current")), career_history[0])
    title = current.get("title", "").lower()
    desc = current.get("description", "").lower()
    duration = current.get("duration_months", 0)

    pure_architecture_titles = ["architect", "engineering manager", "head of", "vp ", "director"]
    is_architecture_title = any(t in title for t in pure_architecture_titles)

    coding_signals = ["implement", "wrote", "built", "shipped", "coded", "developed", "designed and built"]
    has_coding_language = any(sig in desc for sig in coding_signals)

    if is_architecture_title and duration >= 18 and not has_coding_language:
        return 0.5
    return 1.0


def recent_langchain_only_penalty(skills: list, career_history: list, years_of_experience: float) -> float:
    skill_names = {s["name"]: s for s in skills}
    if "LangChain" not in skill_names:
        return 1.0

    langchain_dur = skill_names["LangChain"].get("duration_months", 0)
    if langchain_dur > 18:
        return 1.0  

    
    other_substantial_ml = any(
        s["name"] in {"Python", "Machine Learning", "Deep Learning", "NLP",
                       "scikit-learn", "TensorFlow", "PyTorch", "Statistical Modeling"}
        and s.get("duration_months", 0) > 24
        for s in skills
    )
    if other_substantial_ml or years_of_experience >= 5:
        return 0.9  
    return 0.5


def compute_disqualifier_multiplier(candidate: dict) -> tuple[float, list[str]]:
    profile = candidate["profile"]
    career_history = candidate["career_history"]
    skills = candidate["skills"]
    yoe = profile["years_of_experience"]
    current_title = profile["current_title"]

    flags = []
    multiplier = 1.0

    m = title_chaser_penalty(career_history)
    if m < 1.0:
        flags.append("frequent_short_stints")
        multiplier *= m

    m = consulting_only_penalty(career_history, yoe)
    if m < 1.0:
        flags.append("consulting_only_career")
        multiplier *= m

    m = cv_speech_only_penalty(current_title, skills, career_history)
    if m < 1.0:
        flags.append("cv_speech_without_nlp_ir")
        multiplier *= m

    m = architecture_only_penalty(career_history)
    if m < 1.0:
        flags.append("architecture_role_no_recent_code")
        multiplier *= m

    m = recent_langchain_only_penalty(skills, career_history, yoe)
    if m < 1.0:
        flags.append("recent_langchain_only")
        multiplier *= m

    return multiplier, flags
