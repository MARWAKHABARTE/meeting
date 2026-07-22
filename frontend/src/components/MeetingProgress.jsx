import React from "react";
import { useMeetingProgress } from "../hooks/useMeetingProgress";

/**
 * Composant de suivi de progression temps réel de l'analyse d'une réunion.
 * Idéal pour être incrusté dans le Dashboard ou l'écran de traitement.
 * @param {object} props
 * @param {string} props.meetingId - ID de la réunion à écouter.
 */
export const MeetingProgress = ({ meetingId }) => {
  const {
    steps,
    totalPercent,
    currentStep,
    isComplete,
    hasError,
    errorDetails,
    isConnected,
  } = useMeetingProgress(meetingId);

  if (!meetingId) {
    return (
      <div style={styles.emptyContainer}>
        Sélectionnez une réunion pour suivre son avancement.
      </div>
    );
  }

  return (
    <div style={styles.card}>
      <div style={styles.header}>
        <div>
          <h3 style={styles.title}>Statut de l'analyse</h3>
          <p style={styles.subtitle}>{currentStep}</p>
        </div>
        <div style={styles.percentBadge}>{totalPercent}%</div>
      </div>

      {/* Barre de progression globale */}
      <div style={styles.progressTrack}>
        <div
          style={{
            ...styles.progressBar,
            width: `${totalPercent}%`,
            ...(hasError ? styles.progressBarError : {}),
            ...(isComplete ? styles.progressBarSuccess : {}),
          }}
        />
      </div>

      {/* Liste des étapes détaillées */}
      <div style={styles.stepsList}>
        {Object.entries(steps).map(([key, step]) => (
          <div key={key} style={styles.stepItem}>
            <div style={styles.stepHeader}>
              <span style={styles.stepLabel}>{step.label}</span>
              <span
                style={{
                  ...styles.statusBadge,
                  ...styles[`status_${step.status}`],
                }}
              >
                {step.status === "completed" && "Terminé"}
                {step.status === "running" && `${step.percent}%`}
                {step.status === "pending" && "En attente"}
                {step.status === "failed" && "Échec"}
              </span>
            </div>
            {step.details && <p style={styles.stepDetails}>{step.details}</p>}
          </div>
        ))}
      </div>

      {hasError && (
        <div style={styles.errorAlert}>
          <span style={styles.errorIcon}>⚠️</span>
          <div>
            <div style={styles.errorTitle}>Erreur d'analyse</div>
            <div style={styles.errorText}>{errorDetails}</div>
          </div>
        </div>
      )}
    </div>
  );
};

const styles = {
  emptyContainer: {
    padding: "24px",
    borderRadius: "12px",
    background: "rgba(255, 255, 255, 0.02)",
    border: "1px dashed rgba(255, 255, 255, 0.1)",
    textAlign: "center",
    color: "rgba(255, 255, 255, 0.4)",
    fontSize: "14px",
    fontFamily: "'Inter', sans-serif",
  },
  card: {
    background: "rgba(15, 23, 42, 0.6)", // Slate 900 semi-transparent
    backdropFilter: "blur(20px)",
    border: "1px solid rgba(255, 255, 255, 0.08)",
    borderRadius: "16px",
    padding: "24px",
    boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.3)",
    fontFamily: "'Inter', sans-serif",
    color: "#fff",
    maxWidth: "500px",
    width: "100%",
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-start",
    marginBottom: "16px",
  },
  title: {
    margin: 0,
    fontSize: "16px",
    fontWeight: 600,
    letterSpacing: "-0.025em",
  },
  subtitle: {
    margin: "4px 0 0 0",
    fontSize: "13px",
    color: "rgba(255, 255, 255, 0.6)",
  },
  percentBadge: {
    fontSize: "24px",
    fontWeight: 700,
    color: "#3b82f6", // Bleu vibrant
    fontVariantNumeric: "tabular-nums",
  },
  progressTrack: {
    height: "6px",
    background: "rgba(255, 255, 255, 0.08)",
    borderRadius: "3px",
    overflow: "hidden",
    marginBottom: "24px",
  },
  progressBar: {
    height: "100%",
    background: "linear-gradient(90deg, #3b82f6, #60a5fa)",
    borderRadius: "3px",
    transition: "width 0.5s cubic-bezier(0.4, 0, 0.2, 1)",
  },
  progressBarSuccess: {
    background: "linear-gradient(90deg, #10b981, #34d399)",
  },
  progressBarError: {
    background: "linear-gradient(90deg, #ef4444, #f87171)",
  },
  stepsList: {
    display: "flex",
    flexDirection: "column",
    gap: "16px",
  },
  stepItem: {
    padding: "12px",
    borderRadius: "8px",
    background: "rgba(255, 255, 255, 0.02)",
    border: "1px solid rgba(255, 255, 255, 0.04)",
  },
  stepHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  },
  stepLabel: {
    fontSize: "13px",
    fontWeight: 500,
  },
  statusBadge: {
    fontSize: "11px",
    fontWeight: 600,
    padding: "2px 8px",
    borderRadius: "12px",
    textTransform: "uppercase",
    letterSpacing: "0.5px",
  },
  status_pending: {
    background: "rgba(255, 255, 255, 0.05)",
    color: "rgba(255, 255, 255, 0.4)",
  },
  status_running: {
    background: "rgba(59, 130, 246, 0.15)",
    color: "#60a5fa",
  },
  status_completed: {
    background: "rgba(16, 185, 129, 0.15)",
    color: "#34d399",
  },
  status_failed: {
    background: "rgba(239, 68, 68, 0.15)",
    color: "#f87171",
  },
  stepDetails: {
    margin: "6px 0 0 0",
    fontSize: "11px",
    color: "rgba(255, 255, 255, 0.5)",
  },
  errorAlert: {
    display: "flex",
    gap: "12px",
    marginTop: "20px",
    padding: "12px 16px",
    background: "rgba(239, 68, 68, 0.1)",
    border: "1px solid rgba(239, 68, 68, 0.2)",
    borderRadius: "8px",
  },
  errorIcon: {
    fontSize: "18px",
    alignSelf: "flex-start",
  },
  errorTitle: {
    fontSize: "13px",
    fontWeight: 600,
    color: "#ef4444",
  },
  errorText: {
    fontSize: "11px",
    color: "rgba(255, 255, 255, 0.7)",
    marginTop: "2px",
  },
};

export default MeetingProgress;
