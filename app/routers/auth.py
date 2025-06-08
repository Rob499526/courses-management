import os
from fastapi import APIRouter, HTTPException
from app.models import User
from app.database import AsyncSessionLocal
import jwt
from jwt import PyJWKClient
from sqlalchemy import select
import httpx

router = APIRouter()

@router.get("/login")
async def login():
    return {
        "url": f"https://{os.getenv('AUTH0_DOMAIN')}/authorize"
        f"?response_type=code"
        f"&client_id={os.getenv('AUTH0_CLIENT_ID')}"
        f"&redirect_uri={os.getenv('AUTH0_REDIRECT_URL')}"
        f"&audience={os.getenv('AUTH0_AUDIENCE')}"
        f"&scope=openid%20profile%20email"
    }

@router.get("/callback")
async def callback(code: str):
    token_url = f"https://{os.getenv('AUTH0_DOMAIN')}/oauth/token"
    client_id = os.getenv('AUTH0_CLIENT_ID')
    client_secret = os.getenv('AUTH0_CLIENT_SECRET')
    redirect_uri = os.getenv('AUTH0_REDIRECT_URL')

    async with httpx.AsyncClient() as client:
        response = await client.post(
            token_url,
            data={
                "grant_type": "authorization_code",
                "client_id": client_id,
                "client_secret": client_secret,
                "code": code,
                "redirect_uri": redirect_uri,
            },
        )

    if response.status_code != 200:
        print("Token exchange failed:", response.text)
        raise HTTPException(status_code=response.status_code, detail="Token exchange failed")

    tokens = response.json()
    id_token = tokens.get("id_token")

    if not id_token:
        raise HTTPException(status_code=400, detail="Missing id_token")

    jwks_url = f"https://{os.getenv('AUTH0_DOMAIN')}/.well-known/jwks.json"
    jwks_client = PyJWKClient(jwks_url)
    signing_key = jwks_client.get_signing_key_from_jwt(id_token)

    decoded = jwt.decode(
        id_token,
        signing_key.key,
        algorithms=["RS256"],
        audience=os.getenv('AUTH0_CLIENT_ID'),
        issuer=f"https://{os.getenv('AUTH0_DOMAIN')}/",
    )

    auth0_id = decoded.get("sub")
    email = decoded.get("email")
    name = decoded.get("name")

    # Use DB to check or create user
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).filter(User.auth0_id == auth0_id))
        existing_user = result.scalars().first()

        if not existing_user:
            new_user = User(auth0_id=auth0_id, email=email, username=name)
            db.add(new_user)
            await db.commit()

        return {
            "access_token": tokens["access_token"],
            "token_type": "bearer",
            "id_token": id_token,
            "user_info": {"email": email, "name": name}
        }