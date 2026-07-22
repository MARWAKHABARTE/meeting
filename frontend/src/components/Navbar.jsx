import React from "react";
import { useAuth } from "../hooks/useAuth";
import { LogOut, User as UserIcon } from "lucide-react";
import ConnectionStatus from "./ConnectionStatus";

/**
 * Barre supérieure de l'application connectée.
 */
const Navbar = () => {
  const { user, logout } = useAuth();

  return (
    <header className="navbar">
      <div className="navbar-left">
        <span className="navbar-subtitle">Espace Collaborateur</span>
        <ConnectionStatus />
      </div>

      <div className="navbar-right">
        {user && (
          <div className="user-profile-widget">
            <UserIcon size={18} className="profile-icon" />
            <div className="user-info">
              <span className="user-name">{user.displayName}</span>
              <span className="user-email">{user.email}</span>
            </div>
          </div>
        )}
        
        <button className="btn-logout" onClick={logout} title="Se déconnecter">
          <LogOut size={18} />
          <span>Déconnexion</span>
        </button>
      </div>
    </header>
  );
};

export default Navbar;
