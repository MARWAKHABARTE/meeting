import React from "react";
import { useWebSocket } from "../hooks/useWebSocket";

/**
 * Composant indicateur de statut de la connexion WebSocket temps réel.
 * Propose un affichage discret avec micro-animations et design premium.
 */
export const ConnectionStatus = () => {
  const { isConnected } = useWebSocket();

  return (
    <div style={styles.container} title={isConnected ? "WebSocket connecté" : "WebSocket déconnecté"}>
      <span
        style={{
          ...styles.badge,
          ...(isConnected ? styles.connectedBadge : styles.disconnectedBadge),
        }}
      />
      <span style={styles.text}>{isConnected ? "Live Sync" : "Reconnexion..."}</span>
    </div>
  );
};

const styles = {
  container: {
    display: "flex",
    alignItems: "center",
    gap: "8px",
    padding: "6px 12px",
    borderRadius: "20px",
    background: "rgba(255, 255, 255, 0.05)",
    backdropFilter: "blur(10px)",
    border: "1px solid rgba(255, 255, 255, 0.1)",
    boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)",
    width: "fit-content",
    fontSize: "12px",
    fontWeight: 500,
    color: "#fff",
    fontFamily: "'Inter', sans-serif",
  },
  badge: {
    display: "inline-block",
    width: "8px",
    height: "8px",
    borderRadius: "50%",
    position: "relative",
  },
  connectedBadge: {
    backgroundColor: "#10b981", // Emeraude vibrant
    boxShadow: "0 0 8px #10b981",
    animation: "pulseGreen 2s infinite ease-in-out",
  },
  disconnectedBadge: {
    backgroundColor: "#ef4444", // Rouge vif
    boxShadow: "0 0 8px #ef4444",
    animation: "pulseRed 1.5s infinite ease-in-out",
  },
  text: {
    letterSpacing: "0.5px",
  },
};

// Styles d'animation injectés globalement si nécessaire, ou on s'appuie sur index.css
export default ConnectionStatus;
