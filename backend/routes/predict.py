from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import datetime
from utils.db import profiles_collection, predictions_collection
from services.predict_service import make_prediction
from pymongo.errors import PyMongoError

predict_bp = Blueprint('predict', __name__)


def error_response(message, exc=None, status=503):
    payload = {"error": message}
    if exc is not None:
        payload["details"] = f"{type(exc).__name__}: {exc}"
    return jsonify(payload), status


def build_prediction_record(user_id, results, created_at=None):
    return {
        "user_id": user_id,
        "placement_probability": results["placement_probability"],
        "salary_prediction": results["salary_prediction"],
        "student_cluster": results["student_cluster"],
        "svm_prediction": results["svm_prediction"],
        "cluster_id": results["cluster_id"],
        "readiness_score": results["readiness_score"],
        "skill_match": results["skill_match"],
        "resume_strength": results["resume_strength"],
        "confidence_score": results["confidence_score"],
        "matched_skills": results["matched_skills"],
        "missing_skills": results["missing_skills"],
        "recommendations": results["recommendations"],
        "component_scores": results["component_scores"],
        "weights": results["weights"],
        "created_at": created_at or datetime.datetime.utcnow()
    }


def load_current_profile(user_id):
    try:
        profile = profiles_collection.find_one({"user_id": user_id})
    except PyMongoError as exc:
        print(f"[predict] profile lookup failed user_id={user_id} error={type(exc).__name__}: {exc}")
        return None, error_response("Could not load profile. Please try again.", exc)

    if not profile:
        return None, (jsonify({"error": "Profile not found. Please complete your profile first."}), 404)

    return profile, None


@predict_bp.route('/current', methods=['GET'])
@jwt_required()
def get_current_prediction():
    current_user_id = get_jwt_identity()
    profile, error = load_current_profile(current_user_id)
    if error:
        return error

    try:
        return jsonify(make_prediction(profile=profile)), 200
    except Exception as exc:
        print(f"[predict] current generation failed user_id={current_user_id} error={type(exc).__name__}: {exc}")
        return error_response("Prediction generation failed.", exc, 500)

@predict_bp.route('/', methods=['POST'])
@jwt_required()
def generate_prediction():
    current_user_id = get_jwt_identity()
    profile, error = load_current_profile(current_user_id)
    if error:
        return error

    try:
        results = make_prediction(profile=profile)
        prediction_record = build_prediction_record(current_user_id, results)
        
        result = predictions_collection.insert_one(prediction_record)
        print(f"[predict] prediction saved user_id={current_user_id} prediction_id={result.inserted_id}")
        
        return jsonify(results), 200
    except Exception as e:
        print(f"[predict] generation failed user_id={current_user_id} error={type(e).__name__}: {e}")
        return error_response("Prediction generation failed.", e, 500)

@predict_bp.route('/history', methods=['GET'])
@jwt_required()
def get_prediction_history():
    current_user_id = get_jwt_identity()
    
    try:
        predictions = list(predictions_collection.find(
            {"user_id": current_user_id},
            {"_id": 0}
        ).sort("created_at", -1))
    except PyMongoError as exc:
        print(f"[predict] history lookup failed user_id={current_user_id} error={type(exc).__name__}: {exc}")
        return error_response("Could not load prediction history. Please try again.", exc)
    
    return jsonify(predictions), 200
