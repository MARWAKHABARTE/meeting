# 🚀 Meeting AI Platform — Guide de Production

## Vue d'ensemble

Meeting AI Platform est une application SaaS complète de transcription, résumé et analyse IA de réunions, déployable avec une seule commande Docker Compose.

---

## 🐳 Démarrage rapide

```bash
# 1. Cloner et configurer
cp .env.example .env
# Modifier les secrets dans .env

# 2. Démarrer tous les services
docker compose up -d

# 3. Valider l'infrastructure
python scripts/validate.py
```

L'application sera accessible sur : **http://localhost**

---

## 📦 Architecture des Conteneurs

| Service        | Image                        | Port Public | Rôle |
|----------------|------------------------------|-------------|------|
| `nginx`        | nginx:stable-alpine          | 80          | Reverse proxy principal |
| `backend`      | ./backend/Dockerfile         | 8000 (interne) | API FastAPI |
| `frontend`     | ./frontend/Dockerfile        | (interne)   | App React servie par Nginx |
| `postgres`     | postgres:15-alpine           | 5432        | Base de données principale |
| `redis`        | redis:7-alpine               | 6379        | Broker Celery + Pub/Sub WS |
| `minio`        | minio/minio                  | 9000, 9001  | Stockage fichiers audio |
| `keycloak`     | keycloak:24.0.0              | 8080        | Auth OAuth2/OIDC |
| `ollama`       | ollama/ollama                | 11434       | LLM local (Mistral) |
| `chromadb`     | chromadb/chromadb:0.5.0      | 8002        | Base vectorielle RAG |
| `celery-worker`| ./backend/Dockerfile         | (interne)   | Tâches asynchrones IA |
| `flower`       | ./backend/Dockerfile         | 5555        | Monitoring Celery |
| `prometheus`   | prom/prometheus              | 9090        | Collecte métriques |
| `grafana`      | grafana/grafana              | 3000        | Dashboards monitoring |

---

## 🔐 Sécurité

- Tous les secrets sont dans `.env` (jamais commités)
- Les conteneurs s'exécutent avec un utilisateur non-root (`appuser`)
- Les headers HTTP de sécurité sont configurés dans Nginx
- JWT Keycloak valide sur tous les endpoints API protégés

---

## 📊 Monitoring

| URL                   | Service    | Identifiants |
|-----------------------|------------|--------------|
| http://localhost:3000 | Grafana    | admin / admin |
| http://localhost:9090 | Prometheus | (public) |
| http://localhost:5555 | Flower     | (public) |
| http://localhost:9001 | MinIO UI   | minioadmin / minioadmin |
| http://localhost:8080 | Keycloak   | admin / admin |

---

## 🧪 Tests

```bash
# Tests unitaires rapides (sans services externes)
cd backend
python -m pytest ../tests/test_settings.py ../tests/test_logger.py ../tests/test_api_health.py -v

# Tous les tests avec couverture
python -m pytest ../tests/ --cov=app --cov-report=html:../reports/coverage -v

# Validation Docker complète
python ../scripts/validate.py
```

---

## 🗄️ Sauvegardes

```bash
# Sauvegarde manuelle PostgreSQL
./scripts/backup.sh

# Restauration d'une sauvegarde
docker exec -i meeting_ai_postgres psql -U postgres -d meeting_ai < backups/postgres/meeting_ai_TIMESTAMP.sql

# Cron automatique (ajout à crontab -e)
0 2 * * * /path/to/scripts/backup.sh >> /var/log/meeting_ai_backup.log 2>&1
```

---

## 🔄 Mise à jour

```bash
# Arrêter les services
docker compose down

# Mettre à jour le code
git pull origin main

# Rebuilder uniquement les services modifiés
docker compose build backend frontend

# Redémarrer
docker compose up -d

# Appliquer les migrations Alembic
docker exec meeting_ai_backend alembic upgrade head
```

---

## 🔧 Variables d'environnement clés

Copier `.env.example` en `.env` et configurer :

| Variable | Description | Valeur par défaut |
|---|---|---|
| `POSTGRES_PASSWORD` | Mot de passe PostgreSQL | **À changer en prod** |
| `MINIO_SECRET_KEY` | Clé secrète MinIO | **À changer en prod** |
| `KEYCLOAK_ADMIN_PASSWORD` | Admin Keycloak | **À changer en prod** |
| `JWT_SECRET_KEY` | Clé JWT FastAPI | **À changer en prod** |
| `KEYCLOAK_CLIENT_SECRET` | Secret client backend | Valeur du realm-import.json |
| `OLLAMA_MODEL` | Modèle LLM à utiliser | `mistral` |

---

## 🆘 Dépannage

```bash
# Voir les logs d'un service
docker compose logs -f backend
docker compose logs -f celery-worker

# Vérifier l'état des conteneurs
docker compose ps

# Accéder au shell d'un conteneur
docker exec -it meeting_ai_backend bash
docker exec -it meeting_ai_postgres psql -U postgres -d meeting_ai

# Relancer un seul service
docker compose restart backend

# Réinitialisation complète (ATTENTION : supprime les volumes)
docker compose down -v
docker compose up -d
```

---

## 📋 Pipeline IA

Le traitement d'une réunion suit ce flux :

```
Upload Audio (MinIO) → Celery Worker → Whisper (Transcription)
→ Pyannote (Diarisation) → NLP Ollama (Résumé/Décisions)
→ ChromaDB (Indexation RAG) → WebSocket (Notifications Live)
```

---

*Sprint 12 — Production Ready | Meeting AI Platform*
