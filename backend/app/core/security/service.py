import logging
import jwt
from jwt.exceptions import PyJWTError, ExpiredSignatureError, InvalidAudienceError
from fastapi import HTTPException, status
from app.core.settings import settings

logger = logging.getLogger("meeting_ai")

class KeycloakSecurityService:
    """
    Service de sécurité gérant la validation des tokens JWT Keycloak.
    Utilise PyJWKClient pour charger et mettre en cache les clés de signature (JWKS).
    """

    def __init__(self) -> None:
        self.certs_url = (
            f"{settings.KEYCLOAK_SERVER_URL.rstrip('/')}/realms/"
            f"{settings.KEYCLOAK_REALM}/protocol/openid-connect/certs"
        )
        # PyJWKClient gère automatiquement le cache interne des clés publiques
        self.jwks_client = jwt.PyJWKClient(self.certs_url)

    def verify_token(self, token: str) -> dict:
        """
        Décode et valide la signature asymétrique d'un token JWT.
        Lève une HTTPException 401 si le token est invalide ou expiré.
        """
        try:
            # Récupère la clé publique de signature correspondante (kid dans l'en-tête du JWT)
            signing_key = self.jwks_client.get_signing_key_from_jwt(token)
            
            # Décode le payload et valide l'émetteur (iss), l'audience (aud) et l'expiration (exp)
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                audience=settings.KEYCLOAK_CLIENT_ID,
                options={
                    "verify_aud": True,
                    "verify_iss": True,
                    "verify_exp": True
                }
            )
            return payload
            
        except ExpiredSignatureError as e:
            logger.warning(f"Validation JWT échouée : Token expiré. Détails : {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except InvalidAudienceError as e:
            logger.warning(f"Validation JWT échouée : Audience incorrecte. Détails : {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token audience",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except PyJWTError as e:
            logger.warning(f"Validation JWT échouée : Signature ou format invalide. Détails : {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            logger.error(f"Erreur inattendue lors de la validation du token : {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal authentication service error",
            )

    @staticmethod
    def extract_roles(payload: dict) -> list[str]:
        """
        Extrait les rôles depuis le token (Realm et Client spécifique).
        """
        roles = []
        
        # 1. Extraction des rôles du Realm
        realm_access = payload.get("realm_access", {})
        roles.extend(realm_access.get("roles", []))
        
        # 2. Extraction des rôles du Client
        resource_access = payload.get("resource_access", {})
        client_access = resource_access.get(settings.KEYCLOAK_CLIENT_ID, {})
        roles.extend(client_access.get("roles", []))
        
        # Déduplication
        return list(set(roles))

# Instance globale réutilisable
keycloak_security_service = KeycloakSecurityService()
