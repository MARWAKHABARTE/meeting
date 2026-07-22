class WebSocketException(Exception):
    """Exception de base pour le module WebSocket."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class ConnectionLimitException(WebSocketException):
    """Exception levée lorsque la limite de connexions est atteinte."""
    def __init__(self, limit: int):
        super().__init__(f"Limite de connexions simultanées atteinte ({limit}).")
        self.limit = limit


class BroadcastException(WebSocketException):
    """Exception levée lors d'un échec de diffusion (broadcast)."""
    def __init__(self, details: str):
        super().__init__(f"Échec de la diffusion de l'événement : {details}")
        self.details = details


class AuthenticationException(WebSocketException):
    """Exception levée lors d'un échec d'authentification du client WebSocket."""
    def __init__(self, reason: str):
        super().__init__(f"Authentification WebSocket échouée : {reason}")
        self.reason = reason
