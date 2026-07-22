import { useContext } from "react";
import { WebSocketContext } from "../context/WebSocketContext";

/**
 * Hook personnalisé pour consommer le contexte WebSocket temps réel.
 * Expose l'état de connexion et la méthode d'abonnement.
 */
export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error("useWebSocket doit être utilisé à l'intérieur d'un WebSocketProvider");
  }
  return context;
};
export default useWebSocket;
