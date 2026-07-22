import React from "react";
import Button from "./Button";
import Card from "./Card";
import { AlertOctagon, RefreshCw, Home } from "lucide-react";

/**
 * Composant ErrorBoundary pour intercepter les plantages React en production
 * et proposer une interface de récupération élégante.
 */
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    // Met à jour l'état pour afficher l'UI alternative au prochain rendu.
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("[ErrorBoundary] Erreur non gérée interceptée :", error, errorInfo);
  }

  handleReload = () => {
    window.location.reload();
  };

  handleGoHome = () => {
    window.location.href = "/";
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="not-found-page flex items-center justify-center min-h-screen p-4 bg-tertiary">
          <div className="not-found-card text-center max-w-lg">
            <div className="not-found-icon flex justify-center mb-4">
              <AlertOctagon size={48} className="icon-red text-red-500 animate-pulse" />
            </div>
            <h1 className="text-2xl font-bold mb-2">Une erreur est survenue</h1>
            <p className="text-secondary mb-6 text-sm">
              L'application a rencontré un problème inattendu lors de l'affichage de ce composant. 
              Vos données de session sont préservées.
            </p>
            {this.state.error && (
              <div className="error-details-box text-left p-3 mb-6 bg-black border border-gray-800 rounded font-mono text-xs text-red-400 overflow-x-auto max-h-32">
                {this.state.error.toString()}
              </div>
            )}
            <div className="flex gap-4 justify-center">
              <Button onClick={this.handleReload} variant="primary" className="flex items-center gap-1">
                <RefreshCw size={16} />
                <span>Recharger</span>
              </Button>
              <Button onClick={this.handleGoHome} variant="secondary" className="flex items-center gap-1">
                <Home size={16} />
                <span>Retour Accueil</span>
              </Button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
