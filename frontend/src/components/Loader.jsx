import React from "react";

/**
 * Spinner de chargement global ou local.
 * 
 * @param {boolean} fullPage - Si vrai, affiche le loader au centre de l'écran en plein écran.
 */
const Loader = ({ fullPage = false }) => {
  return (
    <div className={`loader-container ${fullPage ? "loader-fullscreen" : ""}`}>
      <div className="spinner"></div>
    </div>
  );
};

export default Loader;
