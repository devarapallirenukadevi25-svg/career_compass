import os
import socket
import subprocess
import sys
import tempfile
import time
import uuid

import requests
from bson import json_util


API_URL = None
LOCAL_DB_PATH = os.path.join("data", "career_pro_local_db.json")


def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def print_status(message, success=True):
    prefix = "[OK]" if success else "[ERROR]"
    print(f"{prefix} {message}")


def start_backend():
    global API_URL
    port = find_free_port()
    API_URL = f"http://127.0.0.1:{port}/api"
    os.environ["GROQ_API_KEY"] = ""
    env = os.environ.copy()
    env["PORT"] = str(port)
    env["DB_BACKEND"] = "local"
    env["LOCAL_DB_PATH"] = LOCAL_DB_PATH
    env["GROQ_API_KEY"] = ""

    if os.path.exists(LOCAL_DB_PATH):
        os.remove(LOCAL_DB_PATH)

    process = subprocess.Popen(
        [sys.executable, "backend/app.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )

    deadline = time.time() + 20
    while time.time() < deadline:
        if process.poll() is not None:
            _, err = process.communicate()
            print_status(f"Backend failed to start. Exit code: {process.returncode}", False)
            print(err.decode("utf-8"))
            return None

        try:
            response = requests.get(f"http://127.0.0.1:{port}/", timeout=2)
            if response.status_code == 200:
                print_status("Backend started.")
                return process
        except requests.exceptions.RequestException:
            time.sleep(1)

    process.terminate()
    print_status("Backend failed to become ready.", False)
    return None


def make_text_pdf(text):
    escaped = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    stream = f"BT /F1 12 Tf 72 720 Td ({escaped}) Tj ET"
    objects = [
        "1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n",
        "2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n",
        "3 0 obj << /Type /Page /Parent 2 0 R /Resources << /Font << /F1 4 0 R >> >> /MediaBox [0 0 612 792] /Contents 5 0 R >> endobj\n",
        "4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n",
        f"5 0 obj << /Length {len(stream)} >> stream\n{stream}\nendstream endobj\n",
    ]
    content = "%PDF-1.4\n"
    offsets = [0]
    for obj in objects:
        offsets.append(len(content.encode("utf-8")))
        content += obj
    xref_offset = len(content.encode("utf-8"))
    content += f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n"
    for offset in offsets[1:]:
        content += f"{offset:010d} 00000 n \n"
    content += f"trailer << /Root 1 0 R /Size {len(objects) + 1} >>\nstartxref\n{xref_offset}\n%%EOF\n"
    return content.encode("utf-8")


def assert_status(response, expected, label):
    if response.status_code == expected:
        print_status(label)
        return True
    print_status(f"{label} failed: {response.status_code} {response.text}", False)
    return False


def verify():
    session = requests.Session()
    email = f"pro_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"
    success = True

    response = session.post(f"{API_URL}/auth/register", json={
        "name": "Career Pro Test",
        "email": email,
        "password": password,
    })
    success &= assert_status(response, 201, "Register test user")

    response = session.post(f"{API_URL}/auth/login", json={"email": email, "password": password})
    success &= assert_status(response, 200, "Login test user")
    token = response.json().get("token")
    session.headers.update({"Authorization": f"Bearer {token}"})

    profile = {
        "cgpa": 8.4,
        "leetcode": 260,
        "projects": 3,
        "internships": 1,
        "communication": 8,
        "skills": ["API Development", "Database Design", "React", "Docker"],
        "programming_languages": ["Python", "JavaScript", "SQL"],
        "frameworks": ["Flask", "React"],
        "tools": ["Git", "Postman", "Docker"],
        "certifications": [{"name": "MongoDB Developer Certification", "issuer": "MongoDB", "year": 2025}],
        "interested_domain": "Backend Development",
        "github_profile": "https://github.com/example",
        "linkedin_profile": "https://linkedin.com/in/example",
    }
    response = session.post(f"{API_URL}/profile/", json=profile)
    success &= response.status_code in (200, 201)
    print_status("Save extended profile", response.status_code in (200, 201))

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as pdf_file:
        pdf_file.write(make_text_pdf(
            "Skills Python React Docker API Development Database Design. "
            "Projects: - Career Compass API. Certifications: MongoDB Developer Certification. "
            "Experience: - Backend internship."
        ))
        pdf_path = pdf_file.name

    try:
        with open(pdf_path, "rb") as file_obj:
            response = session.post(
                f"{API_URL}/profile/resume",
                files={"resume": ("resume.pdf", file_obj, "application/pdf")},
            )
        success &= assert_status(response, 200, "Upload and analyze PDF resume")
    finally:
        try:
            os.remove(pdf_path)
        except OSError:
            pass

    response = session.get(f"{API_URL}/insights/roles")
    success &= assert_status(response, 200, "List insight roles")

    response = session.get(f"{API_URL}/insights/ats")
    success &= assert_status(response, 200, "Calculate ATS score")
    ats_score = response.json().get("ats_score", -1)
    success &= 0 <= ats_score <= 100
    print_status("ATS score is in range", 0 <= ats_score <= 100)

    response = session.get(f"{API_URL}/insights/ats/history")
    success &= assert_status(response, 200, "Read ATS history")
    success &= len(response.json()) > 0
    print_status("ATS history persisted", len(response.json()) > 0)

    response = session.post(f"{API_URL}/insights/skill-gap", json={"target_role": "Backend Developer"})
    success &= assert_status(response, 200, "Skill gap analysis")

    response = session.get(f"{API_URL}/insights/role-recommendations")
    success &= assert_status(response, 200, "Role recommendations")
    success &= len(response.json().get("recommendations", [])) == 5
    print_status("Top 5 roles returned", len(response.json().get("recommendations", [])) == 5)

    response = session.get(f"{API_URL}/insights/domain-match")
    success &= assert_status(response, 200, "Domain match")

    response = session.get(f"{API_URL}/insights/summary?target_role=Backend%20Developer")
    success &= assert_status(response, 200, "Insight summary")

    response = session.post(f"{API_URL}/predict/")
    success &= assert_status(response, 200, "Generate prediction")

    response = session.post(f"{API_URL}/roadmap/")
    if os.getenv("GROQ_API_KEY"):
        success &= assert_status(response, 200, "Generate upgraded roadmap")
    else:
        success &= assert_status(response, 500, "Missing Groq API key handled")

    try:
        with open(LOCAL_DB_PATH, "r", encoding="utf-8") as handle:
            local_data = json_util.loads(handle.read())
        users = local_data.get("users", [])
        user = next((item for item in users if item.get("email") == email), None)
        if user:
            user_id = str(user["_id"])
            ats_count = len([
                item for item in local_data.get("ats_history", [])
                if item.get("user_id") == user_id
            ])
            success &= ats_count > 0
            print_status("Local ats_history write verified", ats_count > 0)
        if os.path.exists(LOCAL_DB_PATH):
            os.remove(LOCAL_DB_PATH)
        print_status("Career Pro local database cleaned up")
    except Exception as exc:
        print_status(f"Cleanup or local verification failed: {exc}", False)
        success = False

    return success


if __name__ == "__main__":
    backend = start_backend()
    if not backend:
        sys.exit(1)

    try:
        if not verify():
            print("\n[FAILED] Career Compass Pro verification failed.")
            sys.exit(1)
        print("\n[SUCCESS] Career Compass Pro verification passed.")
    finally:
        backend.terminate()
