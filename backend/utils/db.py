import os
import threading
from urllib.parse import urlparse

from bson import ObjectId, json_util
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ConfigurationError, PyMongoError, ServerSelectionTimeoutError

load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

MONGO_URI = os.getenv('MONGO_URI')
DB_NAME = os.getenv('MONGO_DB_NAME', 'career_compass')
DB_BACKEND = os.getenv('DB_BACKEND', 'auto').strip().lower()
LOCAL_DB_PATH = os.getenv(
    'LOCAL_DB_PATH',
    os.path.join(os.path.dirname(__file__), '../../data/local_db.json')
)

client = None
database = None
database_backend = None


def _safe_mongo_host():
    if not MONGO_URI:
        return "not configured"
    try:
        parsed = urlparse(MONGO_URI)
        return parsed.hostname or "unknown host"
    except Exception:
        return "unparseable URI"


class InsertOneResult:
    def __init__(self, inserted_id):
        self.inserted_id = inserted_id


class UpdateResult:
    def __init__(self, matched_count=0, modified_count=0, upserted_id=None):
        self.matched_count = matched_count
        self.modified_count = modified_count
        self.upserted_id = upserted_id


class DeleteResult:
    def __init__(self, deleted_count=0):
        self.deleted_count = deleted_count


class LocalCursor:
    def __init__(self, documents):
        self.documents = documents

    def sort(self, key, direction):
        self.documents.sort(key=lambda item: item.get(key), reverse=direction == -1)
        return self

    def limit(self, count):
        self.documents = self.documents[:count]
        return self

    def __iter__(self):
        return iter(self.documents)


class LocalAdmin:
    def command(self, command_name):
        if command_name == 'ping':
            return {"ok": 1}
        return {"ok": 1}


class LocalClient:
    def __init__(self, db):
        self.admin = LocalAdmin()
        self._db = db


class LocalDatabase:
    def __init__(self, path):
        self.path = os.path.abspath(path)
        self.client = LocalClient(self)
        self._lock = threading.RLock()
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        if not os.path.exists(self.path):
            self._write({})

    def __getitem__(self, collection_name):
        return LocalCollection(self, collection_name)

    def _read(self):
        with self._lock:
            if not os.path.exists(self.path):
                return {}
            with open(self.path, 'r', encoding='utf-8') as handle:
                content = handle.read().strip()
            return json_util.loads(content) if content else {}

    def _write(self, data):
        with self._lock:
            with open(self.path, 'w', encoding='utf-8') as handle:
                handle.write(json_util.dumps(data, indent=2))


class LocalCollection:
    def __init__(self, db, collection_name):
        self.db = db
        self.collection_name = collection_name

    def _normalize(self, value):
        if isinstance(value, ObjectId):
            return str(value)
        return value

    def _matches(self, document, query):
        return all(
            self._normalize(document.get(key)) == self._normalize(value)
            for key, value in (query or {}).items()
        )

    def _project(self, document, projection):
        copied = dict(document)
        if not projection:
            return copied
        if all(value == 0 for value in projection.values()):
            for key, include in projection.items():
                if include == 0:
                    copied.pop(key, None)
            return copied
        return {
            key: copied[key]
            for key, include in projection.items()
            if include and key in copied
        }

    def find_one(self, query=None, sort=None, projection=None):
        documents = list(self.find(query, projection))
        if sort:
            key, direction = sort[0]
            documents.sort(key=lambda item: item.get(key), reverse=direction == -1)
        return documents[0] if documents else None

    def insert_one(self, document):
        data = self.db._read()
        collection = data.setdefault(self.collection_name, [])
        stored = dict(document)
        stored.setdefault('_id', ObjectId())
        collection.append(stored)
        self.db._write(data)
        return InsertOneResult(stored['_id'])

    def update_one(self, query, update, upsert=False):
        data = self.db._read()
        collection = data.setdefault(self.collection_name, [])

        for index, document in enumerate(collection):
            if self._matches(document, query):
                updated = dict(document)
                updated.update(update.get('$set', {}))
                collection[index] = updated
                self.db._write(data)
                return UpdateResult(matched_count=1, modified_count=1)

        if not upsert:
            return UpdateResult()

        inserted = dict(query or {})
        inserted.update(update.get('$setOnInsert', {}))
        inserted.update(update.get('$set', {}))
        inserted.setdefault('_id', ObjectId())
        collection.append(inserted)
        self.db._write(data)
        return UpdateResult(upserted_id=inserted['_id'])

    def find(self, query=None, projection=None):
        data = self.db._read()
        documents = [
            self._project(document, projection)
            for document in data.get(self.collection_name, [])
            if self._matches(document, query)
        ]
        return LocalCursor(documents)

    def delete_one(self, query):
        return self._delete(query, one=True)

    def delete_many(self, query):
        return self._delete(query, one=False)

    def _delete(self, query, one):
        data = self.db._read()
        collection = data.setdefault(self.collection_name, [])
        deleted_count = 0
        remaining = []
        for document in collection:
            if self._matches(document, query) and (not one or deleted_count == 0):
                deleted_count += 1
            else:
                remaining.append(document)
        data[self.collection_name] = remaining
        self.db._write(data)
        return DeleteResult(deleted_count)


