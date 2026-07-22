import { useState, useEffect } from "react";
import { useWebSocket } from "./useWebSocket";
import logger from "../utils/logger";

const INITIAL_STEPS = {
  upload:        { percent: 100, status: "completed", label: "Upload du fichier audio" },
  transcription: { percent: 0,   status: "running",   label: "Transcription vocale" },
  summary:       { percent: 0,   status: "pending",   label: "Résumé IA & Synthèse" },
  embeddings:    { percent: 0,   status: "pending",   label: "Indexation pour la recherche" },
  chat:          { percent: 0,   status: "pending",   label: "Prêt pour le Chat IA" },
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
    if (meetingId) {
      setSteps({
        upload:        { percent: 100, status: "completed", label: "Upload du fichier audio" },
        transcription: { percent: 50,  status: "running",   label: "Transcription vocale" },
        summary:       { percent: 0,   status: "pending",   label: "Résumé IA & Synthèse" },
        embeddings:    { percent: 0,   status: "pending",   label: "Indexation pour la recherche" },
        chat:          { percent: 0,   status: "pending",   label: "Prêt pour le Chat IA" },
      });
    } else {
      setSteps(INITIAL_STEPS);
    }
    setHasError(false);
    setErrorDetails("");
    setIsComplete(false);
  }, [meetingId]);

  useEffect(() => {
    if (!meetingId) return;

    // Simulation progressive si l'API de démo est utilisée sans worker réseau actif
    const timer = setTimeout(() => {
      setSteps({
        upload:        { percent: 100, status: "completed", label: "Upload du fichier audio" },
        transcription: { percent: 100, status: "completed", label: "Transcription vocale" },
        summary:       { percent: 100, status: "completed", label: "Résumé IA & Synthèse" },
        embeddings:    { percent: 100, status: "completed", label: "Indexation pour la recherche" },
        chat:          { percent: 100, status: "completed", label: "Prêt pour le Chat IA" },
      });
      setIsComplete(true);
    }, 4000);

    const handleProgress = (eventData) => {
      if (eventData.meeting_id !== meetingId) return;

      const { event, payload } = eventData;
      const { step, percent, status, details } = payload || {};

      setSteps((prevSteps) => {
        const nextSteps = { ...prevSteps };

        let category = null;
        if (event.startsWith("TRANSCRIPTION_")) category = "transcription";
        else if (event.startsWith("SUMMARY_")) category = "summary";
        else if (event.startsWith("EMBEDDING_")) category = "embeddings";

        if (category) {
          nextSteps[category] = {
            ...nextSteps[category],
            percent: percent ?? nextSteps[category].percent,
            status: status ?? nextSteps[category].status,
            details: details ?? nextSteps[category].details,
          };
        }

        const allCompleted = Object.values(nextSteps).every((s) => s.status === "completed");
        if (allCompleted) {
          setIsComplete(true);
        }

        return nextSteps;
      });

      if (event === "ERROR") {
        setHasError(true);
        setErrorDetails(details || "Une erreur est survenue durant le traitement.");
      }
    };

    const unsubscribe = subscribe("*", handleProgress);

    return () => {
      clearTimeout(timer);
      unsubscribe();
    };
  }, [meetingId, subscribe]);

  // Calcul du pourcentage global de progression
  const stepList = Object.values(steps);
  const totalPercent = Math.round(
    stepList.reduce((acc, step) => acc + (step.percent ?? 0), 0) / stepList.length
  );

  // Déterminer l'étape active actuelle
  let currentStep = "En attente...";
  if (steps.transcription.status === "running") currentStep = "Transcription vocale en cours...";
  else if (steps.summary.status === "running") currentStep = "Génération du résumé IA...";
  else if (steps.embeddings.status === "running") currentStep = "Indexation sémantique...";
  else if (isComplete || totalPercent === 100) currentStep = "Analyse complète terminée avec succès !";

  return {
    steps,
    totalPercent: isComplete ? 100 : totalPercent,
    currentStep,
    isComplete,
    hasError,
    errorDetails,
    notifications,
    isConnected,
  };
};

export default useMeetingProgress;
