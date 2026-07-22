import React from "react";
import { useAuth } from "../hooks/useAuth";
import Card from "../components/Card";
import Button from "../components/Button";
import { Shield, User, Settings as SettingsIcon } from "lucide-react";

/**
 * Page des paramètres de profil de l'utilisateur (données réelles et factices).
 */
const Settings = () => {
  const { user, roles, token } = useAuth();

  return (
    <div className="settings-page">
      <div className="page-header">
        <h1 className="page-title">Paramètres</h1>
        <p className="page-description">
          Gérez vos préférences utilisateur et consultez vos droits d'accès.
        </p>
      </div>

      <div className="settings-grid">
        <Card title="Informations de Profil" icon={<User size={20} className="icon-blue" />}>
          <div className="profile-details">
            <div className="detail-item">
              <span className="detail-label">Nom Complet</span>
              <span className="detail-value">{user?.displayName || "Non renseigné"}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Identifiant Unique</span>
              <span className="detail-value"><code>{user?.id || "N/A"}</code></span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Adresse e-mail</span>
              <span className="detail-value">{user?.email}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Statut Administrateur</span>
              <span className="detail-value">{user?.is_superuser ? "Oui (Superuser)" : "Non"}</span>
            </div>
          </div>
        </Card>

        <Card title="Habilitations & Rôles (Keycloak)" icon={<Shield size={20} className="icon-green" />}>
          <div className="roles-details">
            <p className="description-text">Rôles extraits dynamiquement de votre jeton JWT Keycloak :</p>
            <div className="roles-tags mt-2">
              {roles.length > 0 ? (
                roles.map((role) => (
                  <span key={role} className="role-tag">
                    {role}
                  </span>
                ))
              ) : (
                <span className="no-roles">Aucun rôle affecté</span>
              )}
            </div>
            <div className="info-badge mt-4">
              ℹ️ <strong>Rôles applicatifs :</strong> Ces rôles déterminent vos droits d'écriture et de suppression sur les ressources des prochains sprints.
            </div>
          </div>
        </Card>
      </div>

      <div className="mt-6">
        <Card title="Sécurité et Jeton d'accès (Développement)" icon={<SettingsIcon size={20} className="icon-purple" />}>
          <div className="token-viewer">
            <label className="detail-label">Jeton JWT Actif</label>
            <textarea 
              className="token-textarea" 
              readOnly 
              value={token || ""} 
              rows={4}
              onClick={(e) => e.target.select()}
            />
            <p className="help-text">Cliquez dans la zone de texte pour tout sélectionner et copier le jeton.</p>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default Settings;
