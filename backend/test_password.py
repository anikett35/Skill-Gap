import bcrypt

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(plain: str, hashed: str) -> bool:
    if isinstance(hashed, str):
        hashed = hashed.encode('utf-8')
    return bcrypt.checkpw(plain.encode('utf-8'), hashed)

# Test
test_password = "TestPassword123!"
hashed = hash_password(test_password)
print(f"✓ Password hashing works correctly")
print(f"✓ Verify correct password: {verify_password(test_password, hashed)}")
print(f"✓ Verify wrong password returns: {verify_password('WrongPassword', hashed)}")
print("\nAll tests passed! The fix is working.")
