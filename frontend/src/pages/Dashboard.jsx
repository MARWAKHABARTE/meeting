import React, { useState, useEffect, useCallback } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { useWebSocket } from "../hooks/useWebSocket";
import userService from "../services/user.service";
import {
  LayoutDashboard, Mic, FileText, Brain, Activity,
  RefreshCw, ArrowRight, CheckCircle, Clock, AlertTriangle,
  Cpu, Zap, TrendingUp, Users
} from "lucide-react";
import { Skeleton, SkeletonCard } from "../components/Skeleton";
import { StatusBadge } from "../components/StatusBadge";
import { MeetingProgress } from "../components/MeetingProgress";
import ConnectionStatus from "../components/ConnectionStatus";

/* ─── Constantes ──────────────────────────────────────────────────────── */
const PIPELINE_STEPS = [
  { id: "upload",        label: "Upload Audio",       icon: Mic,      color: "#6366f1", desc: "MinIO Object Storage" },
  { id: "transcription", label: "Transcription",      icon: FileText, color: "#3b82f6", desc: "Whisper + Pyannote" },
  { id: "nlp",           label: "Analyse NLP",        icon: Brain,    color: "#8b5cf6", desc: "Ollama LLM" },
  { id: "rag",           label: "Index RAG",          icon: Cpu,      color: "#10b981", desc: "ChromaDB Embeddings" },
];

const QUICK_LINKS = [
  { to: "/upload",    label: "Nouvel Upload",       icon: Mic,      variant: "primary" },
  { to: "/meetings",  label: "Toutes les réunions", icon: FileText, variant: "secondary" },
  { to: "/chat",      label: "Chat IA (RAG)",       icon: Brain,    variant: "secondary" },
];

/* ─── Composants internes ─────────────────────────────────────────────── */
const StatCard = ({ title, value, icon: Icon, color, subtitle, loading }) => (
  <div className="stat-card">
    <div className="stat-card-header">
      <span className="stat-card-title">{title}</span>
      <div className="stat-card-icon" style={{ color }}>
        <Icon size={22} />
      </div>
    </div>
    <div className="stat-card-value">
      {loading ? <Skeleton height="32px" width="80px" /> : value}
    </div>
    {subtitle && <p className="stat-card-subtitle">{subtitle}</p>}
  </div>
);

const ServiceRow = ({ label, status, detail, loading }) => (
  <div className="service-row">
    <div className="service-row-left">
      <span className="service-dot" style={{ background: status === "online" || status === "healthy" || status === "connected" ? "var(--success-color)" : status === "loading" ? "var(--warning-color)" : "var(--danger-color)" }} />
      <span className="service-label">{label}</span>
    </div>
    <div className="service-row-right">
      {loading
        ? <Skeleton width="70px" height="22px" borderRadius="12px" />
        : <StatusBadge status={status === "healthy" || status === "connected" ? "online" : status === "loading" ? "pending" : status} />
      }
      {detail && <span className="service-detail">{detail}</span>}
    </div>
  </div>
);

