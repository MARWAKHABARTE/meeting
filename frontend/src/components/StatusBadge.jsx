import React from "react";

const STATUS_CONFIG = {
  pending:    { label: "En attente",    className: "badge-warning" },
  processing: { label: "En cours",      className: "badge-info" },
  completed:  { label: "Terminé",       className: "badge-success" },
  failed:     { label: "Échoué",        className: "badge-danger" },
  queued:     { label: "En file",       className: "badge-info" },
  running:    { label: "En cours",      className: "badge-info" },
  success:    { label: "Succès",        className: "badge-success" },
  error:      { label: "Erreur",        className: "badge-danger" },
  online:     { label: "En ligne",      className: "badge-success" },
  offline:    { label: "Hors ligne",    className: "badge-danger" },
  degraded:   { label: "Dégradé",       className: "badge-warning" },
};

/**
 * Badge de statut typé et configurable.
 */
export const StatusBadge = ({ status = "pending", customLabel = null }) => {
  const config = STATUS_CONFIG[status?.toLowerCase()] || {
    label: status,
    className: "badge-default",
  };

  return (
    <span className={`status-badge ${config.className}`} aria-label={`Statut : ${config.label}`}>
      <span className="status-dot" />
      {customLabel || config.label}
    </span>
  );
};

export default StatusBadge;
