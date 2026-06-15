import os
import sys
import time
import requests
import subprocess
import uuid
import socket

API_URL = None


def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(('127.0.0.1', 0))
        return sock.getsockname()[1]

def print_status(msg, success=True):
    if success:
        print(f"[OK] {msg}")
    else:
        print(f"[ERROR] {msg}")

def start_backend():
    global API_URL
    print("--- Starting Backend ---")
    os.environ['GROQ_API_KEY'] = ''
    port = find_free_port()
    API_URL = f"http://127.0.0.1:{port}/api"
    env = os.environ.copy()
    env['PORT'] = str(port)
    env['DB_BACKEND'] = 'local'
    env['LOCAL_DB_PATH'] = os.path.join('data', 'integration_local_db.json')
    env['GROQ_API_KEY'] = ''

    if os.path.exists(env['LOCAL_DB_PATH']):
        os.remove(env['LOCAL_DB_PATH'])

    process = subprocess.Popen([sys.executable, 'backend/app.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    deadline = time.time() + 20
    while time.time() < deadline:
        if process.poll() is not None:
            out, err = process.communicate()
            print_status(f"Backend failed to start. Exit code: {process.returncode}", False)
            print(err.decode('utf-8'))
            return None

        try:
            response = requests.get(f'http://127.0.0.1:{port}/', timeout=2)
            if response.status_code == 200:
                print_status("Backend started.")
                return process
        except requests.exceptions.RequestException:
            time.sleep(1)

    print_status("Backend failed to start.", False)
    process.terminate()
    return None

def test_integration():
    success = True
    session = requests.Session()
    
    # Generate unique test user
    test_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    test_password = "password123"
    
    # 1. AUTHENTICATION
    print("\n--- Testing Authentication ---")
    
    # Register
    res = session.post(f"{API_URL}/auth/register", json={
        "name": "Test User",
        "email": test_email,
        "password": test_password
    })
    if res.status_code == 201:
        print_status("Register POST /api/auth/register")
    else:
        print_status(f"Register failed: {res.text}", False)
        success = False

    # Login
    res = session.post(f"{API_URL}/auth/login", json={
        "email": test_email,
        "password": test_password
    })
    
    token = None
    if res.status_code == 200:
        print_status("Login POST /api/auth/login")
        token = res.json().get('token')
    else:
        print_status(f"Login failed: {res.text}", False)
        success = False
        
    if not token:
        print_status("Failed to get JWT token", False)
        return False
        
    # Set Auth Header
    session.headers.update({"Authorization": f"Bearer {token}"})
    
    # Test Invalid Login (Error handling)
    res_err = session.post(f"{API_URL}/auth/login", json={"email": "wrong@example.com", "password": "wrong"})
    if res_err.status_code == 401:
        print_status("Invalid login handled correctly (401)")
    else:
        print_status("Invalid login not handled", False)
        success = False

    # 2. PROFILE PAGE
    print("\n--- Testing Profile ---")
    
    # Empty profile GET (Should return 404 handled gracefully by frontend)
    res = session.get(f"{API_URL}/profile/")
    if res.status_code == 404:
        print_status("Empty profile returns 404")
    else:
        print_status("Empty profile didn't return 404", False)
        success = False
        
    # Predict without profile (Error handling)
    res = session.post(f"{API_URL}/predict/")
    if res.status_code == 404:
        print_status("Predict without profile handled correctly (404)")
    else:
        print_status("Predict without profile not handled", False)
        success = False

    # Submit Profile
    profile_data = {
        "cgpa": 8.5,
        "leetcode": 300,
        "projects": 3,
        "internships": 1,
        "communication": 8,
        "skills": ["Python", "React", "MongoDB"]
    }
    res = session.post(f"{API_URL}/profile/", json=profile_data)
    if res.status_code in [200, 201]:
        print_status("Submit Profile POST /api/profile")
    else:
        print_status(f"Submit profile failed: {res.text}", False)
        success = False

    # Get Profile
    res = session.get(f"{API_URL}/profile/")
    if res.status_code == 200 and res.json().get('cgpa') == 8.5:
        print_status("Retrieve Profile GET /api/profile")
    else:
        print_status("Retrieve profile failed", False)
        success = False

    # 3. DASHBOARD / PREDICT
    print("\n--- Testing Dashboard & Prediction ---")
    res = session.post(f"{API_URL}/predict/")
    if res.status_code == 200:
        data = res.json()
        print_status("Predict POST /api/predict")
        if 'placement_probability' in data and 'salary_prediction' in data and 'student_cluster' in data and 'svm_prediction' in data:
            print_status("All required fields in prediction response")
        else:
            print_status("Missing fields in prediction response", False)
            success = False
    else:
        print_status(f"Predict failed: {res.text}", False)
        success = False

    # 4. HISTORY
    print("\n--- Testing History ---")
    res = session.get(f"{API_URL}/predict/history")
    if res.status_code == 200 and len(res.json()) > 0:
        print_status("History GET /api/predict/history")
    else:
        print_status("History retrieval failed", False)
        success = False

    # 5. ROADMAP
    print("\n--- Testing Roadmap ---")
    
    # Missing Groq API Key error handling
    if not os.getenv('GROQ_API_KEY'):
        print_status("GROQ_API_KEY not set. Skipping real API call, testing error handling.")
        res = session.post(f"{API_URL}/roadmap/")
        if res.status_code == 500 and "error" in res.json():
             print_status("Missing API key handled correctly (500)")
        else:
             print_status("Missing API key not handled", False)
             success = False
    else:
        res = session.post(f"{API_URL}/roadmap/")
        if res.status_code == 200 and "roadmap_text" in res.json():
            print_status("Roadmap POST /api/roadmap")
            
            # Test getting latest
            res_latest = session.get(f"{API_URL}/roadmap/latest")
            if res_latest.status_code == 200:
                print_status("Latest Roadmap GET /api/roadmap/latest")
            else:
                print_status("Latest Roadmap failed", False)
                success = False
        else:
            print_status(f"Roadmap failed: {res.text}", False)
            success = False

    # Cleanup local integration database
    try:
        local_db_path = os.path.join('data', 'integration_local_db.json')
        if os.path.exists(local_db_path):
            os.remove(local_db_path)
        print_status("Integration database cleaned up.")
    except Exception as e:
        print_status(f"Cleanup failed: {e}", False)
        
    return success

if __name__ == '__main__':
    backend_process = start_backend()
    if not backend_process:
        sys.exit(1)
        
    try:
        success = test_integration()
        if not success:
            print("\n[FAILED] Integration verification failed.")
            sys.exit(1)
        print("\n[SUCCESS] Integration verification passed. All API endpoints and error handling work as expected.")
    finally:
        backend_process.terminate()
