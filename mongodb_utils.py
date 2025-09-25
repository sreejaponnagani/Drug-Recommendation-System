# mongodb_utils.py
from pymongo import MongoClient

MONGO_URI = "mongodb-url"  # replace with your URI
DB_NAME = "drug_recommender_db"
COLLECTION_NAME = "users"

def get_db_collection():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    return db[COLLECTION_NAME]
