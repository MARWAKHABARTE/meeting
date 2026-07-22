import React from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import Loader from "./Loader";

/**
 * Garde de route (Route Guard) qui restreint l'accès aux utilisateurs authentifiés.
 * Si l'utilisateur n'est pas connecté, il est renvoyé vers la page de connexion.
 * Si des rôles spécifiques sont requis, il valide la possession de ceux-ci.
 * 
 * @param {React.ReactNode} children - Le composant ou la page à protéger
 * @param {Array<string>} requiredRoles - Rôles autorisés à accéder à la route (facultatif)
 */
const ProtectedRoute = ({ children, requiredRoles = [] }) => {
  const { isAuthenticated, loading, roles } = useAuth();
  const location = useLocation();

  // Affichage d'un écran de chargement le temps de valider le jeton/charger le profil
  if (loading) {
    return <Loader fullPage />;
  }

  // Redirection vers le login si non connecté
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Vérification facultative des privilèges d'accès
  if (requiredRoles.length > 0) {
    const hasRequiredRole = requiredRoles.some((role) => roles.includes(role));
    if (!hasRequiredRole) {
      // Redirection si l'utilisateur n'a pas les droits requis
      return <Navigate to="/unauthorized" replace />;
    }
  }

  return children;
};

export default ProtectedRoute;
