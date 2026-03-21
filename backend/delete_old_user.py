from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")

client = MongoClient(MONGO_URL)
db = client["skillgap_v3"]
users_col = db["users"]

result = users_col.delete_one({"email": "aniketbedwal90@gmail.com"})
print(f"✓ Deleted {result.deleted_count} user(s)")
print("✓ You can now register a new account with the fixed code")
client.close()
