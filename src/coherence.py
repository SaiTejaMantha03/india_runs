import re


EVIDENCE_PATTERNS = {
    "ranking_system": re.compile(
        r"\b(ranking (model|algorithm|layer|system)|learning-to-rank|rerank(ing|ed)?"
        r"|relevance (ranking|scoring) model|search relevance)\b", re.I
    ),
    "recommendation_system": re.compile(
        r"\b(recommendation (system|engine|model)|recommender (system|model)"
        r"|personalization engine|discovery feed (ranking|model))\b", re.I
    ),
    "search_retrieval": re.compile(
        r"\b(search (engine|infrastructure|backend|index|relevance)"
        r"|information retrieval system|retrieval pipeline|retrieval-augmented"
        r"|query understanding|indexing pipeline)\b", re.I
    ),
    "embeddings_vector": re.compile(
        r"\b(embedding (model|pipeline|drift|index)|vector (search|database|index)"
        r"|semantic search|dense retrieval|hybrid (search|retrieval))\b", re.I
    ),
    "ml_production": re.compile(
        r"\b(shipped (a |the )?(model|ranking|system|pipeline)"
        r"|deployed (to|in) production|production (ml|model|inference) (pipeline|system)"
        r"|trained and shipped)\b", re.I
    ),
    "evaluation": re.compile(
        r"\b(NDCG|MRR|MAP@|precision@|recall@|offline-to-online correlation"
        r"|A/B test(ed|ing)? (the|a|this) (ranking|model|system))\b", re.I
    ),
}

EVIDENCE_WEIGHTS = {
    "ranking_system": 0.35,
    "recommendation_system": 0.35,
    "search_retrieval": 0.30,
    "embeddings_vector": 0.20,
    "ml_production": 0.10,
    "evaluation": 0.20,
}


def career_history_text(career_history: list) -> str:
    return " ".join(ch.get("description", "") for ch in career_history)


def evidence_bonus(career_history: list) -> tuple[float, list[str]]:
    text = career_history_text(career_history)
    matched = []
    bonus = 0.0
    for category, pattern in EVIDENCE_PATTERNS.items():
        if pattern.search(text):
            matched.append(category)
            bonus += EVIDENCE_WEIGHTS[category]
    return min(bonus, 0.8), matched


def skill_evidence_corroboration(skills: list, career_history: list) -> float:
    from .skill_taxonomy import BUZZWORD_SKILLS, HONEYPOT_BAIT_SKILLS

    skill_names = {s["name"] for s in skills}
    buzzword_skills_present = skill_names & set(BUZZWORD_SKILLS.keys())
    bait_skills_present = skill_names & HONEYPOT_BAIT_SKILLS

    if not buzzword_skills_present and not bait_skills_present:
        return 1.0  # nothing to corroborate, no discount

    text = career_history_text(career_history)
    has_any_evidence = any(p.search(text) for p in EVIDENCE_PATTERNS.values())

    n_buzzwords = len(buzzword_skills_present) + len(bait_skills_present)

    if has_any_evidence:
        return 1.0
    
    if n_buzzwords >= 5:
        return 0.5
    elif n_buzzwords >= 2:
        return 0.75
    return 0.9
