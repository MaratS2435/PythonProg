from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext

from .config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES


def create_tokens(email: str, role: str):
    access_token = jwt.encode(
        {'role': role, 'email': email, 'exp': datetime.utcnow() + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))},
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    refresh_token = jwt.encode(
        {'role': role, 'email': email, 'exp': datetime.utcnow() + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))},
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return access_token, refresh_token