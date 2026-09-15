from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

SECRET_KEY = "my_super_secret_key_for_civic_system_viva"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
  # Safely encode and truncate to 72 bytes to prevent bcrypt ValueError
  encoded_password = plain_password.encode("utf-8")[:72]
  return pwd_context.verify(encoded_password, hashed_password)


def get_password_hash(password):
  # Safely encode and truncate to 72 bytes
  encoded_password = password.encode("utf-8")[:72]
  return pwd_context.hash(encoded_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
  to_encode = data.copy()
  if expires_delta:
    expire = datetime.utcnow() + expires_delta
  else:
    expire = datetime.utcnow() + timedelta(minutes=15)
  to_encode.update({"exp": expire})
  encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
  return encoded_jwt