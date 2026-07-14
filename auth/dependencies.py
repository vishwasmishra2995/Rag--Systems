from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from auth.jwtutils import decode_scope_token

security = HTTPBearer()

def get_scope_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    scope_id = decode_scope_token(token)

    if not scope_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    return scope_id