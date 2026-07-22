import React, { useState, useEffect, useCallback, useMemo, useRef } from "react";
import { useParams, Link } from "react-router-dom";
import meetingService from "../services/meeting.service";
import { FileText, Search, Copy, CheckCheck, ChevronLeft, User, Clock } from "lucide-react";
import { StatusBadge } from "../components/StatusBadge";
import { Skeleton } from "../components/Skeleton";
import { EmptyState } from "../components/EmptyState";
import logger from "../utils/logger";

/* ─── Couleurs par locuteur ────────────────────────────────────────────── */
const SPEAKER_COLORS = [
  "#6366f1", "#10b981", "#f59e0b", "#ef4444",
  "#3b82f6", "#8b5cf6", "#ec4899", "#14b8a6",
];

const getSpeakerColor = (name) => {
  const idx = (name?.charCodeAt(0) || 0) % SPEAKER_COLORS.length;
  return SPEAKER_COLORS[idx];
};

const formatTime = (seconds) => {
  if (seconds == null) return "—";
  const m = Math.floor(seconds / 60).toString().padStart(2, "0");
  const s = Math.floor(seconds % 60).toString().padStart(2, "0");
  return `${m}:${s}`;
};

/* ─── Segment de transcription ─────────────────────────────────────────── */
const TranscriptSegment = React.memo(({ segment, isHighlighted }) => {
  const color = getSpeakerColor(segment.speaker);
  return (
    <div className={`transcript-segment ${isHighlighted ? "transcript-segment--highlighted" : ""}`}>
      <div className="segment-meta">
        <span className="segment-speaker" style={{ color }}>
          <User size={12} />
          {segment.speaker || "Inconnu"}
        </span>
        <span className="segment-time">
          <Clock size={11} />
          {formatTime(segment.start)} – {formatTime(segment.end)}
        </span>
      </div>
      <p className="segment-text">{segment.text}</p>
    </div>
  );
});

/* ─── Demo data ─────────────────────────────────────────────────────────── */
const DEMO_TRANSCRIPT = {
  full_text: "Bonjour, nous allons commencer la réunion de lancement. Nous avons plusieurs sujets à aborder aujourd'hui : le planning du sprint, les risques identifiés, et les prochaines étapes.",
  segments: [
    { speaker: "SPEAKER_00", start: 0.0,  end: 4.5,  text: "Bonjour, nous allons commencer la réunion de lancement." },
    { speaker: "SPEAKER_01", start: 4.8,  end: 9.2,  text: "Merci. Commençons par les points à l'ordre du jour." },
    { speaker: "SPEAKER_00", start: 9.5,  end: 16.0, text: "Nous avons plusieurs sujets à aborder : le planning du sprint et les risques identifiés." },
    { speaker: "SPEAKER_02", start: 16.5, end: 22.0, text: "D'accord. Pour le planning, je suggère de commencer par les fonctionnalités critiques." },
    { speaker: "SPEAKER_01", start: 22.3, end: 28.0, text: "Tout à fait. Les fonctionnalités WebSocket en temps réel sont prioritaires pour ce sprint." },
    { speaker: "SPEAKER_00", start: 28.5, end: 35.0, text: "Parfait. Nous pouvons valider cette approche et passer aux prochaines étapes." },
  ],
  speakers: ["SPEAKER_00", "SPEAKER_01", "SPEAKER_02"],
};

