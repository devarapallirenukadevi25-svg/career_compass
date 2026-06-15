import argparse
import os
from copy import deepcopy

from bson import json_util
from dotenv import load_dotenv
from pymongo import MongoClient


COLLECTIONS = ["profiles", "predictions", "roadmaps", "ats_history", "resume_analyses"]


def load_local(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as handle:
        content = handle.read().strip()
    return json_util.loads(content) if content else {}


def clean_document(document):
    cleaned = deepcopy(document)
    cleaned.pop("_id", None)
    return cleaned


def merge_profile(existing, incoming):
    merged = clean_document(existing or {})
    for key, value in clean_document(incoming).items():
        if key in ("created_at", "user_id"):
            continue
        if isinstance(value, list):
            existing_values = merged.get(key, [])
            if not isinstance(existing_values, list):
                existing_values = []
            seen = {json_util.dumps(item, sort_keys=True) for item in existing_values}
            for item in value:
                item_key = json_util.dumps(item, sort_keys=True)
                if item_key not in seen:
                    existing_values.append(item)
                    seen.add(item_key)
            merged[key] = existing_values
        elif value not in ("", None, 0, []):
            if merged.get(key) in ("", None, 0, []):
                merged[key] = value
    return merged


def main():
    parser = argparse.ArgumentParser(description="Safely migrate Career Compass local JSON data to MongoDB.")
    parser.add_argument("--local", default=os.path.join("data", "local_db.json"))
    parser.add_argument("--apply", action="store_true", help="Write changes. Without this flag the script only reports.")
    args = parser.parse_args()

    load_dotenv(".env")
    local_data = load_local(args.local)
    mongo_uri = os.getenv("MONGO_URI")
    db_name = os.getenv("MONGO_DB_NAME", "career_compass")
    if not mongo_uri:
        raise SystemExit("MONGO_URI is not configured.")

    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=12000, connectTimeoutMS=12000)
    db = client[db_name]
    client.admin.command("ping")

    local_users = local_data.get("users", [])
    print(f"Local users: {len(local_users)}")
    print(f"Mode: {'APPLY' if args.apply else 'DRY RUN'}")

    for local_user in local_users:
        email = str(local_user.get("email", "")).strip().lower()
        if not email:
            print("SKIP user without email")
            continue

        mongo_user = db.users.find_one({"email": email})
        if not mongo_user:
            print(f"CREATE user {email}")
            if args.apply:
                result = db.users.insert_one(clean_document(local_user))
                mongo_user = {**clean_document(local_user), "_id": result.inserted_id}
            else:
                continue
        else:
            local_hash = local_user.get("password_hash")
            mongo_hash = mongo_user.get("password_hash")
            if local_hash and mongo_hash and local_hash != mongo_hash:
                print(f"PASSWORD_HASH_DIFF {email}: keeping MongoDB hash")

        local_user_id = str(local_user.get("_id"))
        mongo_user_id = str(mongo_user["_id"])

        local_profile = next((item for item in local_data.get("profiles", []) if str(item.get("user_id")) == local_user_id), None)
        if local_profile:
            mongo_profile = db.profiles.find_one({"user_id": mongo_user_id})
            profile_payload = merge_profile(mongo_profile, {**local_profile, "user_id": mongo_user_id})
            profile_payload.pop("created_at", None)
            print(f"UPSERT profile {email}")
            if args.apply:
                set_on_insert = {}
                if local_profile.get("created_at") and "created_at" not in profile_payload:
                    set_on_insert["created_at"] = local_profile.get("created_at")
                update_operation = {"$set": profile_payload}
                if set_on_insert:
                    update_operation["$setOnInsert"] = set_on_insert
                db.profiles.update_one(
                    {"user_id": mongo_user_id},
                    update_operation,
                    upsert=True,
                )

        for collection_name in COLLECTIONS:
            if collection_name == "profiles":
                continue
            migrated = 0
            for document in local_data.get(collection_name, []):
                if str(document.get("user_id")) != local_user_id:
                    continue
                payload = clean_document({**document, "user_id": mongo_user_id})
                duplicate_query = {"user_id": mongo_user_id, "created_at": payload.get("created_at")}
                if payload.get("created_at") and db[collection_name].find_one(duplicate_query):
                    continue
                migrated += 1
                if args.apply:
                    db[collection_name].insert_one(payload)
            if migrated:
                print(f"INSERT {collection_name} {email}: {migrated}")

    print("Migration check complete.")


if __name__ == "__main__":
    main()
