import React from "react";
import { useMeetingProgress } from "../hooks/useMeetingProgress";
import { CheckCircle2, Loader2, Circle, AlertCircle } from "lucide-react";

/**
 * Composant de suivi de la progression métier d'une réunion en cours d'analyse.
 * Masque toute référence à l'infrastructure technique.
 */
export const MeetingProgress = ({ meetingId }) => {
  const {
    steps,
    totalPercent,
    currentStep,
    isComplete,
    hasError,
    errorDetails,
  } = useMeetingProgress(meetingId);

  // Mappage des étapes utilisateur sans jargon d'infrastructure
  const businessSteps = [
    { key: "upload",        label: "Upload du fichier audio" },
    { key: "transcription", label: "Transcription vocale" },
    { key: "summary",       label: "Résumé IA & Synthèse" },
    { key: "embeddings",    label: "Indexation pour la recherche" },
    { key: "chat",          label: "Prêt pour le Chat IA" },
  ];

  if (!meetingId) {
    return (
      <div className="progress-empty-state">
        <span>Aucune analyse de réunion en cours.</span>
      </div>
    );
  }

  return (
    <div className="business-progress-card">
      <div className="progress-card-header">
        <div>
          <h3 className="progress-card-title">Analyse en cours</h3>
          <p className="progress-card-step">Étape actuelle : {currentStep}</p>
        </div>
        <div className="progress-percent-badge">{totalPercent}%</div>
      </div>

      {/* Barre de progression globale */}
      <div className="progress-track">
        <div
          className={`progress-bar-fill ${hasError ? "progress-bar-error" : isComplete ? "progress-bar-complete" : ""}`}
          style={{ width: `${totalPercent}%` }}
        />
      </div>

      {/* Liste des étapes métier */}
      <div className="business-steps-list">
        {businessSteps.map((bStep) => {
          const stepInfo = steps[bStep.key] || {};
          const status = stepInfo.status || "pending";

          return (
            <div key={bStep.key} className={`step-row step-row-${status}`}>
              <div className="step-status-icon">
                {status === "completed" && <CheckCircle2 size={16} className="text-success" />}
                {status === "running" && <Loader2 size={16} className="spin text-primary" />}
                {status === "pending" && <Circle size={16} className="text-muted" />}
                {status === "failed" && <AlertCircle size={16} className="text-danger" />}
              </div>
              <span className="step-label-text">{bStep.label}</span>
              <span className="step-status-badge">
                {status === "completed" && "Terminé"}
                {status === "running" && "En cours"}
                {status === "pending" && "En attente"}
                {status === "failed" && "Interrompu"}
              </span>
            </div>
          );
        })}
      </div>

      {hasError && (
        <div className="progress-error-banner">
          <AlertCircle size={18} />
          <div>
            <strong>Analyse interrompue</strong>
            <p>Une erreur est survenue lors du traitement. Veuillez réessayer.</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default MeetingProgress;
