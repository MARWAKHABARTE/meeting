from pydantic_settings import BaseSettings

class KeycloakSettings(BaseSettings):
    """
    Configuration de l'authentification Keycloak (OAuth2 / OIDC).
    """
    KEYCLOAK_SERVER_URL: str = "http://localhost:8080"
    KEYCLOAK_REALM: str = "meeting-ai-realm"
    KEYCLOAK_CLIENT_ID: str = "meeting-ai-client"
    KEYCLOAK_CLIENT_SECRET: str = "client-secret-placeholder"
    KEYCLOAK_ADMIN_USERNAME: str = "admin"
    KEYCLOAK_ADMIN_PASSWORD: str = "admin"