/* ─── Page ────────────────────────────────────────────────────────────── */
const Transcript = () => {
  const { id } = useParams();
  const [transcript, setTranscript] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState("");
  const [copied, setCopied] = useState(false);
  const [selectedSpeaker, setSelectedSpeaker] = useState("all");

  useEffect(() => {
    // En production, appel API réel ; ici on utilise les données de démo
    const loadTranscript = async () => {
      try {
        // const data = await meetingService.getTranscription(id);
        await new Promise((r) => setTimeout(r, 600)); // Simule latence
        setTranscript(DEMO_TRANSCRIPT);
      } catch (err) {
        logger.error("[Transcript] Erreur chargement:", err.message);
        setError("Impossible de charger la transcription.");
      } finally {
        setLoading(false);
      }
    };
    loadTranscript();
  }, [id]);

  const filteredSegments = useMemo(() => {
    if (!transcript?.segments) return [];
    return transcript.segments.filter((s) => {
      const matchSpeaker = selectedSpeaker === "all" || s.speaker === selectedSpeaker;
      const matchSearch = !search || s.text.toLowerCase().includes(search.toLowerCase());
      return matchSpeaker && matchSearch;
    });
  }, [transcript, search, selectedSpeaker]);

  const handleCopy = useCallback(async () => {
    if (!transcript?.full_text) return;
    await navigator.clipboard.writeText(transcript.full_text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }, [transcript]);

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <Link to="/meetings" className="back-link">
            <ChevronLeft size={16} /> Retour aux réunions
          </Link>
          <h1 className="page-title">
            <FileText size={24} style={{ verticalAlign: "middle", marginRight: 8, color: "var(--accent-color)" }} />
            Transcription
          </h1>
          <p className="page-description">ID de réunion : <code className="code-inline">{id}</code></p>
        </div>
        <div className="page-header-actions">
          <button className="btn btn-secondary" onClick={handleCopy} aria-label="Copier le texte complet">
            {copied ? <CheckCheck size={15} style={{ color: "var(--success-color)" }} /> : <Copy size={15} />}
            {copied ? "Copié !" : "Copier le texte"}
          </button>
          <Link to={`/summary/${id}`} className="btn btn-primary">Voir le résumé →</Link>
        </div>
      </div>

      {loading ? (
        <div className="card" style={{ display: "flex", flexDirection: "column", gap: 16, padding: 24 }}>
          {[...Array(5)].map((_, i) => <Skeleton key={i} height={i % 2 === 0 ? "72px" : "56px"} />)}
        </div>
      ) : error ? (
        <EmptyState title="Erreur" description={error} />
      ) : (
        <div className="transcript-layout">
          {/* Sidebar de filtres */}
          <div className="transcript-sidebar">
            <div className="card">
              <h3 className="sidebar-section-title">Locuteurs</h3>
              <div className="speaker-filter-list">
                <button
                  className={`speaker-filter-item ${selectedSpeaker === "all" ? "active" : ""}`}
                  onClick={() => setSelectedSpeaker("all")}
                >
                  <span className="speaker-dot" style={{ background: "var(--text-muted)" }} />
                  Tous
                </button>
                {transcript.speakers.map((sp) => (
                  <button
                    key={sp}
                    className={`speaker-filter-item ${selectedSpeaker === sp ? "active" : ""}`}
                    onClick={() => setSelectedSpeaker(sp)}
                  >
                    <span className="speaker-dot" style={{ background: getSpeakerColor(sp) }} />
                    {sp}
                  </button>
                ))}
              </div>

              <h3 className="sidebar-section-title" style={{ marginTop: 20 }}>Statistiques</h3>
              <div className="stats-list">
                <div className="stat-row">
                  <span>Segments</span>
                  <strong>{transcript.segments.length}</strong>
                </div>
                <div className="stat-row">
                  <span>Locuteurs</span>
                  <strong>{transcript.speakers.length}</strong>
                </div>
                <div className="stat-row">
                  <span>Mots (estimé)</span>
                  <strong>{transcript.full_text.split(" ").length}</strong>
                </div>
              </div>
            </div>
          </div>

          {/* Zone principale */}
          <div className="transcript-main">
            {/* Barre de recherche */}
            <div className="search-wrapper" style={{ marginBottom: 16 }}>
              <Search size={16} className="search-icon" />
              <input
                className="search-input"
                type="search"
                placeholder="Rechercher dans la transcription..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                aria-label="Rechercher dans la transcription"
              />
            </div>

            {/* Segments */}
            <div className="transcript-segments">
              {filteredSegments.length === 0 ? (
                <EmptyState type="search" title="Aucun segment trouvé" description={`Aucun résultat pour "${search}".`} />
              ) : (
                filteredSegments.map((seg, i) => (
                  <TranscriptSegment
                    key={i}
                    segment={seg}
                    isHighlighted={search && seg.text.toLowerCase().includes(search.toLowerCase())}
                  />
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Transcript;
