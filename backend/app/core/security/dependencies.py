from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Annotated

from app.db.session import get_db
from app.models.user import User
from app.core.security.service import keycloak_security_service

# Schéma d'authentification Bearer Token utilisé par OpenAPI/Swagger
reusable_oauth2 = HTTPBearer(auto_error=True)

async def get_token_payload(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(reusable_oauth2)]
) -> dict:
    """
    Dépendance qui extrait et valide le token JWT.
    Retourne le dictionnaire décodé du payload.
    """
    return keycloak_security_service.verify_token(credentials.credentials)

async def get_current_user(
    db: Annotated[Session, Depends(get_db)],
    payload: Annotated[dict, Depends(get_token_payload)]
) -> User:
    """
    Dépendance qui récupère l'utilisateur connecté.
    Si l'utilisateur n'existe pas encore en base de données mais possède un JWT valide,
    il est créé à la volée (Just-In-Time Provisioning) sur la base de son email.
    """
    email = payload.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token does not contain an email claim",
        )

    # Recherche de l'utilisateur en base
    stmt = select(User).where(User.email == email)
    user = db.execute(stmt).scalar_one_or_none()

    if not user:
        # Détermination des rôles pour provisionner les attributs de base
        roles = keycloak_security_service.extract_roles(payload)
        is_admin = "admin" in roles

        # Création JIT (pas de mot de passe stocké localement)
        user = User(
            email=email,
            hashed_password="",  
            is_active=True,
            is_superuser=is_admin
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Dépendance qui vérifie si l'utilisateur connecté est actif.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

class RoleChecker:
    """
    Classe utilitaire pour vérifier l'appartenance à un ou plusieurs rôles.
    """
    def __init__(self, allowed_roles: list[str]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, payload: Annotated[dict, Depends(get_token_payload)]) -> None:
        user_roles = keycloak_security_service.extract_roles(payload)
        
        # Un administrateur possède implicitement tous les droits
        if "admin" in user_roles:
            return

        # Vérifie s'il y a une intersection entre les rôles de l'utilisateur et ceux requis
        if not any(role in user_roles for role in self.allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role(s) {self.allowed_roles} required to access this resource"
            )

# Dépendances prêtes à l'emploi pour les contrôles d'accès dans les routeurs
require_admin = RoleChecker(["admin"])
require_manager = RoleChecker(["manager"])
