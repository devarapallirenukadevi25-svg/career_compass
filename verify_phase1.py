import os
import sys
import subprocess
import time
import requests

def print_status(msg, success=True):
    if success:
        print(f"[OK] {msg}")
    else:
        print(f"[ERROR] {msg}")

def check_files():
    print("--- Checking Files ---")
    files_to_check = [
        'dataset/career_data.csv',
        'trained_models/scaler.pkl',
        'trained_models/logistic.pkl',
        'trained_models/linear.pkl',
        'trained_models/svm.pkl',
        'trained_models/kmeans.pkl',
        'backend/app.py',
        'backend/utils/db.py',
        'backend/routes/auth.py',
        'backend/routes/predict.py',
        'backend/routes/profile.py',
        'backend/routes/roadmap.py',
        'backend/services/predict_service.py',
        'backend/services/groq_service.py'
    ]
    all_good = True
    for f in files_to_check:
        if os.path.exists(f):
            print_status(f"File exists: {f}")
        else:
            print_status(f"Missing file: {f}", False)
            all_good = False
    return all_good

def check_syntax():
    print("--- Checking Syntax ---")
    all_good = True
    for root, dirs, files in os.walk('backend'):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r') as source:
                        compile(source.read(), filepath, 'exec')
                    print_status(f"Syntax OK: {filepath}")
                except Exception as e:
                    print_status(f"Syntax error in {filepath}: {e}", False)
                    all_good = False
    return all_good

def check_flask_startup():
    print("--- Checking Flask Startup ---")
    os.environ['PORT'] = '5555'
    process = subprocess.Popen([sys.executable, 'backend/app.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        deadline = time.time() + 20
        last_error = None
        while time.time() < deadline:
            if process.poll() is not None:
                out, err = process.communicate()
                print_status(f"Flask failed to start. Exit code: {process.returncode}", False)
                print(f"Stderr: {err.decode('utf-8')}")
                return False

            try:
                response = requests.get('http://127.0.0.1:5555/', timeout=2)
                if response.status_code == 200:
                    print_status("Flask server health check passed (Status 200).")
                    return True
                last_error = f"Status {response.status_code}"
            except requests.exceptions.RequestException as exc:
                last_error = str(exc)
            time.sleep(1)

        print_status(f"Flask server did not become ready on port 5555: {last_error}", False)
        return False
    finally:
        process.terminate()

if __name__ == '__main__':
    if not check_files():
        sys.exit(1)
    if not check_syntax():
        sys.exit(1)
    if not check_flask_startup():
        sys.exit(1)
        
    print("All Phase 1 checks passed successfully!")
