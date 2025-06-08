from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from app.models import User, Role
from app.database import AsyncSessionLocal
from sqlalchemy.future import select
from jwt import PyJWKClient
import os

auth_scheme = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(auth_scheme),
):
    token = credentials.credentials
    jwks_url = f"https://{os.getenv('AUTH0_DOMAIN')}/.well-known/jwks.json"
    jwks_client = PyJWKClient(jwks_url)
    signing_key = jwks_client.get_signing_key_from_jwt(token)

    try:
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=os.getenv('AUTH0_AUDIENCE'),
            issuer=f"https://{os.getenv('AUTH0_DOMAIN')}/",
        )
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    auth0_id = payload.get("sub")
    if not auth0_id:
        raise HTTPException(status_code=400, detail="Missing user ID")

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).filter(User.auth0_id == auth0_id))
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

def require_role(*roles: Role):
    async def role_checker(user: User = Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return role_checker
