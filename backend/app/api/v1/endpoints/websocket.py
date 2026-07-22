import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from app.core.security.service import keycloak_security_service
from app.db.session import SessionLocal
from app.models.user import User
from app.websocket.manager import ConnectionManager
from app.websocket.exceptions import ConnectionLimitException, AuthenticationException
from sqlalchemy import select

logger = logging.getLogger("meeting_ai")
router = APIRouter()
manager = ConnectionManager()


@router.websocket("")
@router.websocket("/")
@router.websocket("/{meeting_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    meeting_id: str | None = None,
    token: str = Query(..., description="JWT token pour l'authentification")
):
    """
    Point d'entrée WebSocket temps réel sécurisé par token JWT.
    Rejoint automatiquement la room de l'utilisateur et optionnellement de la réunion.
    """
    # 1. Authentification du Token JWT Keycloak
    try:
        payload = keycloak_security_service.verify_token(token)
        email = payload.get("email")
        if not email:
            raise AuthenticationException("Le token ne contient pas d'adresse email.")
    except Exception as e:
        logger.warning(f"[WebSocket Endpoint] Échec de l'authentification WebSocket : {e}")
        # Fermeture immédiate de la connexion si non authentifié
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Authentification échouée")
        return

    # 2. Récupération ou création JIT de l'utilisateur connecté
    db = SessionLocal()
    try:
        stmt = select(User).where(User.email == email)
        user = db.execute(stmt).scalar_one_or_none()
        if not user:
            # Création rapide (Just-In-Time) comme dans les dépendances de sécurité
            roles = keycloak_security_service.extract_roles(payload)
            is_admin = "admin" in roles
            user = User(
                email=email,
                hashed_password="",
                is_active=True,
                is_superuser=is_admin
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        user_id = str(user.id)
    except Exception as e:
        logger.error(f"[WebSocket Endpoint] Erreur lors de la récupération de l'utilisateur : {e}")
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR, reason="Erreur de base de données")
        return
    finally:
        db.close()

    # 3. Connexion au ConnectionManager
    # On accepte la connexion d'abord
    await websocket.accept()

    try:
        connection = await manager.connect(websocket, user_id=user_id, meeting_id=meeting_id)
    except ConnectionLimitException as e:
        logger.warning(f"[WebSocket Endpoint] Limite de connexions atteinte : {e.message}")
        await websocket.close(code=status.WS_1013_TRY_AGAIN_LATER, reason=e.message)
        return
    except Exception as e:
        logger.error(f"[WebSocket Endpoint] Échec de l'enregistrement de la connexion : {e}")
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR, reason="Erreur système")
        return

    # 4. Boucle de maintien de la connexion et écoute (Ping/Pong, déconnexion)
    try:
        while True:
            # On écoute les messages entrants (principalement pour détecter la déconnexion)
            data = await websocket.receive_text()
            logger.debug(f"[WebSocket Endpoint] Message reçu du client '{user_id}' : {data}")
    except WebSocketDisconnect:
        logger.info(f"[WebSocket Endpoint] Déconnexion reçue pour le client '{user_id}'.")
    except Exception as e:
        logger.error(f"[WebSocket Endpoint] Erreur inattendue dans la boucle WebSocket pour '{user_id}' : {e}")
    finally:
        await manager.disconnect(websocket)
