import { useContext } from "react";
import { AuthContext } from "../context/AuthContext";

/**
 * Hook personnalisé pour accéder facilement au contexte d'authentification.
 * 
 * @returns {object} Les propriétés et méthodes du contexte d'authentification
 */
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth doit être utilisé à l'intérieur d'un AuthProvider");
  }
  return context;
};
