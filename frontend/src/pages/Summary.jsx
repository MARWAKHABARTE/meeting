import React, { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { useSummary } from "../hooks/useSummary";
import {
  Brain, ChevronLeft, CheckSquare, Target, TrendingUp,
  TrendingDown, Minus, RefreshCw, MessageSquare, FileText
} from "lucide-react";
import { Skeleton } from "../components/Skeleton";
import { EmptyState } from "../components/EmptyState";

/* ─── Demo data ─────────────────────────────────────────────────────────── */
const DEMO_SUMMARY = {
  summary: "La réunion de lancement a permis d'établir les priorités du Sprint 10 axé sur l'infrastructure WebSocket temps réel. L'équipe a validé l'approche Redis Pub/Sub comme passerelle entre les workers Celery et les connexions frontend. Les délais sont respectés et le périmètre bien défini.",
  decisions: [
    "Utiliser Redis Pub/Sub comme mécanisme de communication Workers → Broadcaster.",
    "Implémenter un ConnectionManager Singleton thread-safe.",
    "Valider l'authentification JWT Keycloak sur le handshake WebSocket.",
  ],
  action_items: [
    { text: "Créer le module app/websocket/ complet",          assignee: "Dev Backend",  priority: "high" },
    { text: "Implémenter WebSocketService.publish()",           assignee: "Dev Backend",  priority: "high" },
    { text: "Créer le hook useMeetingProgress côté frontend",   assignee: "Dev Frontend", priority: "medium" },
    { text: "Tester le flux complet end-to-end avec Celery",    assignee: "QA",           priority: "medium" },
    { text: "Documenter l'architecture dans walkthrough.md",     assignee: "Tech Lead",    priority: "low" },
  ],
  sentiment: { label: "Positif", score: 0.72 },
};

/* ─── Composants ────────────────────────────────────────────────────────── */
const SentimentGauge = ({ sentiment }) => {
  const isPositive = sentiment?.label?.toLowerCase() === "positif";
  const isNegative = sentiment?.label?.toLowerCase() === "négatif";
  const score = Math.round((sentiment?.score || 0) * 100);
  const Icon = isPositive ? TrendingUp : isNegative ? TrendingDown : Minus;
  const color = isPositive ? "var(--success-color)" : isNegative ? "var(--danger-color)" : "var(--warning-color)";

  return (
    <div className="sentiment-gauge">
      <div className="sentiment-icon" style={{ color }}>
        <Icon size={32} />
      </div>
      <div>
        <div className="sentiment-label" style={{ color }}>{sentiment?.label || "Neutre"}</div>
        <div className="sentiment-score">Score de confiance : {score}%</div>
      </div>
      <div className="sentiment-bar-wrapper">
        <div className="sentiment-bar-track">
          <div
            className="sentiment-bar-fill"
            style={{ width: `${score}%`, background: color }}
          />
        </div>
      </div>
    </div>
  );
};

const ActionItem = ({ item, index }) => {
  const priorityColor = {
    high: "var(--danger-color)",
    medium: "var(--warning-color)",
    low: "var(--success-color)",
  }[item.priority] || "var(--text-muted)";

  return (
    <div className="action-item">
      <span className="action-index">{index + 1}</span>
      <div className="action-content">
        <p className="action-text">{item.text}</p>
        {(item.assignee || item.priority) && (
          <div className="action-meta">
            {item.assignee && <span className="action-assignee">👤 {item.assignee}</span>}
            {item.priority && (
              <span className="action-priority" style={{ color: priorityColor }}>
                ● {item.priority}
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

/* ─── Page ────────────────────────────────────────────────────────────── */
const Summary = () => {
  const { id } = useParams();
  const { summary: apiSummary, loading, error, fetchSummary, triggerSummary } = useSummary(id);
  const [triggering, setTriggering] = useState(false);
  const [triggerError, setTriggerError] = useState(null);

  // Données: API si disponibles, sinon démo
  const data = apiSummary || DEMO_SUMMARY;
  const isDemo = !apiSummary;

  useEffect(() => { fetchSummary(id); }, [id, fetchSummary]);

  const handleTrigger = async () => {
    setTriggering(true);
    setTriggerError(null);
    try {
      await triggerSummary(id);
    } catch (err) {
      setTriggerError("Impossible de démarrer l'analyse NLP.");
    } finally {
      setTriggering(false);
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <Link to="/meetings" className="back-link">
            <ChevronLeft size={16} /> Retour aux réunions
          </Link>
          <h1 className="page-title">
            <Brain size={24} style={{ verticalAlign: "middle", marginRight: 8, color: "#8b5cf6" }} />
            Résumé & Analyse NLP
          </h1>
          {isDemo && <p className="demo-notice">⚠️ Données de démonstration — Lancez l'analyse NLP pour voir les résultats réels.</p>}
        </div>
        <div className="page-header-actions">
          <button className="btn btn-secondary" onClick={() => fetchSummary(id)} disabled={loading} aria-label="Rafraîchir le résumé">
            <RefreshCw size={15} className={loading ? "spin" : ""} />
            Actualiser
          </button>
          <button className="btn btn-primary" onClick={handleTrigger} disabled={triggering} aria-busy={triggering}>
            <Brain size={15} className={triggering ? "spin" : ""} />
            {triggering ? "Analyse en cours..." : "Lancer l'analyse NLP"}
          </button>
          <Link to={`/chat/${id}`} className="btn btn-secondary">
            <MessageSquare size={15} /> Chat IA
          </Link>
        </div>
      </div>

      {triggerError && <div className="alert alert-error" role="alert">{triggerError}</div>}

      {loading ? (
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {[...Array(3)].map((_, i) => <div key={i} className="card"><Skeleton height="120px" /></div>)}
        </div>
      ) : (
        <div className="summary-grid">

          {/* Résumé principal */}
          <div className="card summary-card-full">
            <div className="card-header">
              <h2 className="card-title"><Brain size={18} /> Résumé exécutif</h2>
            </div>
            <p className="summary-text">{data.summary}</p>
          </div>

          {/* Sentiment */}
          <div className="card">
            <div className="card-header">
              <h2 className="card-title"><TrendingUp size={18} /> Analyse de sentiment</h2>
            </div>
            <SentimentGauge sentiment={data.sentiment} />
          </div>

          {/* Décisions */}
          <div className="card">
            <div className="card-header">
              <h2 className="card-title"><Target size={18} /> Décisions prises</h2>
              <span className="card-count">{data.decisions?.length || 0}</span>
            </div>
            {data.decisions?.length > 0 ? (
              <ul className="decision-list">
                {data.decisions.map((d, i) => (
                  <li key={i} className="decision-item">
                    <CheckSquare size={16} style={{ color: "var(--success-color)", flexShrink: 0, marginTop: 2 }} />
                    <span>{d}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <EmptyState title="Aucune décision" description="Aucune décision n'a été détectée." />
            )}
          </div>

          {/* Actions */}
          <div className="card summary-card-full">
            <div className="card-header">
              <h2 className="card-title"><CheckSquare size={18} /> Actions à mener</h2>
              <span className="card-count">{data.action_items?.length || 0}</span>
            </div>
            {data.action_items?.length > 0 ? (
              <div className="action-list">
                {data.action_items.map((item, i) => (
                  <ActionItem key={i} item={item} index={i} />
                ))}
              </div>
            ) : (
              <EmptyState title="Aucune action" description="Aucun item d'action n'a été détecté." />
            )}
          </div>

          {/* Navigation */}
          <div className="card nav-card">
            <Link to={`/transcription/${id}`} className="nav-card-link">
              <FileText size={20} />
              <div>
                <div className="nav-card-label">Voir la transcription complète</div>
                <div className="nav-card-sub">Segments, locuteurs, timestamps</div>
              </div>
              <ChevronLeft size={18} style={{ transform: "rotate(180deg)" }} />
            </Link>
            <Link to={`/chat/${id}`} className="nav-card-link">
              <MessageSquare size={20} />
              <div>
                <div className="nav-card-label">Discuter avec l'IA (RAG)</div>
                <div className="nav-card-sub">Questions/réponses sur la réunion</div>
              </div>
              <ChevronLeft size={18} style={{ transform: "rotate(180deg)" }} />
            </Link>
          </div>
        </div>
      )}
    </div>
  );
};

export default Summary;
