import axiosInstance from "../api/axios";
import { authConfig } from "../api/auth";

/**
 * Service gérant les données utilisateur et la communication avec le backend.
 */
class UserService {
  /**
   * Récupère le profil de l'utilisateur connecté depuis notre backend FastAPI (déclenche le JIT Provisioning).
   * 
   * @returns {Promise<object>} Profil utilisateur (id, email, is_superuser, etc.)
   */
  async getCurrentUserProfile() {
    const response = await axiosInstance.get(authConfig.endpoints.userProfile);
    return response.data;
  }

  /**
   * Ping l'endpoint /health du backend pour diagnostiquer l'état du serveur FastAPI et PostgreSQL.
   * 
   * @returns {Promise<object>} Réponse de santé {"status": "healthy"}
   */
  async checkBackendHealth() {
    const response = await axiosInstance.get(authConfig.endpoints.health);
    return response.data;
  }
}

export default new UserService();
