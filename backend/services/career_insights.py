from services.domain_catalog import DOMAINS


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
                or ""
            )
            if not text:
                text = " ".join(str(v).strip() for v in item.values() if str(v).strip())
        else:
            text = str(item).strip()
        key = text.lower()
        if text and key not in seen:
            seen.add(key)
            cleaned.append(text)
    return cleaned


def _profile_skills(profile):
    combined = []
    for field in ("skills", "programming_languages", "frameworks", "tools", "databases", "platforms", "technologies", "soft_skills"):
        combined.extend(_clean_list(profile.get(field)))
    return _clean_list(combined)


def _matches(candidate_values, required_values):
    candidate_keys = {item.lower() for item in _clean_list(candidate_values)}
    matched = []
    missing = []

    for required in _clean_list(required_values):
        required_key = required.lower()
        if required_key in candidate_keys:
            matched.append(required)
        else:
            missing.append(required)
    return matched, missing


ROLE_REQUIREMENTS = {
    "ML Engineer": {
        "skills": ["Machine Learning", "Deep Learning", "Model Evaluation", "Feature Engineering", "MLOps"],
        "courses": ["Machine Learning Specialization", "Deep Learning Specialization", "MLOps Fundamentals"],
        "certifications": ["TensorFlow Developer Certificate", "AWS Machine Learning Specialty"],
        "salary_range": "5-12 LPA",
    },
    "Data Scientist": {
        "skills": ["Statistics", "Machine Learning", "Data Wrangling", "Experiment Design", "SQL"],
        "courses": ["IBM Data Science Professional Certificate", "Applied Statistics", "Feature Engineering"],
        "certifications": ["IBM Data Science Professional Certificate", "Microsoft Azure Data Scientist"],
        "salary_range": "5-11 LPA",
    },
    "Data Analyst": {
        "skills": ["SQL Analysis", "Dashboarding", "Data Cleaning", "Business Analysis", "Excel", "Power BI"],
        "courses": ["Google Data Analytics", "Power BI Dashboarding", "Advanced SQL"],
        "certifications": ["Google Data Analytics Professional Certificate", "Microsoft Power BI Data Analyst"],
        "salary_range": "3-7 LPA",
    },
    "Backend Developer": {
        "skills": ["API Development", "Database Design", "Authentication", "System Design", "REST APIs"],
        "courses": ["Backend API Design", "Database Systems", "System Design Basics"],
        "certifications": ["Meta Back-End Developer Certificate", "MongoDB Developer Certification"],
        "salary_range": "4-9 LPA",
    },
    "Frontend Developer": {
        "skills": ["Responsive UI", "State Management", "Accessibility", "Performance Optimization", "React"],
        "courses": ["Advanced React", "Frontend Performance", "Web Accessibility"],
        "certifications": ["Meta Front-End Developer Certificate", "freeCodeCamp Front End Libraries"],
        "salary_range": "3.5-8 LPA",
    },
    "Full Stack Developer": {
        "skills": ["API Design", "Frontend Development", "Backend Development", "Database Design", "Authentication"],
        "courses": ["Full Stack Web Development", "MERN Stack", "Cloud Deployment"],
        "certifications": ["Meta Full-Stack Engineer Certificate", "MongoDB Developer Certification"],
        "salary_range": "4-10 LPA",
    },
    "Cloud Engineer": {
        "skills": ["Cloud Architecture", "Networking", "Security", "Containers", "Kubernetes"],
        "courses": ["AWS Cloud Foundations", "Kubernetes Basics", "Cloud Networking"],
        "certifications": ["AWS Cloud Practitioner", "Google Associate Cloud Engineer"],
        "salary_range": "4.5-10 LPA",
    },
    "DevOps Engineer": {
        "skills": ["CI/CD", "Infrastructure as Code", "Monitoring", "Docker", "Kubernetes"],
        "courses": ["DevOps on AWS", "Terraform Associate Prep", "Kubernetes for Developers"],
        "certifications": ["Docker Certified Associate", "HashiCorp Terraform Associate"],
        "salary_range": "4.5-10 LPA",
    },
    "Cyber Security Analyst": {
        "skills": ["Network Security", "Threat Analysis", "Vulnerability Assessment", "Incident Response", "SIEM"],
        "courses": ["Security Operations", "Ethical Hacking Basics", "Network Defense"],
        "certifications": ["CompTIA Security+", "Certified Ethical Hacker"],
        "salary_range": "4-9 LPA",
    },
    "Software Engineer": {
        "skills": ["DSA", "System Design", "Testing", "Code Review", "APIs"],
        "courses": ["Data Structures and Algorithms", "System Design Fundamentals", "Clean Code"],
        "certifications": ["Oracle Java Certification", "AWS Developer Associate"],
        "salary_range": "4-11 LPA",
    },
    "Mobile Developer": {
        "skills": ["Mobile UI", "API Integration", "Offline Storage", "Push Notifications", "Firebase"],
        "courses": ["Flutter Development", "React Native Apps", "Android Architecture"],
        "certifications": ["Google Associate Android Developer", "Flutter Certified Application Developer"],
        "salary_range": "3.5-8 LPA",
    },
    "Blockchain Developer": {
        "skills": ["Smart Contracts", "Token Standards", "Web3 Integration", "Security Auditing", "Solidity"],
        "courses": ["Ethereum Smart Contracts", "Web3 Development", "Blockchain Security"],
        "certifications": ["Certified Blockchain Developer", "Ethereum Developer Certification"],
        "salary_range": "5-12 LPA",
    },
    "QA Engineer": {
        "skills": ["Test Planning", "Automation Testing", "Bug Reporting", "API Testing", "Regression Testing"],
        "courses": ["Selenium Automation", "API Testing with Postman", "Testing Fundamentals"],
        "certifications": ["ISTQB Foundation", "Certified Selenium Tester"],
        "salary_range": "3-6.5 LPA",
    },
    "UI/UX Designer": {
        "skills": ["User Research", "Accessibility", "Design Systems", "Analytics", "Product Thinking"],
        "courses": ["Google UX Design", "Design Systems", "Product Analytics"],
        "certifications": ["Google UX Design Certificate", "Product Analytics Certification"],
        "salary_range": "3-7 LPA",
    },
    "Game Developer": {
        "skills": ["Game Mechanics", "Physics", "Level Design", "Optimization", "3D Rendering"],
        "courses": ["Unity Game Development", "Unreal Engine Basics", "Game Physics"],
        "certifications": ["Unity Certified User", "Unreal Engine Certification"],
        "salary_range": "3-8 LPA",
    },
}


