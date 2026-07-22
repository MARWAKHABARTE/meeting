/**
 * Logger léger sécurisé pour l'application.
 * Les messages s'affichent uniquement en mode développement (Vite).
 * Les données sensibles (mots de passe, tokens) ne doivent jamais y être passées.
 */

const isDev = import.meta.env.MODE === "development";

const logger = {
  debug: (message, ...args) => {
    if (isDev) {
      console.debug(`%c[DEBUG] %c${message}`, "color: #8b5cf6; font-weight: bold;", "color: inherit;", ...args);
    }
  },
  info: (message, ...args) => {
    if (isDev) {
      console.info(`%c[INFO]  %c${message}`, "color: #3b82f6; font-weight: bold;", "color: inherit;", ...args);
    }
  },
  warn: (message, ...args) => {
    if (isDev) {
      console.warn(`%c[WARN]  %c${message}`, "color: #f59e0b; font-weight: bold;", "color: inherit;", ...args);
    }
  },
  error: (message, ...args) => {
    if (isDev) {
      console.error(`%c[ERROR] %c${message}`, "color: #ef4444; font-weight: bold;", "color: inherit;", ...args);
    }
  }
};

export default logger;
