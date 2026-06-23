

from .skill_taxonomy import is_honeypot_bait_skill


def expert_count_penalty(skills: list) -> float:
   
    expert_count = sum(1 for s in skills if s.get("proficiency") == "expert")
    if expert_count <= 1:
        return 1.0
    elif expert_count == 2:
        return 0.92
    elif expert_count <= 4:
        return 0.65
    elif expert_count <= 6:
        return 0.35
    else:
        return 0.12


def honeypot_bucket_title_penalty(current_title: str, skills: list) -> float:
    
    
    from .title_taxonomy import is_honeypot_bucket_title

    if not is_honeypot_bucket_title(current_title):
        return 1.0

    expert_count = sum(1 for s in skills if s.get("proficiency") == "expert")
    if expert_count >= 2:
        return 0.15  
    return 1.0


def skill_duration_exceeds_career_penalty(career_history: list, skills: list) -> float:

    career_total = sum(ch.get("duration_months", 0) for ch in career_history)
    if not skills:
        return 1.0
    max_skill_dur = max((s.get("duration_months", 0) for s in skills), default=0)
    overshoot = max_skill_dur - career_total

    if overshoot <= 6:
        return 1.0
    elif overshoot <= 20:
        return 0.85
    elif overshoot <= 35:
        return 0.6
    else:
        return 0.35


def overlapping_education_penalty(education: list) -> float:
    intervals = sorted(
        (e["start_year"], e["end_year"])
        for e in education
        if e.get("start_year") is not None and e.get("end_year") is not None
    )
    max_overlap = 0
    for i in range(len(intervals) - 1):
        overlap = intervals[i][1] - intervals[i + 1][0]
        if overlap > max_overlap:
            max_overlap = overlap
    if max_overlap <= 0:
        return 1.0
    elif max_overlap <= 2:
        return 0.97
    elif max_overlap <= 4:
        return 0.88
    else:
        return 0.75


def zero_duration_expert_penalty(skills: list) -> float:
    zero_dur_experts = sum(
        1 for s in skills
        if s.get("proficiency") == "expert" and s.get("duration_months", -1) == 0
    )
    if zero_dur_experts == 0:
        return 1.0
    elif zero_dur_experts == 1:
        return 0.5
    else:
        return 0.2


def honeypot_bait_skill_penalty(skills: list) -> float:

    bait_count = sum(1 for s in skills if is_honeypot_bait_skill(s.get("name", "")))
    if bait_count == 0:
        return 1.0
    return max(0.5, 1.0 - 0.12 * bait_count)


def duplicate_description_penalty(career_history: list) -> float:
    descs = [ch.get("description", "") for ch in career_history]
    if len(descs) < 4:
        return 1.0
    if len(set(descs)) == 1:
        return 0.93
    return 1.0


def compute_anomaly_multiplier(candidate: dict) -> tuple[float, list[str]]:
    career_history = candidate["career_history"]
    skills = candidate["skills"]
    education = candidate["education"]
    current_title = candidate["profile"]["current_title"]

    flags = []
    multiplier = 1.0

    m = expert_count_penalty(skills)
    if m < 1.0:
        flags.append(f"high_expert_skill_count")
        multiplier *= m

    m = honeypot_bucket_title_penalty(current_title, skills)
    if m < 1.0:
        flags.append("honeypot_title_bucket_with_expert_skills")
        multiplier *= m

    m = zero_duration_expert_penalty(skills)
    if m < 1.0:
        flags.append("expert_skill_zero_duration")
        multiplier *= m

    m = skill_duration_exceeds_career_penalty(career_history, skills)
    if m < 1.0:
        flags.append("skill_duration_exceeds_career_total")
        multiplier *= m

    m = overlapping_education_penalty(education)
    if m < 1.0:
        flags.append("overlapping_education")
        multiplier *= m

    m = honeypot_bait_skill_penalty(skills)
    if m < 1.0:
        flags.append("bespoke_bait_skill_vocabulary")
        multiplier *= m

    m = duplicate_description_penalty(career_history)
    if m < 1.0:
        flags.append("duplicate_role_descriptions")
        multiplier *= m

    return multiplier, flags
