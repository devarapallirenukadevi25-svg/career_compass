from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import datetime
from utils.db import users_collection
from bson.objectid import ObjectId
from bson.errors import InvalidId
from pymongo.errors import PyMongoError

auth_bp = Blueprint('auth', __name__)


def error_response(message, exc=None, status=503):
    payload = {"error": message}
    if exc is not None:
        payload["details"] = f"{type(exc).__name__}: {exc}"
    return jsonify(payload), status

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json(silent=True) or {}
    name = str(data.get('name', '')).strip()
    email = str(data.get('email', '')).strip().lower()
    password = data.get('password')

    if not name or not email or not password:
        return jsonify({"error": "Name, email, and password are required"}), 400
    if len(str(password)) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    try:
        if users_collection.find_one({"email": email}):
            print(f"[auth] register duplicate email={email}")
            return jsonify({"error": "User with this email already exists"}), 409

        password_hash = generate_password_hash(str(password))
        now = datetime.datetime.utcnow()

        new_user = {
            "name": name,
            "email": email,
            "password_hash": password_hash,
            "created_at": now,
            "updated_at": now
        }

        result = users_collection.insert_one(new_user)
        print(f"[auth] registered user_id={result.inserted_id} email={email}")

        return jsonify({
            "message": "User registered successfully",
            "user": {
                "id": str(result.inserted_id),
                "name": name,
                "email": email
            }
        }), 201
    except PyMongoError as exc:
        print(f"[auth] register database error={type(exc).__name__}: {exc}")
        return error_response("Could not register user. Please try again.", exc)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    email = str(data.get('email', '')).strip().lower()
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    try:
        user = users_collection.find_one({"email": email})
    except PyMongoError as exc:
        print(f"[auth] login database error={type(exc).__name__}: {exc}")
        return error_response("Could not connect to the database. Please try again.", exc)

    if not user or not check_password_hash(user.get('password_hash', ''), str(password)):
        print(f"[auth] login failed email={email} user_found={bool(user)}")
        return jsonify({"error": "Invalid email or password"}), 401

    access_token = create_access_token(identity=str(user['_id']), expires_delta=datetime.timedelta(days=1))
    print(f"[auth] login success user_id={user['_id']} email={email}")
    
    return jsonify({
        "message": "Login successful",
        "token": access_token,
        "user": {
            "id": str(user['_id']),
            "name": user['name'],
            "email": user['email']
        }
    }), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    current_user_id = get_jwt_identity()
    print(f"[auth] /me lookup user_id={current_user_id}")
    try:
        user = users_collection.find_one({"_id": ObjectId(current_user_id)})
    except InvalidId:
        print(f"[auth] /me invalid user_id={current_user_id}")
        return jsonify({"error": "User not found"}), 404
    except PyMongoError as exc:
        print(f"[auth] /me database error user_id={current_user_id} error={type(exc).__name__}: {exc}")
        return error_response("User not found", exc, 404)
    
    if not user:
        print(f"[auth] /me user not found user_id={current_user_id}")
        return jsonify({"error": "User not found"}), 404
    print(f"[auth] /me success user_id={current_user_id} email={user.get('email')}")
        
    return jsonify({
        "user": {
            "id": str(user['_id']),
            "name": user['name'],
            "email": user['email']
        }
    }), 200
