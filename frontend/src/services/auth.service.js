import axios from "axios";
import { authConfig } from "../api/auth";

/**
 * Service pur d'intégration d'appels HTTP avec Keycloak.
 * Sans aucune dépendance React ni manipulation directe du stockage.
 */
class AuthService {
  /**
   * Effectue la requête POST d'authentification par mot de passe (Direct Access Grants).
   * 
   * @param {string} email - L'e-mail de l'utilisateur
   * @param {string} password - Le mot de passe de l'utilisateur
   * @returns {Promise<object>} Les données de jetons retournées par Keycloak
   */
  async login(email, password) {
    const params = new URLSearchParams({
      grant_type: "password",
      client_id: authConfig.clientId,
      username: email,
      password: password,
      scope: "openid profile email"
    });

    const response = await axios.post(authConfig.endpoints.token, params, {
      headers: {
        "Content-Type": "application/x-www-form-urlencoded"
      }
    });

    return response.data;
  }

  /**
   * Effectue la requête de rafraîchissement de jeton d'accès.
   * 
   * @param {string} refreshToken - Le jeton de rafraîchissement courant
   * @returns {Promise<object>} Les nouveaux jetons de session
   */
  async refreshToken(refreshToken) {
    const params = new URLSearchParams({
      grant_type: "refresh_token",
      refresh_token: refreshToken,
      client_id: authConfig.clientId
    });

    const response = await axios.post(authConfig.endpoints.token, params, {
      headers: {
        "Content-Type": "application/x-www-form-urlencoded"
      }
    });

    return response.data;
  }

  /**
   * Déconnexion logique.
   * Méthode vide car le stockage de session est géré séparément par AuthStorage.
   */
  async logout() {
    // Squelette prêt pour de futures extensions (ex: appel de révocation de jeton au serveur)
    return true;
  }

  /**
   * Construit l'URL de fin de session Keycloak officielle pour de futures évolutions.
   * 
   * @param {string} redirectUri - URL de retour après déconnexion
   * @returns {string} URL complète de déconnexion Keycloak
   */
  buildLogoutUrl(redirectUri = "http://localhost/login") {
    const params = new URLSearchParams({
      client_id: authConfig.clientId,
      post_logout_redirect_uri: redirectUri
    });
    return `${authConfig.endpoints.logout}?${params.toString()}`;
  }
}

export default new AuthService();
