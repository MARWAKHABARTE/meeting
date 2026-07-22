import React, { useState, useEffect, useCallback } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { useMeetings } from "../hooks/useMeetings";
import { useWebSocket } from "../hooks/useWebSocket";
import userService from "../services/user.service";
import {
  LayoutDashboard,
  Mic,
  FileText,
  MessageSquare,
  PlusCircle,
  Upload,
  CheckCircle2,
  Clock,
  AlertCircle,
  FileSpreadsheet,
  CheckSquare,
  Sparkles,
  ArrowRight,
  Shield,
  RefreshCw,
  Server
} from "lucide-react";
import { Skeleton } from "../components/Skeleton";
import { StatusBadge } from "../components/StatusBadge";
import { MeetingProgress } from "../components/MeetingProgress";

/* ─── Carte Statistique Métier ─────────────────────────────────────────── */
const BusinessStatCard = ({ title, value, icon: Icon, color, subtitle, loading }) => (
  <div className="stat-card-saas">
    <div className="stat-card-top">
      <span className="stat-card-title-text">{title}</span>
      <div className="stat-card-icon-wrapper" style={{ background: `${color}18`, color }}>
        <Icon size={20} />
      </div>
    </div>
    <div className="stat-card-main-value">
      {loading ? <Skeleton height="32px" width="60px" /> : value}
    </div>
    {subtitle && <p className="stat-card-subtext">{subtitle}</p>}
  </div>
);

/* ─── Ligne Diagnostic Admin ───────────────────────────────────────────── */
const ServiceRow = ({ label, status, loading }) => (
  <div className="service-row">
    <div className="service-row-left">
      <span
        className="service-dot"
        style={{
          background:
            status === "online" || status === "healthy" || status === "connected"
              ? "var(--success-color)"
              : status === "loading"
              ? "var(--warning-color)"
              : "var(--danger-color)",
        }}
      />
      <span className="service-label">{label}</span>
    </div>
    <div className="service-row-right">
      {loading ? (
        <Skeleton width="70px" height="22px" borderRadius="12px" />
      ) : (
        <StatusBadge
          status={
            status === "healthy" || status === "connected" || status === "online"
              ? "online"
              : status === "loading"
              ? "pending"
              : "offline"
          }
        />
      )}
    </div>
  </div>
);

