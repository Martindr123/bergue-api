# app/infrastructure/security/auth0_security.py

import os
import httpx
import time
from typing import Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError, jwk
from jose.utils import base64url_decode

AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN", "dev-mrtgzj2vrustiuo1.us.auth0.com")
API_AUDIENCE = os.getenv("AUTH0_AUDIENCE", "bergue-api")
ALGORITHMS = ["RS256"]

oauth2_scheme = HTTPBearer()

_JWKS_CACHE: Dict[str, Any] = {
    "keys": None,
    "fetched_at": 0
}
_JWKS_CACHE_TIMEOUT_SECONDS = 60 * 5  # 5 minutes

def _get_jwks() -> Dict[str, Any]:
    now = time.time()
    if (_JWKS_CACHE["keys"] is None) or (now - _JWKS_CACHE["fetched_at"] > _JWKS_CACHE_TIMEOUT_SECONDS):
        url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
        resp = httpx.get(url, timeout=5)
        resp.raise_for_status()
        jwks_data = resp.json()
        _JWKS_CACHE["keys"] = jwks_data["keys"]
        _JWKS_CACHE["fetched_at"] = now
    return {"keys": _JWKS_CACHE["keys"]}

def _get_public_key_from_jwks(kid: str):
    jwks = _get_jwks()["keys"]
    for key in jwks:
        if key["kid"] == kid:
            n = base64url_decode(key["n"])
            e = base64url_decode(key["e"])
            return jwk.construct(dict(kty=key["kty"], n=n, e=e))
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token: unknown kid")

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    token = credentials.credentials
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token manquant",
        )
    try:
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        if not kid:
            raise HTTPException(status_code=401, detail="Missing kid in token header")

        public_key = _get_public_key_from_jwks(kid)

        payload = jwt.decode(
            token,
            public_key,
            algorithms=ALGORITHMS,
            audience=API_AUDIENCE,
            issuer=f"https://{AUTH0_DOMAIN}/"
        )

        return payload

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token invalide: {str(e)}"
        ) from e
