import React from "react";
import { useWebSocket } from "../hooks/useWebSocket";

/**
 * Composant de maintien de la connexion WebSocket en arrière-plan.
 * Complètement invisible pour l'utilisateur final.
 */
export const ConnectionStatus = () => {
  // Conserve l'écoute du hook WebSocket en arrière-plan
  useWebSocket();
  return null;
};

export default ConnectionStatus;
