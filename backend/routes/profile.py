import os
import traceback
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import datetime
from utils.db import ats_history_collection, predictions_collection, profiles_collection, resume_analyses_collection
from pymongo.errors import PyMongoError
from services.domain_catalog import DOMAINS, get_domains_payload, get_option_catalog
from services.resume_parser import parse_resume
from services.career_insights import calculate_ats
from services.predict_service import make_prediction

profile_bp = Blueprint('profile', __name__)

STRING_ARRAY_FIELDS = [
    "skills",
    "programming_languages",
    "frameworks",
    "tools",
    "databases",
    "platforms",
    "technologies",
    "soft_skills",
    "education",
]

STRUCTURED_ARRAY_FIELDS = {
    "certifications",
    "achievements",
    "hackathons",
}

STRUCTURED_FIELD_DEFS = {
    "certifications": {
        "display_key": "name",
        "allowed_keys": ("name", "issuer", "year"),
    },
    "achievements": {
        "display_key": "title",
        "allowed_keys": ("title", "description", "year"),
    },
    "hackathons": {
        "display_key": "name",
        "allowed_keys": ("name", "position", "year"),
    },
}

TEXT_FIELDS = [
    "degree",
    "branch",
    "project_complexity",
    "interested_domain",
    "github_profile",
    "linkedin_profile",
    "resume_url",
    "resume_text",
]


def normalize_array(value):
    if value is None:
        return []
    if isinstance(value, str):
        value = [item.strip() for item in value.split(',')]
    if not isinstance(value, list):
        return []

    normalized = []
    seen = set()
    for item in value:
        cleaned = str(item).strip()
        key = cleaned.lower()
        if cleaned and key not in seen:
            normalized.append(cleaned)
            seen.add(key)
    return normalized


def log_exception(context, exc):
    print(f"[profile] {context} error={type(exc).__name__}: {exc}")
    traceback.print_exc()


def error_response(message, exc=None, status=503):
    payload = {"error": message}
    if exc is not None:
        payload["details"] = f"{type(exc).__name__}: {exc}"
    return jsonify(payload), status


def merge_unique(existing, incoming):
    return normalize_array([*(existing or []), *(incoming or [])])


def merge_structured(existing, incoming, field_name):
    return normalize_structured_entries([*(existing or []), *(incoming or [])], field_name)


def normalize_year(value):
    if value is None:
        return ""
    text = str(value).strip()
    if not text:
        return ""
    return int(text) if text.isdigit() else text


def normalize_structured_entries(value, field_name):
    if value is None:
        return []
    if isinstance(value, dict):
        value = [value]
    elif isinstance(value, str):
        value = [value]
    if not isinstance(value, list):
        return []

    field_def = STRUCTURED_FIELD_DEFS[field_name]
    display_key = field_def["display_key"]
    allowed_keys = field_def["allowed_keys"]

    normalized = []
    seen = set()
    for item in value:
        if isinstance(item, dict):
            cleaned = {}
            for key in allowed_keys:
                raw = item.get(key, "")
                if key == "year":
                    normalized_year = normalize_year(raw)
                    if normalized_year != "":
                        cleaned[key] = normalized_year
                else:
                    text = str(raw).strip()
                    if text:
                        cleaned[key] = text
        else:
            text = str(item).strip()
            cleaned = {display_key: text} if text else {}

        if not cleaned or not cleaned.get(display_key):
            continue

        dedupe_key = tuple(str(cleaned.get(key, "")).lower() for key in allowed_keys)
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        normalized.append(cleaned)

    return normalized


def build_category_lookup():
    catalog = get_option_catalog()
    lookup = {}
    for field, options in catalog.items():
        for option in options:
            lookup.setdefault(option.lower(), field)
    return catalog, lookup


