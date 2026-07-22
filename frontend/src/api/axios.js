import axios from "axios";
import AuthStorage from "../utils/AuthStorage";
import TokenManager from "../utils/TokenManager";
import authService from "../services/auth.service";
import { authConfig } from "./auth";
import logger from "../utils/logger";

// Création de l'instance Axios partagée avec timeout et paramètres de retry par défaut
const axiosInstance = axios.create({
  baseURL: authConfig.apiBaseUrl,
  timeout: 15000, // Empêche les requêtes de rester bloquées indéfiniment (15 secondes)
  headers: {
    "Content-Type": "application/json",
  },
});

// Configuration du retry pour les pannes réseau ou serveur temporaires
axiosInstance.defaults.retry = 2; // Tentatives max de rejeu pour les erreurs réseau/serveur 5xx

// Variables de gestion du rafraîchissement
let isRefreshing = false;
let failedRequestsQueue = [];

// Libère toutes les requêtes en attente dans la file
const processQueue = (error, token = null) => {
  failedRequestsQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedRequestsQueue = [];
};

// Intercepteur de requête : Rafraîchissement Préventif & Injection Token
axiosInstance.interceptors.request.use(
  async (config) => {
    // Si la requête concerne l'obtention ou l'actualisation de jetons OIDC, on ne fait rien
    if (config.url.includes("/protocol/openid-connect") || config.url.includes(authConfig.endpoints.token)) {
      return config;
    }

    let token = AuthStorage.getAccessToken();

    // 1. Rafraîchissement préventif si le jeton expire dans moins de VITE_REFRESH_THRESHOLD secondes
    if (token && TokenManager.shouldRefresh(token)) {
      const refreshToken = AuthStorage.getRefreshToken();
      if (refreshToken) {
        if (isRefreshing) {
          // Attendre la fin du rafraîchissement en cours et obtenir le nouveau token
          try {
            const newToken = await new Promise((resolve, reject) => {
              failedRequestsQueue.push({ resolve, reject });
            });
            config.headers.Authorization = `Bearer ${newToken}`;
            return config;
          } catch (err) {
            return Promise.reject(err);
          }
        }

        isRefreshing = true;
        try {
          logger.info("Rafraîchissement préventif initié (expiration proche)...");
          const newTokens = await authService.refreshToken(refreshToken);
          if (newTokens && newTokens.access_token) {
            // Toujours remplacer l'ancien couple par le nouveau
            AuthStorage.saveSession(newTokens);
            token = newTokens.access_token;
            processQueue(null, newTokens.access_token);
          }
        } catch (error) {
          logger.error("Échec du rafraîchissement préventif.", error.message || error);
          processQueue(error, null);
          isRefreshing = false;
          
          // Déconnexion forcée
          AuthStorage.clearSession();
          delete axiosInstance.defaults.headers.common["Authorization"];
          window.location.href = "/login";
          return Promise.reject(error);
        } finally {
          isRefreshing = false;
        }
      }
    }

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Intercepteur de réponse : Gestion des retries temporaires & Gestion réactive des 401
axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    // 1. Gérer les requêtes annulées par AbortController (pas d'action de retry ni de déconnexion)
    if (axios.isCancel(error)) {
      logger.debug("Requête annulée volontairement par l'appelant.");
      return Promise.reject(error);
    }

    const originalRequest = error.config;

    // 2. Gestion réactive de l'erreur 401 Unauthorized (Rejeu unique)
    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // En attente du token en cours de rafraîchissement
        return new Promise((resolve, reject) => {
          failedRequestsQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            return axiosInstance(originalRequest);
          })
          .catch((err) => Promise.reject(err));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      const storedRefreshToken = AuthStorage.getRefreshToken();
      if (storedRefreshToken) {
        try {
          logger.info("Erreur 401 détectée. Rafraîchissement réactif du jeton...");
          const newTokens = await authService.refreshToken(storedRefreshToken);
          
          if (newTokens && newTokens.access_token) {
            // Toujours sauvegarder le nouveau couple
            AuthStorage.saveSession(newTokens);
            
            axiosInstance.defaults.headers.common["Authorization"] = `Bearer ${newTokens.access_token}`;
            originalRequest.headers.Authorization = `Bearer ${newTokens.access_token}`;
            
            processQueue(null, newTokens.access_token);
            isRefreshing = false;

            // Rejouer la requête d'origine
            return axiosInstance(originalRequest);
          }
        } catch (refreshError) {
          logger.error("Échec du rafraîchissement réactif. Déconnexion.", refreshError.message || refreshError);
          processQueue(refreshError, null);
          isRefreshing = false;
          
          AuthStorage.clearSession();
          delete axiosInstance.defaults.headers.common["Authorization"];
          window.location.href = "/login";
          return Promise.reject(refreshError);
        }
      } else {
        AuthStorage.clearSession();
        delete axiosInstance.defaults.headers.common["Authorization"];
        window.location.href = "/login";
      }
    }

    // 3. Rejeu exponentiel pour les erreurs réseau/serveur temporaires (5xx, timeout ou absence de réponse)
    const maxRetries = originalRequest ? (originalRequest.retry !== undefined ? originalRequest.retry : axiosInstance.defaults.retry) : undefined;
    if (originalRequest && maxRetries !== undefined) {
      originalRequest.retryCount = originalRequest.retryCount || 0;

      const isNetworkError = !error.response;
      const isTimeout = error.code === "ECONNABORTED";
      const isServerError = error.response && error.response.status >= 500;

      if ((isNetworkError || isTimeout || isServerError) && originalRequest.retryCount < maxRetries) {
        originalRequest.retryCount += 1;
        
        // Délai progressif : 2s, 4s...
        const backoffDelay = Math.pow(2, originalRequest.retryCount) * 1000;
        logger.warn(`Panne temporaire. Tentative de retry #${originalRequest.retryCount} dans ${backoffDelay}ms...`);
        
        await new Promise((resolve) => setTimeout(resolve, backoffDelay));
        return axiosInstance(originalRequest);
      }
    }

    return Promise.reject(error);
  }
);

export default axiosInstance;
