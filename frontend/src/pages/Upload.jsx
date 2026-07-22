import React, { useState, useCallback } from "react";
import { useUpload } from "../hooks/useUpload";
import { useMeetingProgress } from "../hooks/useMeetingProgress";
import { Upload as UploadIcon, FileAudio, CheckCircle, AlertTriangle, X, Play, Loader } from "lucide-react";
import { MeetingProgress } from "../components/MeetingProgress";
import meetingService from "../services/meeting.service";
import MeetingStorage from "../utils/MeetingStorage";
import logger from "../utils/logger";

const FORMAT_LABELS = ["MP3", "WAV", "OGG", "FLAC", "MP4 Audio"];

const formatSize = (bytes) => {
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} Ko`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} Mo`;
};

/* ─── Zone de drop ─────────────────────────────────────────────────────── */
const DropZone = ({ onFileSelected, disabled }) => {
  const inputRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setIsDragging(false);
    if (disabled) return;
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) onFileSelected(droppedFile);
  }, [onFileSelected, disabled]);

  const handleDragOver = (e) => { e.preventDefault(); setIsDragging(true); };
  const handleDragLeave = () => setIsDragging(false);

  return (
    <div
      className={`drop-zone ${isDragging ? "drop-zone--dragging" : ""} ${disabled ? "drop-zone--disabled" : ""}`}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onClick={() => !disabled && inputRef.current?.click()}
      role="button"
      tabIndex={disabled ? -1 : 0}
      aria-label="Zone de dépôt de fichier audio"
      onKeyDown={(e) => e.key === "Enter" && !disabled && inputRef.current?.click()}
    >
      <input
        ref={inputRef}
        type="file"
        accept="audio/*,video/mp4"
        style={{ display: "none" }}
        onChange={(e) => { const f = e.target.files[0]; if (f) onFileSelected(f); e.target.value = ""; }}
        aria-hidden="true"
      />
      <div className="drop-zone-content">
        <div className={`drop-zone-icon ${isDragging ? "drop-zone-icon--active" : ""}`}>
          <UploadIcon size={40} strokeWidth={1.5} />
        </div>
        <p className="drop-zone-primary">
          {isDragging ? "Déposez le fichier ici" : "Glissez-déposez votre fichier audio"}
        </p>
        <p className="drop-zone-secondary">ou <span className="link-accent">cliquez pour parcourir</span></p>
        <div className="drop-zone-formats">
          {FORMAT_LABELS.map((f) => <span key={f} className="format-chip">{f}</span>)}
        </div>
        <p className="drop-zone-limit">Taille maximale : 500 Mo</p>
      </div>
    </div>
  );
};

/* ─── Aperçu du fichier ────────────────────────────────────────────────── */
const FilePreview = ({ file, onRemove }) => (
  <div className="file-preview">
    <div className="file-preview-icon"><FileAudio size={28} /></div>
    <div className="file-preview-info">
      <div className="file-preview-name">{file.name}</div>
      <div className="file-preview-meta">{formatSize(file.size)} · {file.type || "audio"}</div>
    </div>
    <button className="file-preview-remove" onClick={onRemove} aria-label="Retirer le fichier">
      <X size={18} />
    </button>
  </div>
);

/* ─── Barre de progression ─────────────────────────────────────────────── */
const ProgressBar = ({ percent, label }) => (
  <div className="progress-wrapper">
    <div className="progress-header">
      <span className="progress-label">{label}</span>
      <span className="progress-percent">{percent}%</span>
    </div>
    <div className="progress-track">
      <div className="progress-bar" style={{ width: `${percent}%` }} role="progressbar" aria-valuenow={percent} aria-valuemin={0} aria-valuemax={100} />
    </div>
  </div>
);