def canonicalize_profile_arrays(profile_data):
    catalog, lookup = build_category_lookup()
    corrected = {field: [] for field in STRING_ARRAY_FIELDS}

    for field in STRING_ARRAY_FIELDS:
        for value in normalize_array(profile_data.get(field)):
            target_field = lookup.get(value.lower(), field)
            if target_field in corrected:
                corrected[target_field].append(value)

    for field in STRING_ARRAY_FIELDS:
        allowed = {item.lower(): item for item in catalog.get(field, [])}
        kept = []
        for value in normalize_array(corrected.get(field)):
            canonical = allowed.get(value.lower(), value)
            if canonical not in kept:
                kept.append(canonical)
        profile_data[field] = normalize_array(kept)

    for field in STRUCTURED_ARRAY_FIELDS:
        profile_data[field] = normalize_structured_entries(profile_data.get(field), field)

    return profile_data


def persist_ats_snapshot(user_id, profile_data, now):
    ats_result = calculate_ats(profile_data)
    ats_history_collection.insert_one({
        "user_id": user_id,
        **ats_result,
        "created_at": now,
    })
    return ats_result


def persist_prediction_snapshot(user_id, profile_data, now):
    prediction = make_prediction(profile=profile_data)
    predictions_collection.insert_one({
        "user_id": user_id,
        **prediction,
        "created_at": now,
    })
    return prediction


def serialize_profile_payload(profile_data, user_id=None):
    payload = dict(profile_data or {})
    payload.pop("_id", None)
    if user_id is not None:
        payload["user_id"] = user_id
    return payload


def parse_profile_payload(data, existing_profile=None):
    existing_profile = existing_profile or {}
    required_fields = ['cgpa', 'leetcode', 'projects', 'internships']
    communication_value = data.get('communication', data.get('communication_score'))
    missing_fields = [field for field in required_fields if field not in data]
    if communication_value is None:
        missing_fields.append('communication')
    if missing_fields:
        return None, f"Missing required fields: {', '.join(missing_fields)}"

    try:
        profile_data = {
            "cgpa": float(data['cgpa']),
            "leetcode": int(data['leetcode']),
            "projects": int(data['projects']),
            "internships": int(data['internships']),
            "communication": int(communication_value),
        }
    except (TypeError, ValueError):
        return None, "Profile fields must contain valid numeric values"

    if not 0 <= profile_data["cgpa"] <= 10:
        return None, "CGPA must be between 0 and 10"
    if profile_data["leetcode"] < 0 or profile_data["projects"] < 0 or profile_data["internships"] < 0:
        return None, "LeetCode, projects, and internships cannot be negative"
    if not 1 <= profile_data["communication"] <= 10:
        return None, "Communication score must be between 1 and 10"
    interested_domain = str(data.get("interested_domain", existing_profile.get("interested_domain", "")) or "").strip()
    if interested_domain and interested_domain not in DOMAINS:
        return None, "Selected domain is not supported"

    profile_data["communication_score"] = profile_data["communication"]
    profile_data["interested_domain"] = interested_domain

    for field in ("codechef_rating", "codeforces_rating", "github_activity"):
        try:
            profile_data[field] = int(data.get(field, existing_profile.get(field, 0)) or 0)
        except (TypeError, ValueError):
            return None, f"{field} must contain a valid number"
        if profile_data[field] < 0:
            return None, f"{field} cannot be negative"

    for field in STRING_ARRAY_FIELDS:
        source = data[field] if field in data else existing_profile.get(field, [])
        profile_data[field] = normalize_array(source)

    for field in STRUCTURED_ARRAY_FIELDS:
        source = data[field] if field in data else existing_profile.get(field, [])
        profile_data[field] = normalize_structured_entries(source, field)

    for field in TEXT_FIELDS:
        if field != "interested_domain":
            source = data[field] if field in data else existing_profile.get(field, "")
            profile_data[field] = str(source or "").strip()

    try:
        profile_data["ats_score"] = int(existing_profile.get("ats_score", 0) or 0)
    except (TypeError, ValueError):
        profile_data["ats_score"] = 0

    return canonicalize_profile_arrays(profile_data), None


def build_profile_update(existing_profile, parsed_profile, user_id, now):
    profile_data = canonicalize_profile_arrays({
        **existing_profile,
        "user_id": user_id,
        **parsed_profile,
        "updated_at": now,
    })
    for immutable_field in ("_id", "created_at", "user_id"):
        profile_data.pop(immutable_field, None)
    return profile_data


