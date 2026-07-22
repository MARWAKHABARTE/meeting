# ==========================================
# Étape 1 : Build de l'application React
# ==========================================
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./

RUN npm install --legacy-peer-deps

COPY . .

# Variables de build (valeurs par défaut de production)
ARG VITE_API_URL=/api
ARG VITE_KEYCLOAK_URL=/keycloak
ARG VITE_KEYCLOAK_REALM=meeting-ai
ARG VITE_KEYCLOAK_CLIENT_ID=meeting-ai-frontend

ENV VITE_API_URL=$VITE_API_URL \
    VITE_KEYCLOAK_URL=$VITE_KEYCLOAK_URL \
    VITE_KEYCLOAK_REALM=$VITE_KEYCLOAK_REALM \
    VITE_KEYCLOAK_CLIENT_ID=$VITE_KEYCLOAK_CLIENT_ID

RUN npm run build

# ==========================================
# Étape 2 : Serveur Nginx léger pour la prod
# ==========================================
FROM nginx:stable-alpine AS runner

COPY --from=builder /app/dist /usr/share/nginx/html

# Configuration Nginx de base pour Single Page Application (SPA)
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
