import React, { useEffect, useState } from "react";
import { useWebSocket } from "../hooks/useWebSocket";
import { Bell, CheckCircle2, AlertTriangle, FileText, X } from "lucide-react";

/**
 * Centre de notifications SaaS pour événements métier.
 * Transforme les notifications système en messages clairs pour l'utilisateur.
 */
export const NotificationCenter = () => {
  const { subscribe } = useWebSocket();
  const [toasts, setToasts] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    const handleEvent = (eventData) => {
      const { event, payload } = eventData;
      if (event === "NOTIFICATION" || event === "MEETING_UPDATED" || event === "ERROR") {
        let title = "Notification";
        let message = payload.message || "Mise à jour disponible";
        let type = "info";
        let icon = FileText;

        if (payload.status === "completed" || event === "MEETING_COMPLETED") {
          title = "Réunion analysée";
          message = payload.title ? `L'analyse de "${payload.title}" est terminée.` : "Compte-rendu et synthèses disponibles.";
          type = "success";
          icon = CheckCircle2;
        } else if (payload.type === "report_generated") {
          title = "Rapport généré";
          message = "Nouveau compte-rendu disponible au téléchargement.";
          type = "success";
          icon = FileText;
        } else if (event === "ERROR" || payload.status === "failed") {
          title = "Analyse interrompue";
          message = "L'analyse a rencontré une difficulté. Veuillez rééessayer.";
          type = "warning";
          icon = AlertTriangle;
        }

        addToast(title, message, type, icon);
      }
    };

    const unsubscribe = subscribe("*", handleEvent);
    return () => unsubscribe();
  }, [subscribe]);

  const addToast = (title, message, type, IconComponent) => {
    const id = Math.random().toString(36).substr(2, 9);
    setToasts((prev) => [...prev, { id, title, message, type, IconComponent }]);
    setUnreadCount((prev) => prev + 1);

    setTimeout(() => {
      removeToast(id);
    }, 6000);
  };

  const removeToast = (id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  return (
    <div className="notification-wrapper">
      {/* Popups Toasts */}
      <div className="toast-container">
        {toasts.map((toast) => {
          const Icon = toast.IconComponent || FileText;
          return (
            <div key={toast.id} className={`toast-card toast-${toast.type}`}>
              <div className="toast-icon">
                <Icon size={18} />
              </div>
              <div className="toast-content">
                <h4 className="toast-title">{toast.title}</h4>
                <p className="toast-message">{toast.message}</p>
              </div>
              <button
                className="toast-close-btn"
                onClick={() => removeToast(toast.id)}
                aria-label="Fermer"
              >
                <X size={14} />
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default NotificationCenter;
