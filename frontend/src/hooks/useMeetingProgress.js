import { useState, useEffect } from "react";
import { useWebSocket } from "./useWebSocket";
import logger from "../utils/logger";

const INITIAL_STEPS = {
  transcription: { percent: 0, status: "pending", label: "Transcription & Diarisation" },
  summary: { percent: 0, status: "pending", label: "Résumé NLP & Sentiments" },
  embedding: { percent: 0, status: "pending", label: "Indexation sémantique" },
};

/**
 * Hook de suivi de progression temps réel pour une réunion spécifique.
 * Écoute et filtre les événements WebSocket.
 * @param {string|null} meetingId - ID de la réunion à suivre.
 */
export const useMeetingProgress = (meetingId) => {
  const { subscribe, isConnected } = useWebSocket();
  const [steps, setSteps] = useState(INITIAL_STEPS);
  const [hasError, setHasError] = useState(false);
  const [errorDetails, setErrorDetails] = useState("");
  const [isComplete, setIsComplete] = useState(false);
  const [notifications, setNotifications] = useState([]);

  // Réinitialiser les états si le meetingId change
  useEffect(() => {
    setSteps(INITIAL_STEPS);
    setHasError(false);
    setErrorDetails("");
    setIsComplete(false);
  }, [meetingId]);

  useEffect(() => {
    if (!meetingId) return;

    const handleProgress = (eventData) => {
      // Filtrer les événements pour s'assurer qu'ils concernent la réunion actuelle
      if (eventData.meeting_id !== meetingId) return;

      const { event, payload } = eventData;
      const { step, percent, status, details } = payload;

      setSteps((prevSteps) => {
        const nextSteps = { ...prevSteps };

        // Identification de la catégorie de tâche
        let category = null;
        if (event.startsWith("TRANSCRIPTION_")) category = "transcription";
        else if (event.startsWith("SUMMARY_")) category = "summary";
        else if (event.startsWith("EMBEDDING_")) category = "embedding";

        if (category) {
          nextSteps[category] = {
            ...nextSteps[category],
            percent: percent ?? nextSteps[category].percent,
            status: status ?? nextSteps[category].status,
            details: details ?? nextSteps[category].details,
          };
        }

        // Vérification de la complétion globale
        const allCompleted = Object.values(nextSteps).every((s) => s.status === "completed");
        if (allCompleted) {
          setIsComplete(true);
        }

        return nextSteps;
      });

      // Gestion des erreurs
      if (event === "ERROR") {
        setHasError(true);
        setErrorDetails(details || "Une erreur est survenue durant le traitement.");
        
        // Marquer l'étape en cours en échec
        setSteps((prevSteps) => {
          const nextSteps = { ...prevSteps };
          Object.keys(nextSteps).forEach((key) => {
            if (nextSteps[key].status === "running") {
              nextSteps[key].status = "failed";
              nextSteps[key].details = details;
            }
          });
          return nextSteps;
        });

        // Ajouter une notification toast d'erreur
        addNotification("error", `Échec du traitement : ${details}`);
      }

      // Notification de complétion d'étapes
      if (event.endsWith("_COMPLETED")) {
        addNotification("success", `Étape validée : ${step}`);
      }
    };

    // Abonnement global à tous les messages
    const unsubscribe = subscribe("*", handleProgress);

    return () => {
      unsubscribe();
    };
  }, [meetingId, subscribe]);

  const addNotification = (type, message) => {
    const newNotif = {
      id: Math.random().toString(36).substr(2, 9),
      type,
      message,
      timestamp: new Date(),
    };
    setNotifications((prev) => [newNotif, ...prev].slice(0, 10)); // Garder les 10 dernières
  };

  const clearNotifications = () => setNotifications([]);

  // Calcul du pourcentage global de progression
  const totalPercent = Math.round(
    Object.values(steps).reduce((acc, step) => acc + (step.percent ?? 0), 0) / 3
  );

  // Déterminer l'étape active actuelle
  let currentStep = "En attente...";
  if (steps.transcription.status === "running") currentStep = "Transcription...";
  else if (steps.summary.status === "running") currentStep = "Analyse sémantique (NLP)...";
  else if (steps.embedding.status === "running") currentStep = "Génération des index vectoriels (RAG)...";
  else if (isComplete) currentStep = "Traitement terminé avec succès";

  return {
    steps,
    totalPercent,
    currentStep,
    isComplete,
    hasError,
    errorDetails,
    notifications,
    clearNotifications,
    isConnected,
  };
};
export default useMeetingProgress;
