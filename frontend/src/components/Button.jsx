import React from "react";

/**
 * Bouton réutilisable et stylisé.
 * 
 * @param {string} type - Le type HTML du bouton (button, submit, reset)
 * @param {string} variant - Le style du bouton (primary, secondary, danger, outline)
 * @param {boolean} loading - Indique si le bouton est en état de chargement
 * @param {boolean} disabled - Indique si le bouton est désactivé
 * @param {function} onClick - Le callback au clic
 * @param {React.ReactNode} children - Le contenu du bouton
 */
const Button = ({
  type = "button",
  variant = "primary",
  loading = false,
  disabled = false,
  onClick,
  children,
  className = "",
  ...props
}) => {
  return (
    <button
      type={type}
      className={`btn btn-${variant} ${loading ? "btn-loading" : ""} ${className}`}
      disabled={disabled || loading}
      onClick={onClick}
      {...props}
    >
      {loading ? (
        <span className="btn-spinner-container">
          <span className="btn-spinner"></span>
          <span>Chargement...</span>
        </span>
      ) : (
        children
      )}
    </button>
  );
};

export default Button;