DOMAIN_TO_ROLES = {
    "Artificial Intelligence / Machine Learning": ["ML Engineer", "Data Scientist", "Software Engineer"],
    "AI/ML": ["ML Engineer", "Data Scientist", "Software Engineer"],
    "Data Science": ["Data Scientist", "ML Engineer", "Data Analyst"],
    "Data Analytics": ["Data Analyst", "Data Scientist", "Product Engineering"],
    "Cloud Computing": ["Cloud Engineer", "DevOps Engineer", "Backend Developer"],
    "Cyber Security": ["Cyber Security Analyst", "Software Engineer", "Cloud Engineer"],
    "DevOps": ["DevOps Engineer", "Cloud Engineer", "Backend Developer"],
    "Software Development": ["Software Engineer", "Backend Developer", "Full Stack Developer"],
    "Software Engineering": ["Software Engineer", "Backend Developer", "Full Stack Developer"],
    "Frontend": ["Frontend Developer", "Full Stack Developer", "UI/UX Designer"],
    "Frontend Development": ["Frontend Developer", "Full Stack Developer", "UI/UX Designer"],
    "Backend": ["Backend Developer", "Software Engineer", "Full Stack Developer"],
    "Backend Development": ["Backend Developer", "Software Engineer", "Full Stack Developer"],
    "Full Stack": ["Full Stack Developer", "Backend Developer", "Frontend Developer"],
    "Full Stack Development": ["Full Stack Developer", "Backend Developer", "Frontend Developer"],
    "Mobile Development": ["Mobile Developer", "Software Engineer", "Frontend Developer"],
    "Mobile App Development": ["Mobile Developer", "Software Engineer", "Frontend Developer"],
    "Blockchain": ["Blockchain Developer", "Backend Developer", "Software Engineer"],
    "Testing": ["QA Engineer", "Software Engineer", "Backend Developer"],
    "QA / Testing": ["QA Engineer", "Software Engineer", "Backend Developer"],
    "UI/UX": ["UI/UX Designer", "Frontend Developer", "Product Engineering"],
    "Game Development": ["Game Developer", "Software Engineer", "Mobile Developer"],
}


