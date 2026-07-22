import React, { useEffect, useState } from "react";
import { useWebSocket } from "../hooks/useWebSocket";
import logger from "../utils/logger";

/**
 * Centre de notifications flottant (Toasts).
 * Reçoit directement les messages WebSocket de type NOTIFICATION ou ERROR
 * et les affiche sous forme de cartes élégantes temporaires.
 */
export const NotificationCenter = () => {
  const { subscribe } = useWebSocket();
  const [toasts, setToasts] = useState([]);

  useEffect(() => {
    // Écoute de tous les événements de type NOTIFICATION ou ERROR
    const handleEvent = (eventData) => {
      const { event, payload } = eventData;
      if (event === "NOTIFICATION" || event === "ERROR") {
        const message = payload.message || payload.details || "Événement reçu";
        const title = event === "ERROR" ? "Erreur" : payload.title || "Notification";
        const type = event === "ERROR" ? "error" : payload.type || "info";

        addToast(title, message, type);
      }
    };

    const unsubscribe = subscribe("*", handleEvent);
    return () => {
      unsubscribe();
    };
  }, [subscribe]);

  const addToast = (title, message, type) => {
    const id = Math.random().toString(36).substr(2, 9);
    setToasts((prev) => [...prev, { id, title, message, type }]);

    // Auto-dismiss après 5s
    setTimeout(() => {
      removeToast(id);
    }, 5000);
  };

  const removeToast = (id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  return (
    <div style={styles.container}>
      {toasts.map((toast) => (
        <div
          key={toast.id}
          style={{
            ...styles.toast,
            ...styles[toast.type],
          }}
        >
          <div style={styles.header}>
            <span style={styles.title}>{toast.title}</span>
            <button style={styles.closeBtn} onClick={() => removeToast(toast.id)}>
              &times;
            </button>
          </div>
          <div style={styles.message}>{toast.message}</div>
        </div>
      ))}
    </div>
  );
};

const styles = {
  container: {
    position: "fixed",
    top: "24px",
    right: "24px",
    zIndex: 9999,
    display: "flex",
    flexDirection: "column",
    gap: "12px",
    width: "320px",
    pointerEvents: "none",
  },
  toast: {
    pointerEvents: "auto",
    padding: "16px",
    borderRadius: "12px",
    backdropFilter: "blur(12px)",
    boxShadow: "0 10px 25px rgba(0, 0, 0, 0.2)",
    border: "1px solid rgba(255, 255, 255, 0.1)",
    fontFamily: "'Inter', sans-serif",
    transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
    animation: "slideIn 0.3s forwards",
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "6px",
  },
  title: {
    fontWeight: 600,
    fontSize: "14px",
    color: "#fff",
  },
  message: {
    fontSize: "13px",
    color: "rgba(255, 255, 255, 0.8)",
    lineHeight: "1.4",
  },
  closeBtn: {
    background: "none",
    border: "none",
    color: "rgba(255, 255, 255, 0.6)",
    fontSize: "18px",
    cursor: "pointer",
    padding: 0,
    lineHeight: "1",
  },
  // Variantes de styles par type
  info: {
    background: "rgba(30, 41, 59, 0.85)", // Slate
  },
  success: {
    background: "rgba(6, 78, 59, 0.85)", // Emerald
    borderLeft: "4px solid #10b981",
  },
  warning: {
    background: "rgba(120, 53, 4, 0.85)", // Amber
    borderLeft: "4px solid #f59e0b",
  },
  error: {
    background: "rgba(153, 27, 27, 0.85)", // Red
    borderLeft: "4px solid #ef4444",
  },
};

export default NotificationCenter;
