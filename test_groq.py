import os
from dotenv import load_dotenv
from backend.services.groq_service import generate_roadmap

load_dotenv()

def test_groq():
    profile = {
        "cgpa": 8.5,
        "leetcode": 120,
        "projects": 2,
        "internships": 1,
        "communication": 7,
        "skills": ["React", "Python"]
    }
    prediction = {
        "placement_probability": 75.5,
        "svm_prediction": 1,
        "salary_prediction": 6.5,
        "student_cluster": "Needs Improvement"
    }

    print("Testing Groq API integration...")
    result = generate_roadmap(profile, prediction)
    
    if "error" in result:
        print(f"FAILED: {result['error']}")
    else:
        print("SUCCESS! Roadmap generated:")
        print("-" * 50)
        print(result["roadmap_text"])
        print("-" * 50)

if __name__ == "__main__":
    test_groq()
