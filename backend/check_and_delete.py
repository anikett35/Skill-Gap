from pymongo import MongoClient

# Connect to LOCAL MongoDB (the app uses localhost, not Atlas)
client = MongoClient("mongodb://localhost:27017")
db = client["skillgap_v3"]
users_col = db["users"]

# Check if user exists
user = users_col.find_one({"email": "aniketbedwal90@gmail.com"})
if user:
    print(f"✓ User found: {user['email']}")
    print(f"  Password hash: {user['password_hash'][:50]}...")
    # Delete it
    result = users_col.delete_one({"email": "aniketbedwal90@gmail.com"})
    print(f"✓ Deleted {result.deleted_count} user(s)")
    print("✓ Ready for fresh registration!")
else:
    print("✗ User not found in database")

client.close()
