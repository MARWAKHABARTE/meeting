import React from "react";
import { Link } from "react-router-dom";
import { AlertCircle } from "lucide-react";

/**
 * Page d'erreur 404.
 */
const NotFound = () => {
  return (
    <div className="not-found-page">
      <div className="not-found-card">
        <AlertCircle size={64} className="not-found-icon" />
        <h1>404 - Page non trouvée</h1>
        <p>La page que vous essayez d'atteindre n'existe pas ou vous n'avez pas l'autorisation d'y accéder.</p>
        <Link to="/dashboard" className="btn btn-primary mt-4">
          Retourner au Dashboard
        </Link>
      </div>
    </div>
  );
};

export default NotFound;
