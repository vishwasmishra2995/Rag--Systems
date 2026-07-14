from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
load_dotenv()

import os
SECRET_KEY = os.getenv("key")
if not SECRET_KEY:
    raise RuntimeError("JWT SECRET_KEY not set")
ALGORITHM = "HS256"
EXPIRE_DAYS = 4

def create_scope_token(scope_id: str):
    payload = {
        "scope_id": scope_id,
        "exp": datetime.now(timezone.utc) + timedelta(days=EXPIRE_DAYS)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def decode_scope_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["scope_id"]
    except JWTError:
        return None
    
