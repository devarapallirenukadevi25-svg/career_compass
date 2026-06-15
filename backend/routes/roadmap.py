from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import datetime
from utils.db import profiles_collection, predictions_collection, roadmaps_collection
from services.groq_service import generate_roadmap
from services.career_insights import analyze_skill_gap, calculate_ats, recommend_roles
from pymongo.errors import PyMongoError

roadmap_bp = Blueprint('roadmap', __name__)


def error_response(message, exc=None, status=503):
    payload = {"error": message}
    if exc is not None:
        payload["details"] = f"{type(exc).__name__}: {exc}"
    return jsonify(payload), status

@roadmap_bp.route('/', methods=['POST'])
@jwt_required()
def create_roadmap():
    current_user_id = get_jwt_identity()
    
    # Get user profile
    try:
        profile = profiles_collection.find_one({"user_id": current_user_id})
    except PyMongoError as exc:
        print(f"[roadmap] profile lookup failed user_id={current_user_id} error={type(exc).__name__}: {exc}")
        return error_response("Could not load profile. Please try again.", exc)

    if not profile:
        return jsonify({"error": "Profile not found. Please complete your profile first."}), 404
        
    # Get latest prediction
    try:
        prediction = predictions_collection.find_one(
            {"user_id": current_user_id},
            sort=[("created_at", -1)]
        )
    except PyMongoError as exc:
        print(f"[roadmap] prediction lookup failed user_id={current_user_id} error={type(exc).__name__}: {exc}")
        return error_response("Could not load prediction. Please try again.", exc)

    if not prediction:
        return jsonify({"error": "No predictions found. Please generate a prediction first."}), 404

    try:
        ats_result = calculate_ats(profile)
        roles = recommend_roles({**profile, "ats_score": ats_result["ats_score"]})
        target_role = roles[0]["role_name"] if roles else None
        skill_gap = analyze_skill_gap(profile, target_role)

        # Generate roadmap
        result = generate_roadmap(profile, prediction, ats_result, skill_gap)
        
        if "error" in result:
            return jsonify(result), 500
            
        # Save roadmap to DB
        roadmap_record = {
            "user_id": current_user_id,
            "roadmap_text": result["roadmap_text"],
            "target_role": skill_gap.get("target_role"),
            "ats_score": ats_result["ats_score"],
            "created_at": datetime.datetime.utcnow()
        }
        
        try:
            roadmaps_collection.insert_one(roadmap_record)
        except PyMongoError as exc:
            print(f"[roadmap] save failed user_id={current_user_id} error={type(exc).__name__}: {exc}")
            return error_response("Could not save roadmap. Please try again.", exc)
        
        return jsonify({"roadmap_text": result["roadmap_text"]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@roadmap_bp.route('/latest', methods=['GET'])
@jwt_required()
def get_latest_roadmap():
    current_user_id = get_jwt_identity()
    
    try:
        roadmap = roadmaps_collection.find_one(
            {"user_id": current_user_id},
            sort=[("created_at", -1)],
            projection={"_id": 0}
        )
    except PyMongoError as exc:
        print(f"[roadmap] latest lookup failed user_id={current_user_id} error={type(exc).__name__}: {exc}")
        return error_response("Could not load roadmap. Please try again.", exc)
    
    if not roadmap:
        return jsonify({"error": "No roadmap found"}), 404
        
    return jsonify(roadmap), 200
