from passlib.context import CryptContext

try:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    print(f"Hash: {pwd_context.hash('password123')}")
except Exception as e:
    print(f"Error: {e}")
