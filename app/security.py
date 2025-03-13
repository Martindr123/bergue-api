# app/security.py

import os
import httpx
from typing import Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError, jwk
from jose.utils import base64url_decode
import time

AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN", "dev-mrtgzj2vrustiuo1.us.auth0.com")
API_AUDIENCE = os.getenv("AUTH0_AUDIENCE", "bergue-api")
ALGORITHMS = ["RS256"]

oauth2_scheme = HTTPBearer()

# Petit cache en mémoire pour éviter de re-télécharger le JWKS
_JWKS_CACHE: Dict[str, Any] = {
    "keys": None,
    "fetched_at": 0
}
_JWKS_CACHE_TIMEOUT_SECONDS = 60 * 5  # 5 minutes

def _get_jwks() -> Dict[str, Any]:
    """
    Récupère et met en cache la JWKS depuis Auth0.
    """
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
    """
    À partir du kid, renvoie la clé publique RSA utilisable par python-jose.
    """
    jwks = _get_jwks()["keys"]  # liste de clés
    for key in jwks:
        if key["kid"] == kid:
            # Soit on reconstruit un dict "public_key" à partir de n/e
            # Soit on exploite la lib jose jwk.construct().
            # Voici un exemple basé sur n/e :
            n = base64url_decode(key["n"])
            e = base64url_decode(key["e"])
            # On utilise jwk.construct(...) pour générer la clé
            return jwk.construct(dict(kty=key["kty"], n=n, e=e))
    # Si on n'a rien trouvé
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token: unknown kid")

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    """
    Vérifie que le token Bearer est valide et renvoie son payload décodé.
    """
    token = credentials.credentials
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token manquant",
        )
    try:
        # 1) Extraire l'en-tête (non vérifié) pour avoir le kid
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        if not kid:
            raise HTTPException(status_code=401, detail="Missing kid in token header")

        # 2) Récupérer la clé publique correspondante
        public_key = _get_public_key_from_jwks(kid)

        # 3) Décoder le token avec la clé
        payload = jwt.decode(
            token,
            public_key,
            algorithms=ALGORITHMS,
            audience=API_AUDIENCE,
            issuer=f"https://{AUTH0_DOMAIN}/"
        )

        return payload

    except JWTError as e:
        # JWTError capture, entre autres, signature invalide, audience manquante, etc.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token invalide: {str(e)}"
        ) from e
