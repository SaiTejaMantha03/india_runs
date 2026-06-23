
def _matched_skills_phrase(matched_skills: list) -> str:
    if not matched_skills:
        return ""
    if len(matched_skills) == 1:
        return matched_skills[0]
    if len(matched_skills) == 2:
        return f"{matched_skills[0]} and {matched_skills[1]}"
    return ", ".join(matched_skills[:-1]) + f", and {matched_skills[-1]}"


def _evidence_phrase(evidence_matched: list) -> str:
    phrases = {
        "ranking_system": "hands-on ranking-model work",
        "recommendation_system": "experience building recommendation systems",
        "search_retrieval": "search/retrieval system experience",
        "embeddings_vector": "embeddings and vector-search work",
        "ml_production": "production ML deployment experience",
        "evaluation": "ranking-evaluation experience",
    }
    matched = [phrases[m] for m in evidence_matched if m in phrases]
    if not matched:
        return ""
    if len(matched) == 1:
        return matched[0]
    return ", ".join(matched[:-1]) + f", and {matched[-1]}"


def _concern_phrases(score_result: dict, candidate: dict) -> list:
    """Build honest, specific concern statements from triggered flags."""
    concerns = []
    sig = candidate["redrob_signals"]
    profile = candidate["profile"]

    flag_set = set(score_result["anomaly_flags"])
    if "high_expert_skill_count" in flag_set:
        n_experts = sum(1 for s in candidate["skills"] if s["proficiency"] == "expert")
        concerns.append(
            f"claims 'expert' proficiency in {n_experts} skills simultaneously, "
            f"statistically unusual and worth verifying in interview"
        )
    if "skill_duration_exceeds_career_total" in flag_set:
        concerns.append(
            "at least one listed skill duration exceeds their total career history length"
        )
    if "expert_skill_zero_duration" in flag_set:
        concerns.append("lists 'expert' proficiency in a skill with 0 months of use")

    disq_set = set(score_result["disqualifier_flags"])
    if "consulting_only_career" in disq_set:
        concerns.append("entire career has been at consulting firms")
    if "cv_speech_without_nlp_ir" in disq_set:
        concerns.append("background is CV-focused with no clear NLP/IR exposure")
    if "frequent_short_stints" in disq_set:
        concerns.append("career shows a pattern of short tenures across roles")
    if "architecture_role_no_recent_code" in disq_set:
        concerns.append("current role reads as architecture-focused with limited recent hands-on coding signal")
    if "recent_langchain_only" in disq_set:
        concerns.append("LangChain experience is recent and not clearly backed by earlier ML production work")

    avail_set = set(score_result["availability_flags"])
    if "inactive_recently" in avail_set:
        concerns.append(f"last active {sig['last_active_date']}")
    if "low_recruiter_response_rate" in avail_set:
        concerns.append(f"recruiter response rate only {sig['recruiter_response_rate']:.0%}")
    if "long_notice_period" in avail_set:
        concerns.append(f"notice period is {sig['notice_period_days']} days")
    if "location_logistics_concern" in avail_set:
        if profile["country"].strip().lower() != "india":
            concerns.append(f"based in {profile['location']}, outside India; Redrob does not sponsor visas")
        else:
            concerns.append(f"based in {profile['location']}, outside the preferred Pune/Noida/Tier-1 cities, no stated relocation interest")

    return concerns


def _rank_framing(rank: int) -> str:
    if rank <= 10:
        return "Strong fit"
    elif rank <= 30:
        return "Solid fit"
    elif rank <= 60:
        return "Reasonable fit"
    else:
        return "Lower-confidence fill"


def generate_reasoning(candidate: dict, score_result: dict, rank: int) -> str:
    profile = candidate["profile"]
    title = profile["current_title"]
    company = profile["current_company"]
    yoe = profile["years_of_experience"]
    location = profile["location"]

    matched_skills = score_result["matched_skills"]
    evidence_matched = score_result["evidence_matched"]
    concerns = _concern_phrases(score_result, candidate)
    skill_phrase = _matched_skills_phrase(matched_skills)
    evidence_phrase = _evidence_phrase(evidence_matched)
    framing = _rank_framing(rank)



    if evidence_phrase and skill_phrase:
        body = (
            f"{framing} -- {title} at {company} ({yoe:.1f}y experience, {location}) "
            f"shows {evidence_phrase} in their career history, backed by listed skills "
            f"including {skill_phrase}."
        )
    elif evidence_phrase:
        body = (
            f"{framing} -- {title} at {company} ({yoe:.1f}y experience, {location}) "
            f"has {evidence_phrase}, which maps directly onto what this JD's first-90-days "
            f"mandate (ranking, retrieval, evaluation) actually needs."
        )
    elif skill_phrase:
        vector_db_skills = {"Qdrant", "Weaviate", "Milvus", "pgvector", "FAISS", "Pinecone"}
        search_skills = {"BM25", "Elasticsearch", "OpenSearch", "Vector Search", "Semantic Search",
                          "Information Retrieval", "Haystack", "LlamaIndex", "Sentence Transformers",
                          "Learning to Rank", "Recommendation Systems", "Embeddings"}
        has_vector_db = set(matched_skills) & vector_db_skills
        has_search = set(matched_skills) & search_skills
        if has_vector_db and has_search:
            closer = "spanning both vector-database and search/ranking work the JD calls out as core requirements"
        elif has_vector_db:
            closer = "covering the vector-database experience the JD calls out as a core requirement"
        elif has_search:
            closer = "covering search and ranking experience the JD calls out as a core requirement"
        else:
            closer = "relevant ML/AI background, though not specifically vector-database or search/ranking skills"
        body = (
            f"{framing} -- {title} at {company}, {yoe:.1f} years of experience, based in {location}. "
            f"Skills list includes {skill_phrase}, {closer}."
        )
    else:
        body = (
            f"{framing} -- {title} at {company}, {yoe:.1f} years of experience, based in {location}. "
            f"Limited direct overlap with the JD's core retrieval/ranking skill list, included on the "
            f"strength of overall profile and experience fit."
        )

    if concerns:
        if rank <= 20:
            tail = f" Worth checking in interview: {concerns[0]}."
        elif len(concerns) == 1:
            tail = f" Concern: {concerns[0]}."
        else:
            tail = f" Concerns: {'; '.join(concerns[:2])}."
    else:
        tail = ""

    return body + tail