def _create_local_db(reason):
    global database_backend
    database_backend = "local"
    print(f"[db] WARNING: Using local JSON database at {os.path.abspath(LOCAL_DB_PATH)}. Reason: {reason}")
    return LocalDatabase(LOCAL_DB_PATH)


def ensure_mongo_indexes(db):
    try:
        db.users.create_index("email", unique=True)
        db.profiles.create_index("user_id", unique=True)
        db.predictions.create_index([("user_id", 1), ("created_at", -1)])
        db.roadmaps.create_index([("user_id", 1), ("created_at", -1)])
        db.ats_history.create_index([("user_id", 1), ("created_at", -1)])
        db.resume_analyses.create_index([("user_id", 1), ("created_at", -1)])
        print("[db] MongoDB indexes verified.")
    except PyMongoError as exc:
        print(f"[db] WARNING: Could not verify MongoDB indexes. error={type(exc).__name__}: {exc}")


def get_client():
    global client, database, database_backend
    if client is None:
        print(f"[db] DB_BACKEND={DB_BACKEND}; MONGO_URI host={_safe_mongo_host()}; DB_NAME={DB_NAME}")

        if DB_BACKEND == 'local':
            database = _create_local_db("DB_BACKEND=local")
            client = database.client
            return client

        if not MONGO_URI:
            if DB_BACKEND in ('mongo', 'mongodb', 'atlas'):
                raise ConfigurationError("MONGO_URI is required when DB_BACKEND=mongodb")
            database = _create_local_db("MONGO_URI is not configured")
            client = database.client
            return client

        try:
            client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000, connectTimeoutMS=3000)
            client.admin.command('ping')
            database = client[DB_NAME]
            database_backend = "mongodb"
            ensure_mongo_indexes(database)
            print(f"[db] Connected to MongoDB successfully. host={_safe_mongo_host()} db={DB_NAME}")
        except (PyMongoError, ServerSelectionTimeoutError, ConfigurationError, ConnectionFailure) as exc:
            print(f"[db] MongoDB connection failed. host={_safe_mongo_host()} error={type(exc).__name__}: {exc}")
            if DB_BACKEND in ('mongo', 'mongodb', 'atlas'):
                client = None
                database = None
                database_backend = "mongodb_failed"
                raise
            database = _create_local_db(str(exc))
            client = database.client
    return client


def get_db():
    global database
    if database is None:
        get_client()
    return database


def get_db_status():
    try:
        get_client()
        return {
            "backend": database_backend,
            "db_name": DB_NAME,
            "mongo_host": _safe_mongo_host(),
            "local_path": os.path.abspath(LOCAL_DB_PATH) if database_backend == "local" else None,
        }
    except Exception as exc:
        return {
            "backend": database_backend or "unavailable",
            "db_name": DB_NAME,
            "mongo_host": _safe_mongo_host(),
            "error": f"{type(exc).__name__}: {exc}",
        }


class CollectionProxy:
    def __init__(self, collection_name):
        self.collection_name = collection_name

    def _collection(self):
        return get_db()[self.collection_name]

    def __getattr__(self, item):
        return getattr(self._collection(), item)


users_collection = CollectionProxy('users')
profiles_collection = CollectionProxy('profiles')
predictions_collection = CollectionProxy('predictions')
roadmaps_collection = CollectionProxy('roadmaps')
ats_history_collection = CollectionProxy('ats_history')
resume_analyses_collection = CollectionProxy('resume_analyses')
