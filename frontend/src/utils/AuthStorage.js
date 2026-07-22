import { authConfig } from "../api/auth";

// Cache en mémoire pour la session en cas de blocage d'accès au localStorage (ex: navigation privée stricte)
let inMemorySession = null;

/**
 * Gestionnaire unique du stockage de session.
 * Encapsule localStorage de manière défensive pour éviter les plantages applicatifs.
 */
class AuthStorage {
  /**
   * Enregistre le modèle de session sous forme d'un objet unique sérialisé en JSON.
   * 
   * @param {object} session - Objet contenant { access_token, refresh_token, token_type }
   */
  saveSession(session) {
    if (!session) return;
    const sessionToSave = {
      access_token: session.access_token || "",
      refresh_token: session.refresh_token || "",
      token_type: session.token_type || "Bearer"
    };

    try {
      localStorage.setItem(authConfig.storageKeys.session, JSON.stringify(sessionToSave));
    } catch (e) {
      console.warn("[AuthStorage] Échec d'écriture dans localStorage (accès restreint). Session stockée en mémoire uniquement.", e);
    }
    // Mise à jour systématique du cache mémoire de secours
    inMemorySession = sessionToSave;
  }

  /**
   * Charge le modèle de session.
   * 
   * @returns {object|null} L'objet session ou null
   */
  loadSession() {
    try {
      const rawSession = localStorage.getItem(authConfig.storageKeys.session);
      if (!rawSession) {
        return inMemorySession;
      }
      return JSON.parse(rawSession);
    } catch (e) {
      console.warn("[AuthStorage] Échec de lecture dans localStorage (accès restreint). Utilisation du cache mémoire.", e);
      return inMemorySession;
    }
  }

  /**
   * Met à jour partiellement la session courante.
   * 
   * @param {object} updatedData - Propriétés de la session à mettre à jour
   */
  updateSession(updatedData) {
    const current = this.loadSession() || {};
    this.saveSession({ ...current, ...updatedData });
  }

  /**
   * Supprime complètement l'objet session de stockage.
   */
  clearSession() {
    try {
      localStorage.removeItem(authConfig.storageKeys.session);
    } catch (e) {
      console.warn("[AuthStorage] Échec de suppression dans localStorage (accès restreint).");
    }
    inMemorySession = null;
  }

  /**
   * Récupère directement le jeton d'accès courant.
   * 
   * @returns {string|null} Le jeton d'accès ou null
   */
  getAccessToken() {
    const session = this.loadSession();
    return session?.access_token || null;
  }

  /**
   * Récupère directement le jeton de rafraîchissement courant.
   * 
   * @returns {string|null} Le jeton de rafraîchissement ou null
   */
  getRefreshToken() {
    const session = this.loadSession();
    return session?.refresh_token || null;
  }
}

export default new AuthStorage();
