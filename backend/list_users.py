from pymongo import MongoClient

# Check local MongoDB for the user
client = MongoClient("mongodb://localhost:27017")
db = client["skillgap_v3"]
users_col = db["users"]

# List ALL users
users = list(users_col.find({}))
print(f"Total users in database: {len(users)}")
for user in users:
    print(f"\n✓ Email: {user['email']}")
    print(f"  Created: {user.get('created_at', 'N/A')}")
    print(f"  Password hash: {user['password_hash'][:50]}...")

if len(users) == 0:
    print("\n✗ No users found in database!")

client.close()