/* ─── Page Upload ──────────────────────────────────────────────────────── */
const Upload = () => {
  const {
    file, uploadProgress, uploadResult, status, error,
    selectFile, upload, reset, maxSizeMB,
  } = useUpload();

  const [uploadedMeetingId, setUploadedMeetingId] = useState(null);

  const handleFileSelected = useCallback((f) => { selectFile(f); }, [selectFile]);

  const handleUpload = useCallback(async () => {
    try {
      const result = await upload();
      const newMeeting = MeetingStorage.addUploadedMeeting(file?.name || "Nouvel Enregistrement");
      setUploadedMeetingId(newMeeting.id);
      
      // Déclenchement automatique du pipeline de transcription & analyse NLP
      try {
        await meetingService.startTranscription(newMeeting.id);
      } catch (e) {
        logger.warn("[Upload] Démarrage transcription automatique:", e.message);
      }
    } catch { /* error déjà géré dans le hook */ }
  }, [upload]);

  const isIdle     = status === "idle";
  const isUploading = status === "uploading";
  const isDone     = status === "done";
  const isError    = status === "error";

  return (
    <div className="page page--centered-content">
      <div className="page-header">
        <div>
          <h1 className="page-title">
            <UploadIcon size={24} style={{ verticalAlign: "middle", marginRight: 8, color: "var(--accent-color)" }} />
            Uploader un enregistrement
          </h1>
          <p className="page-description">
            Déposez votre fichier audio pour démarrer le pipeline d'analyse IA complète.
          </p>
        </div>
      </div>

      <div className="upload-layout">
        {/* Panneau gauche : upload */}
        <div className="card upload-panel">

          {/* Succès */}
          {isDone && (
            <div className="upload-success">
              <CheckCircle size={52} className="upload-success-icon" />
              <h2 className="upload-success-title">Upload réussi !</h2>
              <p className="upload-success-desc">
                Votre fichier <strong>{file?.name}</strong> a été envoyé avec succès.
              </p>
              {uploadResult?.url && (
                <a href={uploadResult.url} target="_blank" rel="noopener noreferrer" className="btn btn-secondary btn-sm">
                  Voir le fichier
                </a>
              )}
              <button className="btn btn-primary" onClick={reset} style={{ marginTop: 8 }}>
                Uploader un autre fichier
              </button>
            </div>
          )}

          {/* Zone de dépôt */}
          {!isDone && (
            <>
              <DropZone onFileSelected={handleFileSelected} disabled={isUploading} />

              {/* Erreur de validation */}
              {error && (
                <div className="alert alert-error" role="alert">
                  <AlertTriangle size={16} />
                  {error}
                </div>
              )}

              {/* Aperçu du fichier sélectionné */}
              {file && !isUploading && (
                <FilePreview file={file} onRemove={reset} />
              )}

              {/* Progression de l'upload */}
              {isUploading && (
                <ProgressBar percent={uploadProgress} label="Upload en cours..." />
              )}

              {/* Bouton Upload */}
              {file && !isUploading && (
                <button
                  className="btn btn-primary btn-full"
                  onClick={handleUpload}
                  disabled={isUploading}
                  aria-busy={isUploading}
                >
                  {isUploading
                    ? <><Loader size={16} className="spin" /> Envoi en cours...</>
                    : <><Play size={16} /> Lancer l'analyse IA</>
                  }
                </button>
              )}
            </>
          )}
        </div>

        {/* Panneau droit : suivi pipeline */}
        <div className="upload-side">
          <div className="card">
            <div className="card-header">
              <h2 className="card-title">Suivi du pipeline IA</h2>
            </div>
            <p className="card-description">
              Une fois le fichier uploadé, suivez ici la progression en temps réel de chaque étape d'analyse.
            </p>
            <MeetingProgress meetingId={uploadedMeetingId} />
          </div>

          {/* Guide des formats */}
          <div className="card info-card">
            <h3 className="info-card-title">Formats supportés</h3>
            <ul className="format-list">
              {[
                { format: "MP3", desc: "Audio MPEG" },
                { format: "WAV", desc: "Waveform Audio" },
                { format: "OGG", desc: "Ogg Vorbis" },
                { format: "FLAC", desc: "Lossless Compression" },
                { format: "MP4", desc: "MPEG-4 Audio/Video" },
              ].map(({ format, desc }) => (
                <li key={format} className="format-list-item">
                  <span className="format-chip">{format}</span>
                  <span className="format-list-desc">{desc}</span>
                </li>
              ))}
            </ul>
            <p className="info-card-note">Taille maximale : {maxSizeMB} Mo par fichier.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Upload;