@profile_bp.route('/domains', methods=['GET'])
@jwt_required()
def get_domains():
    return jsonify({"domains": get_domains_payload(), "options": get_option_catalog()}), 200

@profile_bp.route('/', methods=['POST'])
@jwt_required()
def create_or_update_profile():
    current_user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    print(f"[profile] save request user_id={current_user_id} keys={sorted(data.keys())}")
    print(f"[profile] save payload user_id={current_user_id} arrays={{k: len(v) if isinstance(v, list) else 0 for k, v in data.items() if isinstance(v, list)}}")

    try:
        existing_profile = profiles_collection.find_one({"user_id": current_user_id}) or {}
    except PyMongoError as exc:
        log_exception(f"existing lookup failed user_id={current_user_id}", exc)
        return error_response("Could not load existing profile. Please try again.", exc)

    parsed_profile, error = parse_profile_payload(data, existing_profile)
    if error:
        print(f"[profile] validation failed user_id={current_user_id} error={error}")
        return jsonify({"error": error}), 400

    now = datetime.datetime.utcnow()
    profile_data = build_profile_update(existing_profile, parsed_profile, current_user_id, now)

    try:
        result = profiles_collection.update_one(
            {"user_id": current_user_id},
            {"$set": profile_data, "$setOnInsert": {"created_at": now}},
            upsert=True
        )
        print(f"[profile] mongo write user_id={current_user_id} matched={getattr(result, 'matched_count', None)} upserted={getattr(result, 'upserted_id', None)}")
        try:
            prediction = persist_prediction_snapshot(current_user_id, profile_data, now)
            print(f"[profile] prediction refreshed user_id={current_user_id} probability={prediction['placement_probability']}")
        except PyMongoError as exc:
            log_exception(f"prediction refresh failed user_id={current_user_id}", exc)
    except PyMongoError as exc:
        log_exception(f"save failed user_id={current_user_id}", exc)
        return error_response("Could not save profile. Please try again.", exc)

    status_code = 201 if result.upserted_id else 200
    message = "Profile created successfully" if result.upserted_id else "Profile updated successfully"
    return jsonify({
        "message": message,
        "profile": serialize_profile_payload(profile_data, current_user_id),
        "prediction": prediction if "prediction" in locals() else make_prediction(profile=profile_data),
    }), status_code

@profile_bp.route('/', methods=['GET'])
@jwt_required()
def get_profile():
    current_user_id = get_jwt_identity()
    print(f"[profile] fetch user_id={current_user_id}")
    try:
        profile = profiles_collection.find_one({"user_id": current_user_id})
    except PyMongoError as exc:
        log_exception(f"fetch failed user_id={current_user_id}", exc)
        return error_response("Could not load profile. Please try again.", exc)
    
    if not profile:
        print(f"[profile] fetch missing user_id={current_user_id}")
        return jsonify({"error": "Profile not found"}), 404
        
    profile = canonicalize_profile_arrays(profile)
    profile['_id'] = str(profile['_id'])
    profile.setdefault("communication_score", profile.get("communication"))
    for field in STRING_ARRAY_FIELDS:
        profile.setdefault(field, [])
    for field in STRUCTURED_ARRAY_FIELDS:
        profile.setdefault(field, [])
    for field in TEXT_FIELDS:
        profile.setdefault(field, "")
    for field in ("codechef_rating", "codeforces_rating", "github_activity"):
        profile.setdefault(field, 0)
    profile.setdefault("ats_score", 0)
    return jsonify(profile), 200


