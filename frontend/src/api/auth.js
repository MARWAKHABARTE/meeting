/**
 * Configuration centralisée pour l'authentification OIDC et l'API.
 * Récupère les variables d'environnement injectées par Vite ou utilise des valeurs par défaut locales.
 */

const KEYCLOAK_URL = import.meta.env.VITE_KEYCLOAK_URL || "http://localhost/keycloak";
const REALM = import.meta.env.VITE_KEYCLOAK_REALM || "meeting-ai";

export const authConfig = {
  // Informations client
  clientId: import.meta.env.VITE_KEYCLOAK_CLIENT_ID || "meeting-ai-frontend",
  realm: REALM,
  keycloakUrl: KEYCLOAK_URL,
  apiBaseUrl: import.meta.env.VITE_API_URL || "/api",

  // Seuils et intervalles temporels
  refreshThresholdSeconds: parseInt(import.meta.env.VITE_REFRESH_THRESHOLD || "30", 10),
  timerIntervalMs: 60000, // Vérification périodique toutes les 60 secondes (60 000 ms)

  // Endpoints OIDC et API
  endpoints: {
    token: `${KEYCLOAK_URL}/realms/${REALM}/protocol/openid-connect/token`,
    logout: `${KEYCLOAK_URL}/realms/${REALM}/protocol/openid-connect/logout`,
    userProfile: "/v1/auth/me",
    health: "/health",
  },

  // Clé unique pour le stockage local de la session
  storageKeys: {
    session: "auth_session"
  }
};
