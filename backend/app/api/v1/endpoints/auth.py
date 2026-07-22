import uuid
from datetime import datetime
from typing import Annotated
from pydantic import BaseModel, ConfigDict
from fastapi import APIRouter, Depends

from app.models.user import User
from app.core.security.dependencies import get_current_active_user, get_token_payload
from app.core.security.service import keycloak_security_service

router = APIRouter()

class UserOut(BaseModel):
    """
    Schéma Pydantic v2 de sortie pour l'utilisateur.
    """
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

class UserRolesOut(BaseModel):
    """
    Schéma Pydantic v2 pour renvoyer la liste des rôles.
    """
    roles: list[str]

@router.get("/me", response_model=UserOut, summary="Récupérer l'utilisateur courant")
async def get_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> User:
    """
    Retourne le profil de l'utilisateur courant synchronisé en base de données local.
    """
    return current_user

@router.get("/roles", response_model=UserRolesOut, summary="Récupérer les rôles de l'utilisateur")
async def get_roles(
    payload: Annotated[dict, Depends(get_token_payload)]
) -> dict:
    """
    Extrait les rôles (Realm + Client) du token Keycloak de l'utilisateur connecté.
    """
    roles = keycloak_security_service.extract_roles(payload)
    return {"roles": roles}
