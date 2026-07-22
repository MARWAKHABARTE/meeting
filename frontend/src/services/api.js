import axios from "axios";

// L'URL du backend utilise désormais un chemin relatif (/api) géré par
// le Reverse Proxy Nginx. Plus aucune adresse absolue n'est exposée.
const BACKEND_URL = "/api";

const api = axios.create({
  baseURL: BACKEND_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export const checkHealth = async () => {
  const response = await api.get("/health");
  return response.data;
};

export const getMe = async (token) => {
  const response = await api.get("/api/v1/auth/me", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return response.data;
};

export default api;
