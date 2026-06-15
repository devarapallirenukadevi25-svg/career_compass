from services.domain_catalog import DOMAINS

PREDICTION_WEIGHTS = {
    "academics": 15,
    "coding_profiles": 20,
    "technical_stack": 25,
    "projects": 15,
    "experience": 15,
    "soft_skills": 10,
}


def _clean_list(value):
    if not value:
        return []
    if isinstance(value, str):
        value = value.split(",")
    if not isinstance(value, list):
        return []

    cleaned = []
    seen = set()
    for item in value:
        if isinstance(item, dict):
            text = (
                item.get("name")
                or item.get("title")
                or item.get("position")
                or item.get("issuer")
                or item.get("description")
                or " ".join(str(v).strip() for v in item.values() if str(v).strip())
            )
        else:
            text = str(item).strip()
        key = text.lower()
        if text and key not in seen:
            seen.add(key)
            cleaned.append(text)
    return cleaned


def _number(value, default=0.0):
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return default


def _score_ratio(value, maximum):
    return max(0, min(1, _number(value) / maximum))


def _profile_stack(profile):
    stack = []
    for field in ("skills", "programming_languages", "frameworks", "tools", "databases", "platforms", "technologies"):
        stack.extend(_clean_list(profile.get(field)))
    return _clean_list(stack)


def _domain_required_items(profile):
    domain = profile.get("interested_domain")
    if domain not in DOMAINS:
        return []

    required = []
    metadata = DOMAINS[domain]
    for field in ("skills", "programming_languages", "frameworks", "tools", "databases", "platforms", "technologies"):
        required.extend(metadata.get(field, []))
    return _clean_list(required)


def _match_score(profile):
    required = _domain_required_items(profile)
    if not required:
        stack_count = len(_profile_stack(profile))
        return min(100, stack_count * 6), [], []

    stack_keys = {item.lower() for item in _profile_stack(profile)}
    matched = [item for item in required if item.lower() in stack_keys]
    missing = [item for item in required if item.lower() not in stack_keys]
    return int(round((len(matched) / max(len(required), 1)) * 100)), matched, missing


def _academics_score(profile):
    cgpa_score = _score_ratio(profile.get("cgpa"), 10) * 70
    branch_bonus = 18 if str(profile.get("branch", "")).strip() else 0
    degree_bonus = 12 if str(profile.get("degree", "")).strip() else 0
    return min(100, cgpa_score + branch_bonus + degree_bonus)


def _coding_score(profile):
    leetcode_score = _score_ratio(profile.get("leetcode"), 600) * 70
    codechef_score = _score_ratio(profile.get("codechef_rating"), 2000) * 8
    codeforces_score = _score_ratio(profile.get("codeforces_rating"), 1900) * 7
    github_activity = _score_ratio(profile.get("github_activity"), 100) * 15
    if profile.get("github_profile") and github_activity == 0:
        github_activity = 8
    return min(100, leetcode_score + codechef_score + codeforces_score + github_activity)


def _technical_stack_score(profile):
    skill_match, matched, missing = _match_score(profile)
    breadth = min(100, len(_profile_stack(profile)) * 5)
    return round((skill_match * 0.7) + (breadth * 0.3), 2), matched, missing, skill_match


def _projects_score(profile):
    count_score = _score_ratio(profile.get("projects"), 5) * 65
    complexity = str(profile.get("project_complexity", "")).strip().lower()
    complexity_bonus = {"basic": 8, "intermediate": 20, "advanced": 35}.get(complexity, 0)
    stack_bonus = min(15, len(_profile_stack(profile)) * 2)
    return min(100, count_score + complexity_bonus + stack_bonus)


def _experience_score(profile):
    internships = _score_ratio(profile.get("internships"), 3) * 60
    certifications = min(25, len(_clean_list(profile.get("certifications"))) * 8)
    achievements = min(15, len(_clean_list(profile.get("achievements"))) * 5)
    hackathons = min(10, len(_clean_list(profile.get("hackathons"))) * 5)
    return min(100, internships + certifications + achievements + hackathons)


def _soft_skills_score(profile):
    communication = _score_ratio(profile.get("communication", profile.get("communication_score")), 10) * 60
    soft_skills = {item.lower() for item in _clean_list(profile.get("soft_skills"))}
    bonuses = 0
    for skill in ("problem solving", "teamwork", "leadership", "adaptability"):
        if skill in soft_skills:
            bonuses += 10
    return min(100, communication + bonuses)


def _weighted_total(component_scores):
    total = 0
    for name, weight in PREDICTION_WEIGHTS.items():
        total += component_scores[name] * (weight / 100)
    return round(max(0, min(100, total)), 2)


def _student_cluster(score):
    if score >= 82:
        return 3, "High Potential Candidate"
    if score >= 65:
        return 0, "Placement Ready"
    if score >= 45:
        return 1, "Needs Improvement"
    return 2, "Beginner"


