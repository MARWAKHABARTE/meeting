import React, { createContext, useEffect, useState, useCallback } from "react";
import { useAuth } from "../hooks/useAuth";
import websocketService from "../services/websocket.service";
import logger from "../utils/logger";

export const WebSocketContext = createContext(null);

export const WebSocketProvider = ({ children }) => {
  const { session } = useAuth();
  const [isConnected, setIsConnected] = useState(false);
  const [lastEvent, setLastEvent] = useState(null);

  // Écoute de l'état de connexion globale du service
  useEffect(() => {
    const unsubStatus = websocketService.subscribe("CONNECTION_STATUS", (statusPayload) => {
      setIsConnected(statusPayload.connected);
    });

    const unsubAll = websocketService.subscribe("*", (event) => {
      setLastEvent(event);
    });

    return () => {
      unsubStatus();
      unsubAll();
    };
  }, []);

  // Gérer la connexion / déconnexion en fonction de la présence de la session utilisateur
  useEffect(() => {
    if (session && session.access_token) {
      logger.info("[WebSocket Provider] Jeton de session détecté. Connexion au WebSocket...");
      websocketService.connect(session.access_token);
    } else {
      if (websocketService.isConnected) {
        logger.info("[WebSocket Provider] Pas de session active. Déconnexion du WebSocket.");
        websocketService.disconnect();
      }
    }

    return () => {
      // Déconnexion lors du démontage du provider
      websocketService.disconnect();
    };
  }, [session]);

  const subscribe = useCallback((eventType, callback) => {
    return websocketService.subscribe(eventType, callback);
  }, []);

  const value = {
    isConnected,
    lastEvent,
    subscribe,
  };

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
};
export default WebSocketContext;