@profile_bp.route('/resume', methods=['POST'])
@jwt_required()
def upload_resume():
    current_user_id = get_jwt_identity()
    uploaded_file = request.files.get('resume')

    if not uploaded_file or uploaded_file.filename == '':
        return jsonify({"error": "PDF resume file is required"}), 400
    if not uploaded_file.filename.lower().endswith('.pdf'):
        return jsonify({"error": "Only PDF resumes are supported"}), 400

    try:
        extracted = parse_resume(uploaded_file)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    now = datetime.datetime.utcnow()
    upload_dir = os.path.join(current_app.root_path, "uploads", "resumes")
    os.makedirs(upload_dir, exist_ok=True)
    filename = f"{current_user_id}.pdf"
    file_path = os.path.join(upload_dir, filename)
    uploaded_file.stream.seek(0)
    uploaded_file.save(file_path)
    resume_url = f"/uploads/resumes/{filename}"

    try:
        existing = profiles_collection.find_one({"user_id": current_user_id}) or {}
        update_data = {
            "resume_url": resume_url,
            "resume_text": extracted["resume_text"],
            "resume_analysis": extracted["analysis"],
            "updated_at": now,
            "skills": merge_unique(existing.get("skills"), extracted["skills"]),
            "programming_languages": merge_unique(existing.get("programming_languages"), extracted["programming_languages"]),
            "frameworks": merge_unique(existing.get("frameworks"), extracted["frameworks"]),
            "tools": merge_unique(existing.get("tools"), extracted["tools"]),
            "databases": merge_unique(existing.get("databases"), extracted.get("databases", [])),
            "platforms": merge_unique(existing.get("platforms"), extracted.get("platforms", [])),
            "technologies": merge_unique(existing.get("technologies"), extracted.get("technologies", [])),
            "education": merge_unique(existing.get("education"), extracted.get("education", [])),
            "certifications": merge_structured(existing.get("certifications"), extracted["certifications"], "certifications"),
            "achievements": merge_structured(existing.get("achievements"), extracted["achievements"], "achievements"),
        }
        update_data = canonicalize_profile_arrays({**existing, **update_data})
        for immutable_field in ("_id", "created_at", "user_id"):
            update_data.pop(immutable_field, None)

        if extracted["projects"] > 0:
            update_data["projects"] = max(int(existing.get("projects", 0) or 0), extracted["projects"])
        if extracted["internships"] > 0:
            update_data["internships"] = max(int(existing.get("internships", 0) or 0), extracted["internships"])

        insert_defaults = {
            "user_id": current_user_id,
            "cgpa": 0,
            "leetcode": 0,
            "communication": 1,
            "communication_score": 1,
            "interested_domain": "",
            "achievements": [],
            "hackathons": [],
            "databases": [],
            "platforms": [],
            "technologies": [],
            "soft_skills": [],
            "education": [],
            "github_profile": "",
            "linkedin_profile": "",
            "created_at": now,
        }
        if "projects" not in update_data:
            insert_defaults["projects"] = 0
        if "internships" not in update_data:
            insert_defaults["internships"] = 0

        merged_profile = {**insert_defaults, **existing, **update_data}
        ats_result = persist_ats_snapshot(current_user_id, merged_profile, now)
        update_data["ats_score"] = ats_result["ats_score"]
        set_on_insert = {
            key: value
            for key, value in insert_defaults.items()
            if key not in update_data
        }

        update_operation = {"$set": update_data}
        if set_on_insert:
            update_operation["$setOnInsert"] = set_on_insert

        profiles_collection.update_one(
            {"user_id": current_user_id},
            update_operation,
            upsert=True,
        )
        try:
            prediction = persist_prediction_snapshot(current_user_id, {**merged_profile, **update_data}, now)
            print(f"[profile] resume prediction refreshed user_id={current_user_id} probability={prediction['placement_probability']}")
        except PyMongoError as exc:
            log_exception(f"resume prediction refresh failed user_id={current_user_id}", exc)
        resume_analyses_collection.insert_one({
            "user_id": current_user_id,
            "resume_url": resume_url,
            "extracted": {key: value for key, value in extracted.items() if key != "resume_text"},
            "ats_score": ats_result["ats_score"],
            "created_at": now,
        })
    except PyMongoError as exc:
        log_exception(f"resume save failed user_id={current_user_id}", exc)
        return error_response("Could not save resume analysis. Please try again.", exc)

    return jsonify({
        "message": "Resume analyzed successfully",
        "resume_url": resume_url,
        "extracted": {key: value for key, value in extracted.items() if key != "resume_text"},
        "profile": serialize_profile_payload({**merged_profile, **update_data}, current_user_id),
        "prediction": prediction if "prediction" in locals() else make_prediction(profile={**merged_profile, **update_data}),
    }), 200
