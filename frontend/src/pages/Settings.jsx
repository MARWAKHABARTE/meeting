import React, { useState } from "react";
import { useAuth } from "../hooks/useAuth";
import Card from "../components/Card";
import { Shield, User, Settings as SettingsIcon, Users, Plus, Search, Check, Lock } from "lucide-react";

/**
 * Page des paramètres de profil et de gestion des utilisateurs pour les administrateurs.
 */
const Settings = () => {
  const { user, roles, token } = useAuth();
  const [userSearch, setUserSearch] = useState("");

  // Exemple d'utilisateurs de l'entreprise (gérés via Keycloak / Postgres)
  const [workspaceUsers, setWorkspaceUsers] = useState([
    { id: "1", username: "admin", name: "Admin System", email: "admin@meeting-ai.com", role: "Administrateur", status: "actif" },
    { id: "2", username: "testuser", name: "Test User", email: "user@meeting-ai.com", role: "Collaborateur", status: "actif" },
    { id: "3", username: "m.dupont", name: "Marc Dupont", email: "m.dupont@company.com", role: "Manager", status: "actif" },
    { id: "4", username: "s.martin", name: "Sophie Martin", email: "s.martin@company.com", role: "Collaborateur", status: "inactif" },
  ]);

  const filteredUsers = workspaceUsers.filter(
    (u) =>
      u.name.toLowerCase().includes(userSearch.toLowerCase()) ||
      u.email.toLowerCase().includes(userSearch.toLowerCase()) ||
      u.role.toLowerCase().includes(userSearch.toLowerCase())
  );

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1 className="page-title">Paramètres & Compte</h1>
          <p className="page-description">
            Gérez vos préférences de profil, vos habilitations et la gestion des utilisateurs d'équipe.
          </p>
        </div>
      </div>

      {/* Section 1 : Gestion des utilisateurs (Réservé aux Administrateurs) */}
      {user?.is_superuser && (
        <div className="card-saas mb-6 border-amber">
          <div className="card-saas-header flex-between">
            <div>
              <h2 className="card-saas-title text-amber">
                <Users size={20} />
                Gestion des Utilisateurs (Espace Administrateur)
              </h2>
              <p className="card-saas-subtitle">
                Gérez les accès des collaborateurs de votre organisation.
              </p>
            </div>
            <button className="btn btn-primary btn-sm">
              <Plus size={16} />
              <span>Ajouter un utilisateur</span>
            </button>
          </div>

          {/* Filtre de recherche */}
          <div className="mb-4 flex-between gap-4">
            <div className="search-wrapper flex-1">
              <Search size={16} className="search-icon" />
              <input
                type="text"
                className="search-input"
                placeholder="Rechercher un utilisateur par nom, email ou rôle..."
                value={userSearch}
                onChange={(e) => setUserSearch(e.target.value)}
              />
            </div>
          </div>

          <div className="table-responsive">
            <table className="saas-table">
              <thead>
                <tr>
                  <th>Utilisateur</th>
                  <th>Email</th>
                  <th>Rôle Applicatif</th>
                  <th>Statut</th>
                  <th className="text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredUsers.map((u) => (
                  <tr key={u.id}>
                    <td className="font-semibold text-white">{u.name}</td>
                    <td className="text-muted">{u.email}</td>
                    <td>
                      <span
                        className={`role-badge ${
                          u.role === "Administrateur"
                            ? "role-admin"
                            : u.role === "Manager"
                            ? "role-manager"
                            : "role-user"
                        }`}
                      >
                        {u.role}
                      </span>
                    </td>
                    <td>
                      <span className={`status-pill status-${u.status}`}>
                        {u.status === "actif" ? "Actif" : "Inactif"}
                      </span>
                    </td>
                    <td className="text-right">
                      <button className="btn btn-xs btn-secondary">Éditer</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Section 2 : Profil & Habilitations */}
      <div className="dashboard-content-grid">
        <div className="card-saas">
          <div className="card-saas-header">
            <h2 className="card-saas-title">
              <User size={18} className="text-primary" />
              Informations de Profil
            </h2>
          </div>
          <div className="profile-details-stack">
            <div className="detail-row">
              <span className="detail-label">Nom Utilisateur</span>
              <span className="detail-val">{user?.displayName || "Non renseigné"}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Adresse e-mail</span>
              <span className="detail-val">{user?.email}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Niveau d'Accès</span>
              <span className="detail-val text-primary font-semibold">
                {user?.is_superuser ? "Administrateur Système" : "Collaborateur Équipe"}
              </span>
            </div>
          </div>
        </div>

        <div className="card-saas">
          <div className="card-saas-header">
            <h2 className="card-saas-title">
              <Shield size={18} className="text-success" />
              Droits d'Accès
            </h2>
          </div>
          <div className="roles-details">
            <p className="card-saas-subtitle mb-3">Rôles de votre compte :</p>
            <div className="roles-tags">
              {roles && roles.length > 0 ? (
                roles.map((role) => (
                  <span key={role} className="role-tag">
                    {role}
                  </span>
                ))
              ) : (
                <span className="role-tag">user</span>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;
