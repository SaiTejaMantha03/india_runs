from .title_taxonomy import title_prior
from .skill_taxonomy import skill_weight, SKILL_WEIGHTS, PROFICIENCY_MULTIPLIER
from .experience import experience_fit_score
from .coherence import evidence_bonus, skill_evidence_corroboration
from .disqualifiers import compute_disqualifier_multiplier
from .anomaly import compute_anomaly_multiplier
from .behavioral import compute_availability_multiplier

WEIGHT_TITLE = 0.40
WEIGHT_SKILL = 0.30
WEIGHT_EXPERIENCE = 0.15
WEIGHT_EVIDENCE = 0.15

MAX_SKILL_RAW_SCORE = 6.0  


def skill_match_score(skills: list, career_history: list) -> tuple[float, list[str]]:
    raw = 0.0
    matched = []
    for s in skills:
        w = skill_weight(s["name"])
        if w <= 0:
            continue
        prof_mult = PROFICIENCY_MULTIPLIER.get(s["proficiency"], 0.5)
        
        endorsement_boost = min(s.get("endorsements", 0) / 50.0, 0.15)
        contribution = w * prof_mult * (1.0 + endorsement_boost)
        raw += contribution
        if w >= 0.5:
            matched.append(s["name"])

    normalized = min(raw / MAX_SKILL_RAW_SCORE, 1.0)
    corroboration = skill_evidence_corroboration(skills, career_history)
    final = normalized * corroboration
    matched.sort(key=lambda n: -skill_weight(n))
    return final, matched[:5]


def score_candidate(candidate: dict) -> dict:
    
    profile = candidate["profile"]
    career_history = candidate["career_history"]
    skills = candidate["skills"]

    t_score = title_prior(profile["current_title"])
    s_score, matched_skills = skill_match_score(skills, career_history)
    e_score = experience_fit_score(profile["years_of_experience"])
    ev_bonus, ev_matched = evidence_bonus(career_history)

    base_score = (
        WEIGHT_TITLE * t_score
        + WEIGHT_SKILL * s_score
        + WEIGHT_EXPERIENCE * e_score
        + WEIGHT_EVIDENCE * ev_bonus
    )

    disq_mult, disq_flags = compute_disqualifier_multiplier(candidate)
    anom_mult, anom_flags = compute_anomaly_multiplier(candidate)
    avail_mult, avail_flags = compute_availability_multiplier(candidate)

    adjusted = base_score * disq_mult * anom_mult * avail_mult
    final_score = round(adjusted * 100, 4)

    return {
        "candidate_id": candidate["candidate_id"],
        "final_score": final_score,
        "title_score": round(t_score, 4),
        "skill_score": round(s_score, 4),
        "experience_score": round(e_score, 4),
        "evidence_bonus": round(ev_bonus, 4),
        "base_score": round(base_score, 4),
        "disqualifier_multiplier": round(disq_mult, 4),
        "anomaly_multiplier": round(anom_mult, 4),
        "availability_multiplier": round(avail_mult, 4),
        "matched_skills": matched_skills,
        "evidence_matched": ev_matched,
        "disqualifier_flags": disq_flags,
        "anomaly_flags": anom_flags,
        "availability_flags": avail_flags,
    }