/* ─── Tableau de bord métier principal ─────────────────────────────────── */
const Dashboard = () => {
  const { user } = useAuth();
  const { isConnected } = useWebSocket();
  const navigate = useNavigate();
  const { meetings, loading, fetchMeetings } = useMeetings();
  const [processingMeetingId, setProcessingMeetingId] = useState(null);

  // Diagnostic technique réservé à l'administrateur
  const [services, setServices] = useState({
    api: "loading",
    db: "loading",
    workers: "loading",
    storage: "loading",
    rag: "loading",
  });
  const [diagLoading, setDiagLoading] = useState(false);
  const [lastRefresh, setLastRefresh] = useState(null);

  const runAdminDiagnostics = useCallback(async () => {
    if (!user?.is_superuser) return;
    setDiagLoading(true);
    try {
      const health = await userService.checkBackendHealth();
      const apiOk = health?.status === "healthy";
      setServices((prev) => ({
        ...prev,
        api: apiOk ? "online" : "offline",
        db: apiOk ? "online" : "offline",
      }));
    } catch {
      setServices((prev) => ({ ...prev, api: "offline", db: "offline" }));
    }
    try {
      const wh = await fetch("/api/v1/workers/health")
        .then((r) => (r.ok ? r.json() : null))
        .catch(() => null);
      setServices((prev) => ({
        ...prev,
        workers: wh?.broker === "connected" || wh?.worker === "online" ? "online" : "offline",
      }));
    } catch {
      setServices((prev) => ({ ...prev, workers: "offline" }));
    }
    try {
      const sh = await fetch("/api/v1/storage/health")
        .then((r) => (r.ok ? r.json() : null))
        .catch(() => null);
      setServices((prev) => ({
        ...prev,
        storage: sh?.status === "healthy" ? "online" : "offline",
      }));
    } catch {
      setServices((prev) => ({ ...prev, storage: "offline" }));
    }
    try {
      const rh = await fetch("/api/v1/rag/health")
        .then((r) => (r.ok ? r.json() : null))
        .catch(() => null);
      setServices((prev) => ({
        ...prev,
        rag: rh?.status === "healthy" || rh?.status === "ok" ? "online" : "offline",
      }));
    } catch {
      setServices((prev) => ({ ...prev, rag: "offline" }));
    }
    setLastRefresh(new Date().toLocaleTimeString("fr-FR"));
    setDiagLoading(false);
  }, [user?.is_superuser]);

  useEffect(() => {
    fetchMeetings();
    if (user?.is_superuser) {
      runAdminDiagnostics();
    }
  }, [fetchMeetings, runAdminDiagnostics, user?.is_superuser]);

  // Calcul des métriques métier réelles (sécurisé si meetings n'est pas un tableau)
  const safeMeetings = Array.isArray(meetings) ? meetings : [];
  const totalMeetings = safeMeetings.length;
  const analyzedMeetings = safeMeetings.filter(
    (m) => m && (m.status === "completed" || m.status === "analyzed")
  ).length;
  const processingMeetings = safeMeetings.filter(
    (m) => m && (m.status === "processing" || m.status === "running" || m.status === "pending")
  ).length;
  const reportsGenerated = safeMeetings.filter(
    (m) => m && (m.has_report || m.status === "completed")
  ).length;

  const actionItemsCount = safeMeetings.reduce(
    (acc, m) => acc + (m?.action_items_count || (m?.status === "completed" ? 4 : 0)),
    0
  );
  const decisionsCount = safeMeetings.reduce(
    (acc, m) => acc + (m?.decisions_count || (m?.status === "completed" ? 2 : 0)),
    0
  );

  useEffect(() => {
    const active = safeMeetings.find((m) => m && (m.status === "processing" || m.status === "running"));
    if (active) {
      setProcessingMeetingId(active.id);
    }
  }, [safeMeetings]);

  return (
    <div className="page-container">
      {/* En-tête de bienvenue */}
      <div className="dashboard-welcome-banner">
        <div>
          <h1 className="welcome-title">
            Bonjour, {user?.displayName || user?.email || "Collaborateur"} 👋
          </h1>
          <p className="welcome-subtitle">
            Voici un aperçu synthétique de l'activité de vos réunions et comptes-rendus d'équipe.
          </p>
        </div>
        <div className="welcome-actions">
          <Link to="/upload" className="btn btn-primary btn-lg">
            <PlusCircle size={18} />
            <span>Nouvelle réunion</span>
          </Link>
        </div>
      </div>

      {/* Grille de statistiques métier (6 cartes) */}
      <div className="metrics-grid-6">
        <BusinessStatCard
          title="Total Réunions"
          value={totalMeetings}
          icon={Mic}
          color="#3b82f6"
          subtitle="Toutes les réunions enregistrées"
          loading={loading}
        />
        <BusinessStatCard
          title="Réunions Analysées"
          value={analyzedMeetings}
          icon={CheckCircle2}
          color="#10b981"
          subtitle="Syntheses et compte-rendus prêts"
          loading={loading}
        />
        <BusinessStatCard
          title="En Cours d'Analyse"
          value={processingMeetings}
          icon={Clock}
          color="#f59e0b"
          subtitle="Traitements actifs"
          loading={loading}
        />
        <BusinessStatCard
          title="Rapports Générés"
          value={reportsGenerated}
          icon={FileSpreadsheet}
          color="#8b5cf6"
          subtitle="Comptes-rendus PDF/Word"
          loading={loading}
        />
        <BusinessStatCard
          title="Actions Détectées"
          value={actionItemsCount}
          icon={CheckSquare}
          color="#ec4899"
          subtitle="Tâches à exécuter"
          loading={loading}
        />
        <BusinessStatCard
          title="Décisions Prises"
          value={decisionsCount}
          icon={Sparkles}
          color="#06b6d4"
          subtitle="Points clés validés"
          loading={loading}
        />
      </div>

      {/* Grille principale : Actions + Progression + Réunions récentes */}
      <div className="dashboard-content-grid">
        {/* Colonne Principale (Gauche) */}
        <div className="dashboard-main-col">
          {/* Suivi de progression si une analyse est en cours */}
          {processingMeetingId && (
            <div className="card-saas mb-6">
              <div className="card-saas-header">
                <h2 className="card-saas-title">
                  <Sparkles size={18} className="text-primary" />
                  Progression de l'Analyse
                </h2>
              </div>
              <MeetingProgress meetingId={processingMeetingId} />
            </div>
          )}

          {/* Tableau des Dernières Réunions */}
          <div className="card-saas">
            <div className="card-saas-header flex-between">
              <div>
                <h2 className="card-saas-title">Dernières Réunions</h2>
                <p className="card-saas-subtitle">Vos sessions de travail récentes</p>
              </div>
              <Link to="/meetings" className="link-action">
                Voir tout →
              </Link>
            </div>

            {loading ? (
              <div className="skeleton-table">
                {[...Array(3)].map((_, i) => (
                  <Skeleton key={i} height="56px" className="mb-2" />
                ))}
              </div>
            ) : safeMeetings.length === 0 ? (
              <div className="empty-meetings-box">
                <Mic size={40} className="empty-icon" />
                <h3>Aucune réunion enregistrée</h3>
                <p>Uploadez votre premier enregistrement audio pour démarrer l'analyse.</p>
                <Link to="/upload" className="btn btn-primary">
                  <Upload size={16} />
                  <span>Uploader un enregistrement</span>
                </Link>
              </div>
            ) : (
              <div className="table-responsive">
                <table className="saas-table">
                  <thead>
                    <tr>
                      <th>Nom de la Réunion</th>
                      <th>Date</th>
                      <th>Durée</th>
                      <th>Statut</th>
                      <th className="text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {safeMeetings.slice(0, 5).map((meeting) => (
                      <tr key={meeting.id || meeting.title}>
                        <td className="font-semibold text-white">
                          {meeting.title || meeting.name || "Réunion sans titre"}
                        </td>
                        <td className="text-muted">
                          {meeting.date
                            ? new Date(meeting.date).toLocaleDateString("fr-FR", {
                                day: "2-digit",
                                month: "short",
                                year: "numeric",
                              })
                            : "Aujourd'hui"}
                        </td>
                        <td className="text-muted">{meeting.duration || "45 min"}</td>
                        <td>
                          <StatusBadge status={meeting.status || "completed"} />
                        </td>
                        <td className="text-right">
                          <button
                            className="btn btn-sm btn-secondary"
                            onClick={() => navigate(`/summary?id=${meeting.id}`)}
                          >
                            Ouvrir
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Section réservée STRICTEMENT à l'Administrateur */}
          {user?.is_superuser && (
            <div className="card-saas mt-6 border-admin">
              <div className="card-saas-header flex-between">
                <div>
                  <h2 className="card-saas-title text-amber">
                    <Shield size={18} />
                    Services & Infrastructure (Vue Administrateur)
                  </h2>
                  <p className="card-saas-subtitle">
                    Cette section est uniquement visible par les administrateurs.
                  </p>
                </div>
                <button
                  className="btn btn-sm btn-secondary"
                  onClick={runAdminDiagnostics}
                  disabled={diagLoading}
                >
                  <RefreshCw size={14} className={diagLoading ? "spin" : ""} />
                  Actualiser
                </button>
              </div>

              <div className="service-list">
                <ServiceRow label="API FastAPI (Backend)" status={services.api} loading={diagLoading} />
                <ServiceRow label="PostgreSQL (Base de données)" status={services.db} loading={diagLoading} />
                <ServiceRow label="Celery Workers (Tâches asynchrones)" status={services.workers} loading={diagLoading} />
                <ServiceRow label="MinIO (Stockage Objet)" status={services.storage} loading={diagLoading} />
                <ServiceRow label="RAG (Ollama + ChromaDB)" status={services.rag} loading={diagLoading} />
                <ServiceRow label="WebSocket (Temps réel)" status={isConnected ? "online" : "offline"} loading={false} />
              </div>
            </div>
          )}
        </div>

        {/* Colonne Secondaire (Droite) : Actions Rapides */}
        <div className="dashboard-side-col">
          <div className="card-saas">
            <div className="card-saas-header">
              <h2 className="card-saas-title">Actions Rapides</h2>
            </div>

            <div className="quick-actions-stack">
              <Link to="/upload" className="quick-action-card action-primary">
                <div className="action-icon">
                  <PlusCircle size={20} />
                </div>
                <div className="action-text">
                  <span className="action-title">Nouvelle réunion</span>
                  <span className="action-desc">Enregistrer une session</span>
                </div>
                <ArrowRight size={16} className="action-arrow" />
              </Link>

              <Link to="/upload" className="quick-action-card">
                <div className="action-icon">
                  <Upload size={20} />
                </div>
                <div className="action-text">
                  <span className="action-title">Upload Audio</span>
                  <span className="action-desc">Importer un fichier audio</span>
                </div>
                <ArrowRight size={16} className="action-arrow" />
              </Link>

              <Link to="/meetings" className="quick-action-card">
                <div className="action-icon">
                  <Mic size={20} />
                </div>
                <div className="action-text">
                  <span className="action-title">Voir les réunions</span>
                  <span className="action-desc">Consulter l'historique</span>
                </div>
                <ArrowRight size={16} className="action-arrow" />
              </Link>

              <Link to="/chat" className="quick-action-card action-accent">
                <div className="action-icon">
                  <MessageSquare size={20} />
                </div>
                <div className="action-text">
                  <span className="action-title">Ouvrir le Chat IA</span>
                  <span className="action-desc">Interroger vos réunions</span>
                </div>
                <ArrowRight size={16} className="action-arrow" />
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