/* ─── Dashboard ────────────────────────────────────────────────────────── */
const Dashboard = () => {
  const { user } = useAuth();
  const { isConnected } = useWebSocket();
  const [services, setServices] = useState({ api: "loading", db: "loading", workers: "loading", storage: "loading", rag: "loading" });
  const [loading, setLoading] = useState(true);
  const [lastRefresh, setLastRefresh] = useState(null);

  const runDiagnostics = useCallback(async () => {
    setLoading(true);
    try {
      const health = await userService.checkBackendHealth();
      const apiOk = health?.status === "healthy";
      setServices(prev => ({ ...prev, api: apiOk ? "online" : "offline", db: apiOk ? "connected" : "offline" }));
    } catch {
      setServices(prev => ({ ...prev, api: "offline", db: "offline" }));
    }
    try {
      const ws = await import("../services/user.service").then(m => m.default);
      const wh = await fetch("/api/v1/workers/health").then(r => r.ok ? r.json() : null).catch(() => null);
      setServices(prev => ({ ...prev, workers: wh?.worker === "online" ? "online" : "offline" }));
    } catch {
      setServices(prev => ({ ...prev, workers: "offline" }));
    }
    try {
      const sh = await fetch("/api/v1/storage/health").then(r => r.ok ? r.json() : null).catch(() => null);
      setServices(prev => ({ ...prev, storage: sh?.status === "healthy" ? "healthy" : "offline" }));
    } catch {
      setServices(prev => ({ ...prev, storage: "offline" }));
    }
    try {
      const rh = await fetch("/api/v1/rag/health").then(r => r.ok ? r.json() : null).catch(() => null);
      setServices(prev => ({ ...prev, rag: rh?.status === "ok" ? "healthy" : "offline" }));
    } catch {
      setServices(prev => ({ ...prev, rag: "offline" }));
    }
    setLastRefresh(new Date().toLocaleTimeString("fr-FR"));
    setLoading(false);
  }, []);

  useEffect(() => { runDiagnostics(); }, [runDiagnostics]);

  const allHealthy = Object.values(services).every(s => s === "online" || s === "healthy" || s === "connected");

  return (
    <div className="page">
      {/* En-tête */}
      <div className="page-header">
        <div>
          <h1 className="page-title">
            <LayoutDashboard size={26} style={{ verticalAlign: "middle", marginRight: 8, color: "var(--accent-color)" }} />
            Dashboard
          </h1>
          <p className="page-description">
            Bienvenue, <strong>{user?.displayName || user?.email || "Utilisateur"}</strong> — Plateforme Meeting AI
          </p>
        </div>
        <div className="page-header-actions">
          <button className="btn btn-secondary" onClick={runDiagnostics} disabled={loading} aria-label="Actualiser les diagnostics">
            <RefreshCw size={15} className={loading ? "spin" : ""} />
            Actualiser
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="stats-grid-4">
        <StatCard title="Réunions" value="—" icon={Mic} color="var(--accent-color)" subtitle="Chargement en cours" loading={loading} />
        <StatCard title="Transcriptions" value="—" icon={FileText} color="#3b82f6" subtitle="Chargement en cours" loading={loading} />
        <StatCard title="Rapports NLP" value="—" icon={Brain} color="#8b5cf6" subtitle="Chargement en cours" loading={loading} />
        <StatCard title="WebSocket" value={isConnected ? "Connecté" : "Déconnecté"} icon={Zap} color={isConnected ? "var(--success-color)" : "var(--danger-color)"} subtitle="Temps réel" loading={false} />
      </div>

      {/* Corps principal : 2 colonnes */}
      <div className="dashboard-grid">

        {/* Colonne gauche */}
        <div className="dashboard-col">

          {/* Pipeline IA */}
          <div className="card">
            <div className="card-header">
              <h2 className="card-title"><Cpu size={18} />  Pipeline IA</h2>
            </div>
            <div className="pipeline-steps">
              {PIPELINE_STEPS.map((step, i) => {
                const Icon = step.icon;
                return (
                  <React.Fragment key={step.id}>
                    <div className="pipeline-step">
                      <div className="pipeline-icon" style={{ background: `${step.color}22`, border: `1px solid ${step.color}44` }}>
                        <Icon size={20} style={{ color: step.color }} />
                      </div>
                      <div>
                        <div className="pipeline-label">{step.label}</div>
                        <div className="pipeline-desc">{step.desc}</div>
                      </div>
                    </div>
                    {i < PIPELINE_STEPS.length - 1 && (
                      <div className="pipeline-arrow"><ArrowRight size={16} /></div>
                    )}
                  </React.Fragment>
                );
              })}
            </div>
          </div>

          {/* Liens rapides */}
          <div className="card">
            <div className="card-header">
              <h2 className="card-title"><TrendingUp size={18} />  Actions rapides</h2>
            </div>
            <div className="quick-links">
              {QUICK_LINKS.map(({ to, label, icon: Icon, variant }) => (
                <Link key={to} to={to} className={`btn btn-${variant} quick-link-btn`}>
                  <Icon size={16} />
                  {label}
                </Link>
              ))}
            </div>
          </div>

          {/* Suivi WebSocket */}
          <div className="card">
            <div className="card-header">
              <h2 className="card-title"><Activity size={18} />  Progression temps réel</h2>
              <ConnectionStatus />
            </div>
            <MeetingProgress meetingId={null} />
          </div>
        </div>

        {/* Colonne droite */}
        <div className="dashboard-col">

          {/* Santé des services */}
          <div className="card">
            <div className="card-header">
              <h2 className="card-title">
                {allHealthy
                  ? <CheckCircle size={18} style={{ color: "var(--success-color)" }} />
                  : <AlertTriangle size={18} style={{ color: "var(--warning-color)" }} />
                }
                &nbsp; Services & Infrastructure
              </h2>
              {lastRefresh && <span className="card-subtitle">Dernière vérification : {lastRefresh}</span>}
            </div>
            <div className="service-list">
              <ServiceRow label="API FastAPI (Backend)" status={services.api} loading={loading} />
              <ServiceRow label="PostgreSQL (Base de données)" status={services.db} loading={loading} />
              <ServiceRow label="Celery Workers (Tâches asynchrones)" status={services.workers} loading={loading} />
              <ServiceRow label="MinIO (Stockage Objet)" status={services.storage} loading={loading} />
              <ServiceRow label="RAG (Ollama + ChromaDB)" status={services.rag} loading={loading} />
              <ServiceRow label="WebSocket (Temps réel)" status={isConnected ? "online" : "offline"} loading={false} />
            </div>
          </div>

          {/* Activité récente — placeholder */}
          <div className="card">
            <div className="card-header">
              <h2 className="card-title"><Clock size={18} />  Activité récente</h2>
            </div>
            {loading ? (
              <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                {[...Array(4)].map((_, i) => <Skeleton key={i} height="52px" />)}
              </div>
            ) : (
              <div className="activity-list">
                <div className="activity-empty">
                  <Users size={32} strokeWidth={1.5} />
                  <p>Aucune activité récente.<br />Uploadez votre première réunion pour commencer.</p>
                  <Link to="/upload" className="btn btn-primary btn-sm">Commencer →</Link>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
