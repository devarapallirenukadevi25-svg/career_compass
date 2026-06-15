import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from pymongo.errors import PyMongoError

from services.career_insights import (
    ROLE_REQUIREMENTS,
    analyze_skill_gap,
    build_resume_summary,
    calculate_ats,
    calculate_domain_match,
    recommend_roles,
)
from utils.db import ats_history_collection, profiles_collection

insights_bp = Blueprint("insights", __name__)


def error_response(message, exc=None, status=503):
    payload = {"error": message}
    if exc is not None:
        payload["details"] = f"{type(exc).__name__}: {exc}"
    return jsonify(payload), status


def _load_profile(user_id):
    profile = profiles_collection.find_one({"user_id": user_id})
    if not profile:
        return None
    profile["_id"] = str(profile["_id"])
    return profile


def _save_ats_result(user_id, ats_result):
    now = datetime.datetime.utcnow()
    profiles_collection.update_one(
        {"user_id": user_id},
        {"$set": {"ats_score": ats_result["ats_score"], "updated_at": now}},
    )
    ats_history_collection.insert_one({
        "user_id": user_id,
        **ats_result,
        "created_at": now,
    })


@insights_bp.route("/roles", methods=["GET"])
@jwt_required()
def get_roles():
    return jsonify({"roles": list(ROLE_REQUIREMENTS.keys())}), 200


@insights_bp.route("/ats", methods=["GET", "POST"])
@jwt_required()
def get_ats_score():
    current_user_id = get_jwt_identity()
    try:
        profile = _load_profile(current_user_id)
        if not profile:
            return jsonify({"error": "Profile not found. Please complete your profile first."}), 404

        ats_result = calculate_ats(profile)
        _save_ats_result(current_user_id, ats_result)
        return jsonify(ats_result), 200
    except PyMongoError as exc:
        print(f"[insights] ats failed user_id={current_user_id} error={type(exc).__name__}: {exc}")
        return error_response("Could not calculate ATS score. Please try again.", exc)


@insights_bp.route("/ats/history", methods=["GET"])
@jwt_required()
def get_ats_history():
    current_user_id = get_jwt_identity()
    try:
        history = list(ats_history_collection.find(
            {"user_id": current_user_id},
            {"_id": 0},
        ).sort("created_at", -1).limit(20))
    except PyMongoError as exc:
        print(f"[insights] ats history failed user_id={current_user_id} error={type(exc).__name__}: {exc}")
        return error_response("Could not load ATS history. Please try again.", exc)

    return jsonify(history), 200


@insights_bp.route("/skill-gap", methods=["GET", "POST"])
@jwt_required()
def get_skill_gap():
    current_user_id = get_jwt_identity()
    payload = request.get_json(silent=True) or {}
    target_role = payload.get("target_role") or request.args.get("target_role")

    try:
        profile = _load_profile(current_user_id)
    except PyMongoError as exc:
        print(f"[insights] skill gap profile lookup failed user_id={current_user_id} error={type(exc).__name__}: {exc}")
        return error_response("Could not load profile. Please try again.", exc)

    if not profile:
        return jsonify({"error": "Profile not found. Please complete your profile first."}), 404

    return jsonify(analyze_skill_gap(profile, target_role)), 200


@insights_bp.route("/role-recommendations", methods=["GET"])
@jwt_required()
def get_role_recommendations():
    current_user_id = get_jwt_identity()
    try:
        profile = _load_profile(current_user_id)
    except PyMongoError as exc:
        print(f"[insights] recommendations profile lookup failed user_id={current_user_id} error={type(exc).__name__}: {exc}")
        return error_response("Could not load profile. Please try again.", exc)

    if not profile:
        return jsonify({"error": "Profile not found. Please complete your profile first."}), 404

    return jsonify({"recommendations": recommend_roles(profile)}), 200


@insights_bp.route("/domain-match", methods=["GET"])
@jwt_required()
def get_domain_match():
    current_user_id = get_jwt_identity()
    try:
        profile = _load_profile(current_user_id)
    except PyMongoError as exc:
        print(f"[insights] domain match profile lookup failed user_id={current_user_id} error={type(exc).__name__}: {exc}")
        return error_response("Could not load profile. Please try again.", exc)

    if not profile:
        return jsonify({"error": "Profile not found. Please complete your profile first."}), 404

    return jsonify(calculate_domain_match(profile)), 200


@insights_bp.route("/summary", methods=["GET"])
@jwt_required()
def get_insight_summary():
    current_user_id = get_jwt_identity()
    target_role = request.args.get("target_role")

    try:
        profile = _load_profile(current_user_id)
        if not profile:
            return jsonify({"error": "Profile not found. Please complete your profile first."}), 404

        ats_result = calculate_ats(profile)
        _save_ats_result(current_user_id, ats_result)
        profile["ats_score"] = ats_result["ats_score"]
        roles = recommend_roles(profile)
        selected_role = target_role or (roles[0]["role_name"] if roles else None)

        return jsonify({
            "ats": ats_result,
            "skill_gap": analyze_skill_gap(profile, selected_role),
            "role_recommendations": roles,
            "domain_match": calculate_domain_match(profile),
            "resume_summary": build_resume_summary(profile),
        }), 200
    except PyMongoError as exc:
        print(f"[insights] summary failed user_id={current_user_id} error={type(exc).__name__}: {exc}")
        return error_response("Could not load career insights. Please try again.", exc)
