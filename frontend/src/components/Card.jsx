import React from "react";

/**
 * Carte réutilisable pour structurer l'affichage.
 * 
 * @param {string} title - Le titre de la carte
 * @param {string} subtitle - Le sous-titre de la carte
 * @param {React.ReactNode} icon - Icône à afficher en haut à droite
 * @param {string} footer - Texte ou contenu de pied de page
 * @param {React.ReactNode} children - Contenu principal de la carte
 */
const Card = ({ title, subtitle, icon, footer, children, className = "" }) => {
  return (
    <div className={`card ${className}`}>
      {(title || icon) && (
        <div className="card-header">
          <div>
            {title && <h4 className="card-title">{title}</h4>}
            {subtitle && <p className="card-subtitle">{subtitle}</p>}
          </div>
          {icon && <div className="card-icon">{icon}</div>}
        </div>
      )}
      <div className="card-body">{children}</div>
      {footer && <div className="card-footer">{footer}</div>}
    </div>
  );
};

export default Card;
