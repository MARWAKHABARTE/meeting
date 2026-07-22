import logger from "../utils/logger";

class WebSocketService {
  constructor() {
    this.socket = null;
    this.listeners = new Map(); // eventType -> Set of callbacks
    this.reconnectAttempts = 0;
    this.reconnectTimeoutId = null;
    this.isConnected = false;
    this.token = null;
    this.meetingId = null;
  }

  /**
   * Initialise et ouvre la connexion WebSocket.
   * @param {string} token - JWT Token de l'utilisateur.
   * @param {string|null} meetingId - Optionnel, ID de la réunion à écouter.
   */
  connect(token, meetingId = null) {
    if (!token) {
      logger.error("[WebSocket Service] Impossible de se connecter sans token.");
      return;
    }

    this.token = token;
    this.meetingId = meetingId;

    // Fermeture de l'ancienne connexion si existante
    if (this.socket) {
      this.disconnect();
    }

    // Détermination de l'URL cible (utilisation de la même origine ou fallback port 8000)
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const host = window.location.host;
    
    // Si nous sommes en développement direct avec Vite (port 5173), on cible l'API sur 8000.
    // Si nous sommes derrière Nginx (port 80), window.location.host sera correct.
    const wsHost = host.includes("5173") || host.includes("3000") ? "localhost:8000" : host;
    const meetingPath = meetingId ? `/${meetingId}` : "";
    const wsUrl = `${protocol}//${wsHost}/api/v1/ws${meetingPath}?token=${token}`;

    logger.info(`[WebSocket Service] Tentative de connexion sur : ${wsUrl}`);
    
    try {
      this.socket = new WebSocket(wsUrl);

      this.socket.onopen = () => {
        logger.info("[WebSocket Service] Connexion établie avec succès.");
        this.isConnected = true;
        this.reconnectAttempts = 0;
        this._triggerEvent("CONNECTION_STATUS", { connected: true });
      };

      this.socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          logger.debug("[WebSocket Service] Événement reçu :", data);
          
          if (data.event === "HEARTBEAT") {
            // Heartbeat serveur reçu, pas de dispatch nécessaire sauf pour debugging
            return;
          }
          
          // Dispatch de l'événement vers les écouteurs concernés
          this._triggerEvent(data.event, data);
          // Dispatch général pour tous les messages
          this._triggerEvent("*", data);
        } catch (e) {
          logger.error("[WebSocket Service] Erreur de parsing du message :", e);
        }
      };

      this.socket.onclose = (event) => {
        this.isConnected = false;
        this._triggerEvent("CONNECTION_STATUS", { connected: false });
        
        // Fermeture volontaire (code 1000) vs anormale
        if (event.code !== 1000) {
          logger.warn(`[WebSocket Service] Connexion fermée anormalement (code: ${event.code}). Tentative de reconnexion...`);
          this._scheduleReconnect();
        } else {
          logger.info("[WebSocket Service] Connexion fermée proprement.");
        }
      };

      this.socket.onerror = (error) => {
        logger.error("[WebSocket Service] Erreur sur le socket :", error);
      };

    } catch (e) {
      logger.error("[WebSocket Service] Erreur d'initialisation de WebSocket :", e);
      this._scheduleReconnect();
    }
  }

  /**
   * Ferme proprement la connexion WebSocket.
   */
  disconnect() {
    this._clearReconnect();
    if (this.socket) {
      // 1000 = Fermeture normale
      this.socket.close(1000, "Déconnexion volontaire de l'application");
      this.socket = null;
    }
    this.isConnected = false;
  }

  /**
   * S'abonne à un type d'événement WebSocket.
   * @param {string} eventType - Type d'événement (ex: 'TRANSCRIPTION_PROGRESS') ou '*' pour tous.
   * @param {Function} callback - Fonction appelée lors de la réception.
   * @returns {Function} Fonction pour se désabonner.
   */
  subscribe(eventType, callback) {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, new Set());
    }
    this.listeners.get(eventType).add(callback);

    // Retourne une fonction de nettoyage pour se désabonner facilement
    return () => {
      const list = this.listeners.get(eventType);
      if (list) {
        list.delete(callback);
        if (list.size === 0) {
          this.listeners.delete(eventType);
        }
      }
    };
  }

  _triggerEvent(eventType, payload) {
    const list = this.listeners.get(eventType);
    if (list) {
      list.forEach((cb) => {
        try {
          cb(payload);
        } catch (err) {
          logger.error(`[WebSocket Service] Erreur dans le callback pour '${eventType}' :`, err);
        }
      });
    }
  }

  _scheduleReconnect() {
    this._clearReconnect();
    
    // Backoff exponentiel : 1s, 2s, 4s, 8s jusqu'à 30s max
    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
    this.reconnectAttempts++;
    
    logger.info(`[WebSocket Service] Planification de reconnexion dans ${delay / 1000}s (Tentative #${this.reconnectAttempts}).`);
    
    this.reconnectTimeoutId = setTimeout(() => {
      this.connect(this.token, this.meetingId);
    }, delay);
  }

  _clearReconnect() {
    if (this.reconnectTimeoutId) {
      clearTimeout(this.reconnectTimeoutId);
      this.reconnectTimeoutId = null;
    }
  }
}

const websocketService = new WebSocketService();
export default websocketService;
export { WebSocketService };
