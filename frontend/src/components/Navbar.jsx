import React from "react";
import { useAuth } from "../hooks/useAuth";
import { LogOut, User as UserIcon, Bell } from "lucide-react";
import ConnectionStatus from "./ConnectionStatus";
import NotificationCenter from "./NotificationCenter";

/**
 * Barre supérieure professionnelle de l'application.
 */
const Navbar = () => {
  const { user, logout } = useAuth();

  return (
    <header className="navbar">
      {/* WebSocket actif en arrière-plan sans rendu UI */}
      <ConnectionStatus />
      
      {/* Toasts de notifications */}
      <NotificationCenter />

      <div className="navbar-left">
        <span className="navbar-title">Espace d'Analyse Intelligent</span>
      </div>

      <div className="navbar-right">
        {user && (
          <div className="user-profile-widget">
            <div className="avatar-circle">
              <UserIcon size={16} />
            </div>
            <div className="user-info">
              <span className="user-name">{user.displayName || user.email}</span>
              <span className="user-role">
                {user.is_superuser ? "Administrateur" : "Collaborateur"}
              </span>
            </div>
          </div>
        )}

        <button className="btn-logout" onClick={logout} title="Se déconnecter">
          <LogOut size={16} />
          <span>Déconnexion</span>
        </button>
      </div>
    </header>
  );
};

export default Navbar;