def _salary_prediction(profile, probability):
    cgpa = _score_ratio(profile.get("cgpa"), 10)
    dsa = _score_ratio(profile.get("leetcode"), 600)
    projects = _score_ratio(profile.get("projects"), 5)
    internships = _score_ratio(profile.get("internships"), 3)
    communication = _score_ratio(profile.get("communication", profile.get("communication_score")), 10)
    readiness = _score_ratio(probability, 100)
    stack_depth = _score_ratio(len(_profile_stack(profile)), 12)

    complexity = str(profile.get("project_complexity", "")).strip().lower()
    complexity_bonus = {"basic": 0.15, "intermediate": 0.45, "advanced": 0.9}.get(complexity, 0)
    coding_bonus = 0
    if _number(profile.get("codechef_rating")) >= 1600:
        coding_bonus += 0.25
    if _number(profile.get("codeforces_rating")) >= 1400:
        coding_bonus += 0.25
    if profile.get("github_profile"):
        coding_bonus += 0.2

    salary = (
        2.4
        + (cgpa * 1.0)
        + (dsa * 1.2)
        + (projects * 1.45)
        + (internships * 1.35)
        + (communication * 0.65)
        + (readiness * 1.9)
        + (stack_depth * 0.75)
        + complexity_bonus
        + coding_bonus
    )

    if probability < 45:
        salary = min(salary, 4.2)
    elif probability < 60:
        salary = min(salary, 5.8)
    elif probability < 75:
        salary = min(salary, 7.8)
    elif probability < 88:
        salary = min(salary, 10.5)
    else:
        salary = min(salary, 14.0)

    minimum = 3.0 if probability >= 60 else 2.4
    return round(max(minimum, salary), 2)


def _recommendations(profile, missing_skills, component_scores):
    recommendations = []
    if component_scores["coding_profiles"] < 60:
        recommendations.append("Increase DSA consistency and add CodeChef/Codeforces/GitHub activity signals.")
    if component_scores["technical_stack"] < 70 and missing_skills:
        recommendations.append(f"Prioritize these target-domain skills: {', '.join(missing_skills[:4])}.")
    if component_scores["projects"] < 70:
        recommendations.append("Build 2-3 deployed projects with clear problem statements, measurable outcomes, and GitHub links.")
    if component_scores["experience"] < 60:
        recommendations.append("Add internships, certifications, hackathons, open-source work, or freelance experience.")
    if component_scores["soft_skills"] < 65:
        recommendations.append("Improve communication, problem solving, and teamwork signals with mock interviews and team projects.")
    return recommendations[:5]


def models_loaded():
    return True


def make_prediction(profile=None, cgpa=None, leetcode=None, projects=None, internships=None, communication=None):
    profile = dict(profile or {})
    if not profile:
        profile = {
            "cgpa": cgpa,
            "leetcode": leetcode,
            "projects": projects,
            "internships": internships,
            "communication": communication,
        }

    technical_score, matched_skills, missing_skills, skill_match = _technical_stack_score(profile)
    component_scores = {
        "academics": _academics_score(profile),
        "coding_profiles": _coding_score(profile),
        "technical_stack": technical_score,
        "projects": _projects_score(profile),
        "experience": _experience_score(profile),
        "soft_skills": _soft_skills_score(profile),
    }

    placement_probability = _weighted_total(component_scores)
    if component_scores["academics"] >= 70 and component_scores["technical_stack"] >= 55 and component_scores["projects"] >= 55:
        placement_probability = max(placement_probability, 58)
    if component_scores["coding_profiles"] >= 60 and component_scores["technical_stack"] >= 70:
        placement_probability = max(placement_probability, 68)
    placement_probability = round(min(100, placement_probability), 2)
    cluster_id, cluster_name = _student_cluster(placement_probability)
    resume_strength = int(round((component_scores["technical_stack"] * 0.35) + (component_scores["projects"] * 0.25) + (component_scores["experience"] * 0.25) + (component_scores["soft_skills"] * 0.15)))
    readiness_score = int(round((placement_probability * 0.7) + (skill_match * 0.3)))
    confidence_score = int(round(min(95, 45 + len(_profile_stack(profile)) * 2 + min(_number(profile.get("projects")) * 5, 20) + min(_number(profile.get("internships")) * 6, 18))))

    return {
        "placement_probability": placement_probability,
        "svm_prediction": 1 if placement_probability >= 60 else 0,
        "salary_prediction": _salary_prediction(profile, placement_probability),
        "student_cluster": cluster_name,
        "cluster_id": cluster_id,
        "readiness_score": readiness_score,
        "skill_match": skill_match,
        "resume_strength": max(0, min(100, resume_strength)),
        "confidence_score": confidence_score,
        "matched_skills": matched_skills[:10],
        "missing_skills": missing_skills[:10],
        "recommendations": _recommendations(profile, missing_skills, component_scores),
        "component_scores": {key: round(value, 2) for key, value in component_scores.items()},
        "weights": PREDICTION_WEIGHTS,
    }
