import React, { useState, useEffect, useCallback, useMemo } from "react";
import { Link } from "react-router-dom";
import { useMeetings } from "../hooks/useMeetings";
import { Mic, Search, FileText, Brain, MessageSquare, RefreshCw, Upload, Play, ChevronRight } from "lucide-react";
import { StatusBadge } from "../components/StatusBadge";
import { Skeleton, SkeletonTable } from "../components/Skeleton";
import { EmptyState } from "../components/EmptyState";
import Button from "../components/Button";

/* ─── Demo data (affiché tant que le CRUD Meetings n'est pas finalisé côté API) ── */
const DEMO_MEETINGS = [
  { id: "1", title: "Réunion de lancement Sprint 10", date: "2026-07-15T10:00:00Z", duration: "45 min", status: "completed", speakers: 3, file: "reunion_sprint10.mp3" },
  { id: "2", title: "Revue hebdomadaire équipe",      date: "2026-07-14T14:00:00Z", duration: "30 min", status: "processing", speakers: 2, file: "revue_hebdo.wav" },
  { id: "3", title: "Interview client Enterprise",    date: "2026-07-12T09:00:00Z", duration: "60 min", status: "pending",    speakers: 4, file: "interview.mp3" },
  { id: "4", title: "Séance de brainstorming design", date: "2026-07-10T16:30:00Z", duration: "90 min", status: "failed",     speakers: 5, file: "brainstorm.ogg" },
];

const formatDate = (iso) => new Date(iso).toLocaleDateString("fr-FR", { day: "2-digit", month: "short", year: "numeric" });

/* ─── Row de la table ─────────────────────────────────────────────────── */
const MeetingRow = ({ meeting, onStartTranscription, onStartSummary }) => (
  <tr className="table-row">
    <td className="table-cell">
      <div className="meeting-title-cell">
        <div className="meeting-icon"><Mic size={16} /></div>
        <div>
          <div className="meeting-name">{meeting.title}</div>
          <div className="meeting-file">{meeting.file}</div>
        </div>
      </div>
    </td>
    <td className="table-cell table-cell-secondary">{formatDate(meeting.date)}</td>
    <td className="table-cell table-cell-secondary">{meeting.duration}</td>
    <td className="table-cell table-cell-secondary">{meeting.speakers} locuteurs</td>
    <td className="table-cell"><StatusBadge status={meeting.status} /></td>
    <td className="table-cell">
      <div className="row-actions">
        {meeting.status === "pending" && (
          <button className="btn btn-xs btn-primary" onClick={() => onStartTranscription(meeting.id)} title="Démarrer la transcription">
            <Play size={12} /> Transcrire
          </button>
        )}
        {meeting.status === "completed" && (
          <>
            <Link to={`/transcription/${meeting.id}`} className="btn btn-xs btn-secondary" title="Voir la transcription">
              <FileText size={12} /> Transcript
            </Link>
            <Link to={`/summary/${meeting.id}`} className="btn btn-xs btn-secondary" title="Voir le résumé">
              <Brain size={12} /> Résumé
            </Link>
            <Link to={`/chat/${meeting.id}`} className="btn btn-xs btn-secondary" title="Chat IA">
              <MessageSquare size={12} /> Chat
            </Link>
          </>
        )}
        <Link to={`/meetings/${meeting.id}`} className="btn btn-xs btn-ghost" title="Détail">
          <ChevronRight size={14} />
        </Link>
      </div>
    </td>
  </tr>
);

/* ─── Page ────────────────────────────────────────────────────────────── */
const Meetings = () => {
  const { startTranscription, startSummary } = useMeetings();
  const [search, setSearch] = useState("");
  const [filterStatus, setFilterStatus] = useState("all");
  const [loading] = useState(false);
  const meetings = DEMO_MEETINGS;

  const filtered = useMemo(() => {
    return meetings.filter((m) => {
      const matchSearch = m.title.toLowerCase().includes(search.toLowerCase());
      const matchStatus = filterStatus === "all" || m.status === filterStatus;
      return matchSearch && matchStatus;
    });
  }, [meetings, search, filterStatus]);

  const handleStartTranscription = useCallback(async (id) => {
    try { await startTranscription(id); }
    catch (err) { console.error(err); }
  }, [startTranscription]);

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1 className="page-title">
            <Mic size={24} style={{ verticalAlign: "middle", marginRight: 8, color: "var(--accent-color)" }} />
            Réunions
          </h1>
          <p className="page-description">Gérez vos enregistrements et suivez le pipeline d'analyse IA.</p>
        </div>
        <div className="page-header-actions">
          <Link to="/upload" className="btn btn-primary">
            <Upload size={15} /> Nouveau Upload
          </Link>
        </div>
      </div>

      {/* Barre de filtres */}
      <div className="filters-bar">
        <div className="search-wrapper">
          <Search size={16} className="search-icon" />
          <input
            className="search-input"
            type="search"
            placeholder="Rechercher une réunion..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            aria-label="Rechercher une réunion"
          />
        </div>
        <div className="filter-pills">
          {["all", "pending", "processing", "completed", "failed"].map((s) => (
            <button
              key={s}
              className={`filter-pill ${filterStatus === s ? "active" : ""}`}
              onClick={() => setFilterStatus(s)}
            >
              {s === "all" ? "Toutes" : s === "pending" ? "En attente" : s === "processing" ? "En cours" : s === "completed" ? "Terminées" : "Échouées"}
            </button>
          ))}
        </div>
        <span className="results-count">{filtered.length} résultat{filtered.length !== 1 ? "s" : ""}</span>
      </div>

      {/* Table */}
      {loading ? (
        <div className="card"><SkeletonTable rows={5} /></div>
      ) : filtered.length === 0 ? (
        <EmptyState
          type="search"
          title="Aucune réunion trouvée"
          description={search ? `Aucun résultat pour "${search}".` : "Commencez par uploader un enregistrement audio."}
          action={<Link to="/upload" className="btn btn-primary">Uploader un fichier</Link>}
        />
      ) : (
        <div className="card table-card">
          <div className="table-scroll">
            <table className="data-table" role="table" aria-label="Liste des réunions">
              <thead>
                <tr>
                  <th className="table-th">Réunion</th>
                  <th className="table-th">Date</th>
                  <th className="table-th">Durée</th>
                  <th className="table-th">Locuteurs</th>
                  <th className="table-th">Statut</th>
                  <th className="table-th">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((m) => (
                  <MeetingRow
                    key={m.id}
                    meeting={m}
                    onStartTranscription={handleStartTranscription}
                    onStartSummary={startSummary}
                  />
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default Meetings;
