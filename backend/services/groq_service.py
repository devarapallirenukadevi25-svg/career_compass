import os
from groq import Groq


def format_list(values, display_key=None):
    formatted = []
    for value in values or []:
        if isinstance(value, dict):
            if display_key and value.get(display_key):
                formatted.append(str(value[display_key]))
            elif value:
                formatted.append(" - ".join(str(part) for part in value.values() if part))
        elif value:
            formatted.append(str(value))
    return ", ".join(formatted)


def generate_roadmap(profile, prediction, ats_result=None, skill_gap=None):
    api_key = os.getenv("GROQ_API_KEY")
    if api_key:
        api_key = api_key.strip("'").strip('"')
        
    if not api_key:
        return {"error": "GROQ_API_KEY is not set in the environment variables."}

    client = Groq(api_key=api_key)
    ats_result = ats_result or {}
    skill_gap = skill_gap or {}

    certifications = format_list(profile.get('certifications', []), 'name')

    prompt = f"""
    You are an expert AI Career Coach. Analyze the following student profile, ATS analysis, skill gaps, and machine learning placement predictions to generate a highly personalized career improvement roadmap.
    
    STUDENT PROFILE:
    - CGPA: {profile.get('cgpa')}
    - LeetCode Problems Solved: {profile.get('leetcode')}
    - Projects: {profile.get('projects')}
    - Internships: {profile.get('internships')}
    - Communication Score: {profile.get('communication')}/10
    - Interested Domain: {profile.get('interested_domain') or 'Not selected'}
    - Target Role: {skill_gap.get('target_role') or 'Recommended best fit'}
    - Skills: {format_list(profile.get('skills', []))}
    - Programming Languages: {format_list(profile.get('programming_languages', []))}
    - Frameworks: {format_list(profile.get('frameworks', []))}
    - Tools: {format_list(profile.get('tools', []))}
    - Certifications: {certifications}
    - GitHub: {'Provided' if profile.get('github_profile') else 'Missing'}
    - LinkedIn: {'Provided' if profile.get('linkedin_profile') else 'Missing'}

    ATS ANALYSIS:
    - ATS Score: {ats_result.get('ats_score', 'Not calculated')}
    - ATS Weaknesses: {', '.join(ats_result.get('weaknesses', []))}
    - Missing Resume Sections: {', '.join(ats_result.get('missing_sections', []))}
    - ATS Improvement Suggestions: {', '.join(ats_result.get('improvement_suggestions', []))}

    SKILL GAP:
    - Current Matching Skills: {', '.join(skill_gap.get('current_skills', []))}
    - Missing Skills: {', '.join(skill_gap.get('missing_skills', []))}
    - Recommended Certifications: {', '.join(skill_gap.get('recommended_certifications', []))}
    
    PREDICTION RESULTS:
    - Placement Probability: {prediction.get('placement_probability')}%
    - SVM Prediction: {'Placed' if prediction.get('svm_prediction') == 1 else 'Not Placed'}
    - Expected Salary: {prediction.get('salary_prediction')} LPA
    - Student Cluster Assignment: {prediction.get('student_cluster')}
    
    Based on this data, provide a structured response in the following format using markdown:
    
    ### 1. Strengths
    [List 2-3 key strengths based on the profile]
    
    ### 2. Weaknesses
    [List 2-3 areas that need improvement]
    
    ### 3. Missing Skills
    [Suggest 2-3 specific tech skills they should learn based on their current skills and industry trends]
    
    ### 4. Personalized 4-Month Roadmap
    - **Month 1:** [Skills to learn, resume fixes, DSA target, and one measurable task]
    - **Month 2:** [Project to build, missing skills to cover, and GitHub/LinkedIn improvements]
    - **Month 3:** [Certification preparation, interview preparation, and advanced project milestone]
    - **Month 4:** [Mock interviews, application strategy, final DSA goals, and portfolio polish]
    
    ### 5. Interview Preparation Strategy
    [Actionable advice on technical, HR, resume, and DSA preparation]
    
    ### 6. Recommended Projects
    [Suggest 2 project ideas that would elevate their resume]
    
    ### 7. Certifications and DSA Goals
    [Recommend certifications and weekly DSA goals aligned with the target role]

    ### 8. Company Preparation Plan
    [Based on their cluster ({prediction.get('student_cluster')}), suggest the types of companies they should target (e.g., FAANG, Startups, Service-based) and how to approach them]
    """

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert AI Career Coach. Output ONLY markdown formatted text as requested. Do not include introductory or concluding conversational text."
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.1-8b-instant",
            temperature=0.7,
            max_tokens=1500,
        )
        
        roadmap_text = chat_completion.choices[0].message.content
        return {"roadmap_text": roadmap_text}
        
    except Exception as e:
        return {"error": f"Failed to generate roadmap: {str(e)}"}
