import { decodeToken } from "./jwt";
import { authConfig } from "../api/auth";

/**
 * Validateur et analyseur sémantique de jeton JWT.
 * Utilise la clé 'exp' du payload du jeton de manière défensive.
 */
class TokenManager {
  /**
   * Décode le jeton d'accès pour renvoyer son payload de manière sécurisée (sans crash).
   * 
   * @param {string} token - Le jeton d'accès JWT
   * @returns {object|null} Le payload décodé ou null en cas d'erreur/malformation
   */
  decode(token) {
    if (!token) return null;
    try {
      return decodeToken(token);
    } catch (e) {
      console.warn("[TokenManager] Jeton malformé rencontré lors du décodage.", e);
      return null;
    }
  }

  /**
   * Valide la présence et la cohérence des claims OIDC standard de base (exp, iat, iss, aud).
   * 
   * @param {string} token - Le jeton d'accès JWT
   * @returns {boolean} True si le jeton possède les claims conformes
   */
  validateClaims(token) {
    const decoded = this.decode(token);
    if (!decoded) return false;

    // Claims indispensables requis pour le cycle de vie de l'authentification
    const required = ["exp", "iat", "iss", "aud"];
    const valid = required.every((claim) => claim in decoded);
    if (!valid) return false;

    // Validation sémantique de l'audience (peut être une chaîne ou un tableau de chaînes)
    const aud = decoded.aud;
    const isAudValid = Array.isArray(aud) ? aud.includes(authConfig.clientId) : aud === authConfig.clientId;
    if (!isAudValid) return false;

    // Cohérence temporelle
    if (decoded.exp <= decoded.iat) return false;

    return true;
  }

  /**
   * Récupère la date d'expiration brute (timestamp en secondes) du jeton.
   * 
   * @param {string} token - Le jeton d'accès JWT
   * @returns {number} Le timestamp d'expiration ou 0
   */
  getExpiration(token) {
    const decoded = this.decode(token);
    return decoded?.exp || 0;
  }

  /**
   * Calcule le temps restant en secondes avant l'expiration du jeton.
   * 
   * @param {string} token - Le jeton d'accès JWT
   * @returns {number} Nombre de secondes restantes (peut être négatif si expiré)
   */
  secondsRemaining(token) {
    const expiration = this.getExpiration(token);
    if (!expiration) return 0;
    
    const currentTime = Date.now() / 1000;
    return Math.floor(expiration - currentTime);
  }

  /**
   * Vérifie si le jeton est expiré (ou proche de l'expiration avec une marge de 5 secondes).
   * 
   * @param {string} token - Le jeton d'accès JWT
   * @returns {boolean} True si le jeton est expiré ou invalide
   */
  isExpired(token) {
    if (!token) return true;
    if (!this.validateClaims(token)) return true;
    return this.secondsRemaining(token) <= 5;
  }

  /**
   * Détermine si le jeton doit faire l'objet d'un rafraîchissement préventif (basé sur le seuil configuré).
   * 
   * @param {string} token - Le jeton d'accès JWT
   * @returns {boolean} True si un rafraîchissement préventif est recommandé
   */
  shouldRefresh(token) {
    if (!token) return true;
    return this.secondsRemaining(token) < authConfig.refreshThresholdSeconds;
  }

  /**
   * Extrait la liste des rôles applicatifs fusionnés.
   * 
   * @param {string} token - Le jeton d'accès JWT
   * @returns {Array<string>} Tableau des rôles
   */
  getRoles(token) {
    const decoded = this.decode(token);
    if (!decoded) return [];

    const realmRoles = decoded.realm_access?.roles || [];
    const clientRoles = decoded.resource_access?.["meeting-ai-backend"]?.roles || [];
    return [...new Set([...realmRoles, ...clientRoles])];
  }

  /**
   * Extrait l'email de l'utilisateur.
   * 
   * @param {string} token - Le jeton d'accès JWT
   * @returns {string|null} L'email ou null
   */
  getEmail(token) {
    const decoded = this.decode(token);
    return decoded?.email || null;
  }

  /**
   * Extrait l'identifiant utilisateur Keycloak.
   * 
   * @param {string} token - Le jeton d'accès JWT
   * @returns {string|null} L'identifiant ou null
   */
  getUsername(token) {
    const decoded = this.decode(token);
    return decoded?.preferred_username || decoded?.name || null;
  }
}

export default new TokenManager();
