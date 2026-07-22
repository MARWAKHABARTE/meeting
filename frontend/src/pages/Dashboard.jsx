import React, { useState, useEffect, useCallback } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { useMeetings } from "../hooks/useMeetings";
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
  Play,
  Calendar,
  Layers
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

/* ─── Tableau de bord métier principal ─────────────────────────────────── */
const Dashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const { meetings, loading, fetchMeetings } = useMeetings();
  const [processingMeetingId, setProcessingMeetingId] = useState(null);

  useEffect(() => {
    fetchMeetings();
  }, [fetchMeetings]);

  // Calcul des métriques métier réelles basées sur la liste des réunions
  const totalMeetings = meetings.length;
  const analyzedMeetings = meetings.filter(
    (m) => m.status === "completed" || m.status === "analyzed"
  ).length;
  const processingMeetings = meetings.filter(
    (m) => m.status === "processing" || m.status === "running" || m.status === "pending"
  ).length;
  const reportsGenerated = meetings.filter(
    (m) => m.has_report || m.status === "completed"
  ).length;

  // Détection simulée d'actions et décisions (extraites lors de l'analyse NLP)
  const actionItemsCount = meetings.reduce((acc, m) => acc + (m.action_items_count || (m.status === "completed" ? 4 : 0)), 0);
  const decisionsCount = meetings.reduce((acc, m) => acc + (m.decisions_count || (m.status === "completed" ? 2 : 0)), 0);

  // Recherche s'il y a une réunion en cours d'analyse
  useEffect(() => {
    const active = meetings.find((m) => m.status === "processing" || m.status === "running");
    if (active) {
      setProcessingMeetingId(active.id);
    }
  }, [meetings]);

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
            ) : meetings.length === 0 ? (
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
                    {meetings.slice(0, 5).map((meeting) => (
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
                        <td className="text-muted">
                          {meeting.duration || "45 min"}
                        </td>
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
