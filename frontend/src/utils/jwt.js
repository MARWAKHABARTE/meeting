/**
 * Décode le payload d'un jeton JWT.
 * Permet de récupérer les informations de l'utilisateur et ses rôles côté client.
 * 
 * @param {string} token - Le jeton JWT encodé
 * @returns {object|null} Le payload décodé ou null en cas d'erreur
 */
export const decodeToken = (token) => {
  if (!token) return null;
  try {
    const base64Url = token.split(".")[1];
    if (!base64Url) return null;
    const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split("")
        .map((c) => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2))
        .join("")
    );
    return JSON.parse(jsonPayload);
  } catch (error) {
    console.error("Erreur lors du décodage du token JWT:", error);
    return null;
  }
};
