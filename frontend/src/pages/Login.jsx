import React, { useState, useEffect, useRef } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import Button from "../components/Button";

/**
 * Formulaire de connexion personnalisé connecté à Keycloak.
 * Entièrement accessible et conforme WCAG.
 */
const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const { login, error, loading } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const errorRef = useRef(null);

  // Redirection d'origine par défaut
  const from = location.state?.from?.pathname || "/dashboard";

  // Mettre le focus sur l'alerte d'erreur lorsqu'elle apparaît
  useEffect(() => {
    if (error && errorRef.current) {
      errorRef.current.focus();
    }
  }, [error]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) return;

    const success = await login(email, password);
    if (success) {
      navigate(from, { replace: true });
    }
  };

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-header">
          <h1 className="logo-text">MEETING AI</h1>
          <p className="login-subtitle">Plateforme d'analyse intelligente de réunions</p>
        </div>

        <form 
          onSubmit={handleSubmit} 
          className="login-form"
          aria-busy={loading}
        >
          <div className="form-group">
            <label htmlFor="email">Adresse e-mail</label>
            <input
              id="email"
              type="email"
              placeholder="votre.nom@domaine.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              disabled={loading}
              aria-required="true"
              aria-invalid={!!error}
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Mot de passe</label>
            <input
              id="password"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={loading}
              aria-required="true"
              aria-invalid={!!error}
            />
          </div>

          {error && (
            <div 
              ref={errorRef}
              className="login-error-alert"
              role="alert"
              aria-live="assertive"
              tabIndex={-1} // Permet de mettre le focus par programmation
              style={{ outline: "none" }}
            >
              <span>⚠️ {error}</span>
            </div>
          )}

          <Button 
            type="submit" 
            variant="primary" 
            loading={loading} 
            className="w-full"
            aria-disabled={loading}
          >
            Se connecter
          </Button>
        </form>

        <div className="login-footer">
          <p>Supervisé par <strong>Keycloak OpenID Connect</strong></p>
          <p className="credentials-hint">Utilisateur de test : <code>khabaratemarwa@gmail.com</code> / <code>marwakh</code></p>
        </div>
      </div>
    </div>
  );
};

export default Login;
