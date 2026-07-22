import React, { createContext, useState, useEffect, useCallback, useMemo } from "react";
import authService from "../services/auth.service";
import userService from "../services/user.service";
import AuthStorage from "../utils/AuthStorage";
import TokenManager from "../utils/TokenManager";
import axiosInstance from "../api/axios";
import { authConfig } from "../api/auth";
import logger from "../utils/logger";

export const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [session, setSession] = useState(AuthStorage.loadSession());
  const [user, setUser] = useState(null);
  const [roles, setRoles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // 1. Restauration de session au démarrage de l'application
  useEffect(() => {
    const restoreSession = async () => {
      const activeSession = AuthStorage.loadSession();

      if (activeSession && activeSession.access_token) {
        const accessToken = activeSession.access_token;
        const refreshToken = activeSession.refresh_token;

        // Si le jeton d'accès a expiré
        if (TokenManager.isExpired(accessToken)) {
          logger.info("Jeton d'accès expiré au démarrage. Tentative de renouvellement...");
          
          if (refreshToken) {
            try {
              const newTokens = await authService.refreshToken(refreshToken);
              if (newTokens && newTokens.access_token) {
                // Enregistrer le nouveau couple de tokens (access + refresh)
                AuthStorage.saveSession(newTokens);
                setSession(AuthStorage.loadSession());

                // Configurer les habilitations et le profil
                const decoded = TokenManager.decode(newTokens.access_token);
                setRoles(TokenManager.getRoles(newTokens.access_token));

                const profile = await userService.getCurrentUserProfile();
                setUser({
                  ...profile,
                  username: TokenManager.getUsername(newTokens.access_token) || profile.email,
                  displayName: decoded?.name || profile.email
                });

                setLoading(false);
                return;
              }
            } catch (err) {
              logger.error("Le renouvellement de démarrage a échoué :", err.message || err);
            }
          }
          
          // Déconnexion forcée en cas d'échec
          logout();
          setLoading(false);
          return;
        }

        // Si le jeton d'accès est toujours valide
        try {
          const decoded = TokenManager.decode(accessToken);
          setRoles(TokenManager.getRoles(accessToken));
          const profile = await userService.getCurrentUserProfile();
          setUser({
            ...profile,
            username: TokenManager.getUsername(accessToken) || profile.email,
            displayName: decoded?.name || profile.email
          });
        } catch (err) {
          logger.error("Erreur de restauration de la session active :", err.message || err);
          logout();
        }
      }
      setLoading(false);
    };

    restoreSession();
  }, [session?.access_token]);

  // 2. Timer de rafraîchissement périodique (toutes les 60 secondes)
  useEffect(() => {
    let intervalId = null;

    if (session && session.access_token) {
      intervalId = setInterval(async () => {
        const token = AuthStorage.getAccessToken();
        if (token && TokenManager.shouldRefresh(token)) {
          logger.info("Expiration proche détectée par le timer. Rafraîchissement silencieux...");
          const currentRefreshToken = AuthStorage.getRefreshToken();
          
          if (currentRefreshToken) {
            try {
              const newTokens = await authService.refreshToken(currentRefreshToken);
              if (newTokens && newTokens.access_token) {
                // Toujours remplacer l'ancien refresh par le nouveau
                AuthStorage.saveSession(newTokens);
                setSession(AuthStorage.loadSession());
                logger.info("Jeton renouvelé avec succès par le planificateur.");
              }
            } catch (err) {
              logger.error("Échec du rafraîchissement périodique planifié :", err.message || err);
              logout();
            }
          }
        }
      }, authConfig.timerIntervalMs);
    }

    // Nettoyage de l'intervalle au démontage ou au logout
    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [session?.access_token]);

  // 3. Synchronisation de déconnexion et de session inter-onglets (Multi-tab concurrency)
  useEffect(() => {
    const handleStorageSync = (event) => {
      if (event.key === authConfig.storageKeys.session) {
        if (!event.newValue) {
          // La session a été supprimée (ex: logout dans un autre onglet)
          logger.info("Session invalidée depuis un autre onglet. Déconnexion immédiate.");
          
          // Réinitialisation des états locaux
          setSession(null);
          setUser(null);
          setRoles([]);
          setError(null);
          delete axiosInstance.defaults.headers.common["Authorization"];

          if (window.location.pathname !== "/login") {
            window.location.href = "/login";
          }
        } else {
          // Les jetons ont été mis à jour par un rafraîchissement dans un autre onglet
          logger.info("Session mise à jour depuis un autre onglet. Synchronisation...");
          const updatedSession = AuthStorage.loadSession();
          setSession(updatedSession);
        }
      }
    };

    window.addEventListener("storage", handleStorageSync);
    return () => window.removeEventListener("storage", handleStorageSync);
  }, []);

  /**
   * Connecte l'utilisateur en transmettant ses identifiants.
   * Différencie proprement les erreurs réseau des identifiants incorrects.
   */
  const login = useCallback(async (email, password) => {
    setLoading(true);
    setError(null);
    try {
      const data = await authService.login(email, password);
      
      if (data && data.access_token) {
        AuthStorage.saveSession(data);
        setSession(AuthStorage.loadSession());

        const decoded = TokenManager.decode(data.access_token);
        setRoles(TokenManager.getRoles(data.access_token));

        const profile = await userService.getCurrentUserProfile();
        setUser({
          ...profile,
          username: TokenManager.getUsername(data.access_token) || profile.email,
          displayName: decoded?.name || profile.email
        });

        setLoading(false);
        return true;
      }
      throw new Error("Format de réponse invalide");
    } catch (err) {
      logger.error("Échec de la connexion :", err.message || err);
      
      if (!err.response) {
        // Pas de réponse HTTP (serveur éteint, erreur CORS ou timeout réseau)
        setError("Impossible de contacter le serveur d'authentification. Veuillez réessayer ultérieurement.");
      } else if (err.response.status === 401 || err.response.status === 400) {
        // Mauvais mot de passe ou email
        setError("Email ou mot de passe incorrect.");
      } else {
        // Autre erreur masquée
        setError("Impossible de contacter le serveur d'authentification. Veuillez réessayer ultérieurement.");
      }
      setLoading(false);
      return false;
    }
  }, []);

  /**
   * Déconnecte l'utilisateur localement, nettoie les en-têtes Axios et redirige vers /login.
   */
  const logout = useCallback(() => {
    // Appel facultatif du logout logique réseau en tâche de fond
    authService.logout().catch((err) => {
      logger.warn("Échec facultatif du logout Keycloak:", err.message || err);
    });

    // Vider le stockage centralisé
    AuthStorage.clearSession();
    
    // Réinitialisation des états locaux
    setSession(null);
    setUser(null);
    setRoles([]);
    setError(null);

    // Suppression du header d'autorisation Axios
    delete axiosInstance.defaults.headers.common["Authorization"];

    // Redirection vers le login
    if (window.location.pathname !== "/login") {
      window.location.href = "/login";
    }
  }, []);

  const value = useMemo(() => ({
    token: session?.access_token || null,
    refreshToken: session?.refresh_token || null,
    tokenType: session?.token_type || null,
    user,
    roles,
    isAuthenticated: !!session?.access_token,
    loading,
    error,
    login,
    logout
  }), [session, user, roles, loading, error, login, logout]);

  return <AuthContext value={value}>{children}</AuthContext>;
};