def calculate_ats(profile):
    strengths = []
    weaknesses = []
    missing_sections = []
    suggestions = []
    score = 0

    skills = _profile_skills(profile)
    certifications = _clean_list(profile.get("certifications"))
    achievements = _clean_list(profile.get("achievements"))
    education = _clean_list(profile.get("education"))
    projects = int(profile.get("projects", 0) or 0)
    internships = int(profile.get("internships", 0) or 0)
    communication = int(profile.get("communication", profile.get("communication_score", 0)) or 0)

    if skills:
        skill_score = min(len(skills), 12) * 2
        score += min(skill_score, 24)
        strengths.append(f"{len(skills)} technical skills listed")
    else:
        missing_sections.append("Skills")
        weaknesses.append("No explicit technical skills were found")
        suggestions.append("Add 8-10 role-specific skills from your target domain")

    if projects >= 3:
        score += 20
        strengths.append("Strong project count")
    elif projects > 0:
        score += 10 + projects * 2
        weaknesses.append("Project portfolio can be stronger")
        suggestions.append("Add deployed projects with metrics, tech stack, and GitHub links")
    else:
        missing_sections.append("Projects")
        suggestions.append("Add at least two substantial projects aligned with your target role")

    if internships >= 2:
        score += 15
        strengths.append("Multiple internships improve recruiter confidence")
    elif internships == 1:
        score += 10
    else:
        missing_sections.append("Internships")
        weaknesses.append("No internship experience listed")
        suggestions.append("Add internship, freelance, open-source, or simulated industry experience")

    if certifications:
        score += min(10, len(certifications) * 4)
        strengths.append("Certifications included")
    else:
        missing_sections.append("Certifications")
        suggestions.append("Add one recognized certification for the selected domain")

    if achievements:
        score += min(8, len(achievements) * 4)
        strengths.append("Achievements or awards included")
    else:
        missing_sections.append("Achievements")
        suggestions.append("Add achievements, awards, hackathons, or measurable outcomes")

    if education or profile.get("degree") or profile.get("branch"):
        score += 8
        strengths.append("Education details are available")
    else:
        missing_sections.append("Education")
        weaknesses.append("Education details are missing")
        suggestions.append("Add degree, branch, college, CGPA, and graduation year")

    if profile.get("github_profile"):
        score += 10
        strengths.append("GitHub profile is available")
    else:
        missing_sections.append("GitHub")
        suggestions.append("Add a GitHub profile with pinned projects")

    if profile.get("linkedin_profile"):
        score += 10
        strengths.append("LinkedIn profile is available")
    else:
        missing_sections.append("LinkedIn")
        suggestions.append("Add a complete LinkedIn profile URL")

    if profile.get("resume_text"):
        score += 5
        strengths.append("Resume text is available for analysis")
    else:
        missing_sections.append("Resume upload")
        suggestions.append("Upload a text-based PDF resume for deeper analysis")

    if communication >= 8:
        score += 7
        strengths.append("Strong communication score")
    elif communication >= 5:
        score += 4
        weaknesses.append("Communication score is moderate")
    else:
        weaknesses.append("Communication score needs improvement")
        suggestions.append("Practice mock interviews and concise project explanations")

    return {
        "ats_score": max(0, min(100, int(round(score)))),
        "strengths": strengths[:6],
        "weaknesses": weaknesses[:6],
        "missing_sections": missing_sections[:8],
        "improvement_suggestions": suggestions[:8],
    }


