import jwt
from caddy_api import settings
from fastapi import Request, HTTPException
from pydantic import BaseModel, Field
from typing import List


# Define a estrutura do token decodificado
class HasuraClaims(BaseModel):
    x_hasura_allowed_roles: List[str] = Field(..., alias="x-hasura-allowed-roles")
    x_hasura_default_role: str = Field(..., alias="x-hasura-default-role")
    x_hasura_user_id: str = Field(..., alias="x-hasura-user-id")


class DecodedToken(BaseModel):
    sub: str
    role: str
    user_id: int
    is_admin: int
    https_hasura_io_jwt_claims: HasuraClaims = Field(
        ..., alias="https://hasura.io/jwt/claims"
    )
    iat: int
    aud: str


def validate_authentication(request: Request) -> DecodedToken:
    """
    Obtém token de autorização por Header ou Cookie da requisição e decodifica para validação.

    :param request: Requisição HTTP, deve possuir Header Auhorization ou Cookie session.
    """
    # import ipdb;ipdb.set_trace()
    jwt_token = None
    auth_header = request.headers.get("Authorization")
    session_cookie = request.cookies.get("session")

    if auth_header and auth_header.startswith("Bearer "):
        # Valida o header de Authorization
        jwt_token = auth_header.split(" ")[1]
    elif session_cookie:
        # Valida o cookie de sessão
        jwt_token = session_cookie

    if not jwt_token:
        raise HTTPException(status_code=401, detail="Missing JWT token")

    try:
        # Decodifica o JWT
        decoded_token = DecodedToken(
            **jwt.decode(
                jwt_token,
                settings.JWT_SECRET,
                algorithms=[settings.JWT_ALGORITHM],
                audience=settings.JWT_AUDIENCE,
            )
        )

        return decoded_token
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Expired JWT token")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid JWT token")
