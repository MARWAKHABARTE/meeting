from pydantic_settings import BaseSettings


class WebSocketSettings(BaseSettings):
    """
    Configuration du module WebSocket temps réel.
    Toutes les valeurs sont centralisées ici et injectées via Settings.
    """
    # Intervalle entre deux pings serveur → clients (secondes)
    WEBSOCKET_HEARTBEAT_INTERVAL: int = 30

    # Délai maximum d'inactivité avant fermeture de la connexion (secondes)
    WEBSOCKET_TIMEOUT: int = 300

    # Nombre maximal de connexions simultanées acceptées par le serveur
    WEBSOCKET_MAX_CONNECTIONS: int = 500

    # Délai initial de reconnexion côté client (millisecondes)
    WEBSOCKET_RECONNECT_DELAY_MS: int = 1000

    # Délai maximal de reconnexion (backoff exponentiel, millisecondes)
    WEBSOCKET_RECONNECT_MAX_DELAY_MS: int = 30000

    # Canal Redis utilisé pour la communication Workers → Broadcaster
    WEBSOCKET_REDIS_CHANNEL: str = "ws_events"