def analyze_skill_gap(profile, target_role):
    role_name = target_role if target_role in ROLE_REQUIREMENTS else recommend_roles(profile)[0]["role_name"]
    requirement = ROLE_REQUIREMENTS[role_name]
    current_skills, missing_skills = _matches(_profile_skills(profile), requirement["skills"])
    readiness_score = int(round((len(current_skills) / max(len(requirement["skills"]), 1)) * 100))

    return {
        "target_role": role_name,
        "current_skills": current_skills,
        "missing_skills": missing_skills,
        "recommended_courses": requirement["courses"][:4],
        "recommended_certifications": requirement["certifications"][:4],
        "readiness_score": readiness_score,
    }


def recommend_roles(profile):
    candidate_skills = _profile_skills(profile)
    domain = profile.get("interested_domain") or ""
    preferred_roles = set(DOMAIN_TO_ROLES.get(domain, []))
    ats_score = int(profile.get("ats_score", 0) or 0)
    projects = int(profile.get("projects", 0) or 0)
    internships = int(profile.get("internships", 0) or 0)

    recommendations = []
    for role_name, requirement in ROLE_REQUIREMENTS.items():
        matched, missing = _matches(candidate_skills, requirement["skills"])
        skill_score = (len(matched) / max(len(requirement["skills"]), 1)) * 70
        experience_score = min(15, projects * 3 + internships * 4)
        ats_bonus = min(10, ats_score / 10)
        domain_bonus = 5 if role_name in preferred_roles else 0
        match_percentage = int(round(min(100, skill_score + experience_score + ats_bonus + domain_bonus)))

        reasoning_parts = []
        if matched:
            reasoning_parts.append(f"Matches {', '.join(matched[:3])}")
        if role_name in preferred_roles:
            reasoning_parts.append("Aligned with selected domain")
        if missing:
            reasoning_parts.append(f"Needs {', '.join(missing[:2])}")

        recommendations.append({
            "role_name": role_name,
            "match_percentage": match_percentage,
            "salary_range": requirement["salary_range"],
            "reasoning": "; ".join(reasoning_parts) or "Based on profile breadth and career signals",
        })

    return sorted(recommendations, key=lambda item: item["match_percentage"], reverse=True)[:5]


def calculate_domain_match(profile):
    selected_domain = profile.get("interested_domain")
    domain_names = [selected_domain] if selected_domain in DOMAINS else list(DOMAINS.keys())
    candidate_values = _profile_skills(profile)
    results = []

    for domain_name in domain_names:
        domain = DOMAINS[domain_name]
        required = []
        for field in ("skills", "technologies", "programming_languages", "frameworks", "tools", "databases", "platforms"):
            required.extend(domain.get(field, []))
        matched, missing = _matches(candidate_values, required)
        score = int(round((len(matched) / max(len(_clean_list(required)), 1)) * 100))
        results.append({
            "domain_name": domain_name,
            "match_percentage": score,
            "matched_items": matched[:10],
            "missing_items": missing[:10],
            "recommended_certifications": domain.get("certifications", [])[:4],
        })

    return sorted(results, key=lambda item: item["match_percentage"], reverse=True)[0]


def build_resume_summary(profile):
    return {
        "has_resume": bool(profile.get("resume_text")),
        "resume_url": profile.get("resume_url", ""),
        "skills_count": len(_clean_list(profile.get("skills"))),
        "languages_count": len(_clean_list(profile.get("programming_languages"))),
        "frameworks_count": len(_clean_list(profile.get("frameworks"))),
        "tools_count": len(_clean_list(profile.get("tools"))),
        "databases_count": len(_clean_list(profile.get("databases"))),
        "platforms_count": len(_clean_list(profile.get("platforms"))),
        "technologies_count": len(_clean_list(profile.get("technologies"))),
        "certifications_count": len(_clean_list(profile.get("certifications"))),
    }
