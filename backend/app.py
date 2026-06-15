import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from routes.auth import auth_bp
from routes.profile import profile_bp
from routes.predict import predict_bp
from routes.roadmap import roadmap_bp
from routes.insights import insights_bp
from services.predict_service import models_loaded
from utils.db import get_db, get_db_status

load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))

app = Flask(__name__)
app.url_map.strict_slashes = False

# Configure CORS
CORS(
    app,
    resources={r"/api/*": {"origins": os.getenv("CORS_ORIGINS", "*").split(",")}},
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# JWT Config
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev_fallback_secret')
jwt = JWTManager(app)

@jwt.unauthorized_loader
def missing_token(error):
    print(f"[jwt] missing token error={error}")
    return jsonify({"error": "Authorization token is required"}), 401

@jwt.invalid_token_loader
def invalid_token(error):
    print(f"[jwt] invalid token error={error}")
    return jsonify({"error": "Invalid authorization token"}), 422

@jwt.expired_token_loader
def expired_token(jwt_header, jwt_payload):
    print(f"[jwt] expired token identity={jwt_payload.get('sub')}")
    return jsonify({"error": "Authorization token has expired"}), 401

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(profile_bp, url_prefix='/api/profile')
app.register_blueprint(predict_bp, url_prefix='/api/predict')
app.register_blueprint(roadmap_bp, url_prefix='/api/roadmap')
app.register_blueprint(insights_bp, url_prefix='/api/insights')

print("[app] Registered routes:")
for rule in sorted(app.url_map.iter_rules(), key=lambda route: str(route)):
    methods = ",".join(sorted(rule.methods - {"HEAD", "OPTIONS"}))
    print(f"[app]   {methods:12s} {rule}")

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "Career Compass API is running"}), 200

@app.route('/api/health', methods=['GET'])
def api_health_check():
    database_ok = False
    db_status = get_db_status()
    try:
        get_db().client.admin.command('ping')
        database_ok = True
    except Exception:
        database_ok = False

    status_code = 200 if database_ok and models_loaded() else 503
    return jsonify({
        "status": "healthy" if status_code == 200 else "degraded",
        "database": database_ok,
        "database_status": db_status,
        "models": models_loaded()
    }), status_code

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.getenv('FLASK_DEBUG') == '1')
