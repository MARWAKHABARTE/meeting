import React, { useEffect } from "react";
import { useReport } from "../hooks/useReport";
import { FileText, Download, BarChart2, Calendar, FileType } from "lucide-react";
import { Skeleton } from "../components/Skeleton";
import { EmptyState } from "../components/EmptyState";
import { StatusBadge } from "../components/StatusBadge";

const DEMO_REPORTS = [
  { id: "rep-1", title: "Rapport Synthèse Executif — Sprint 10", meeting_id: "meeting-session-1", type: "PDF", created_at: new Date().toISOString() },
  { id: "rep-2", title: "Compte Rendu & Actions — Lancement Project", meeting_id: "meeting-session-2", type: "TXT", created_at: new Date().toISOString() },
  { id: "rep-3", title: "Analyse Sémantique & NLP — Comité Technique", meeting_id: "meeting-session-3", type: "PDF", created_at: new Date().toISOString() },
];

export const Reports = () => {
  const { reports: apiReports, loading, error, fetchReports, downloadReport } = useReport();

  useEffect(() => {
    fetchReports();
  }, [fetchReports]);

  const reports = (apiReports && apiReports.length > 0) ? apiReports : DEMO_REPORTS;

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1 className="page-title">
            <BarChart2 size={24} style={{ verticalAlign: "middle", marginRight: 8, color: "var(--accent-color)" }} />
            Rapports & Statistiques
          </h1>
          <p className="page-description">
            Visualisez les données d'analyse et exportez les rapports de synthèse au format PDF ou TXT.
          </p>
        </div>
      </div>

      {loading ? (
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {[...Array(3)].map((_, i) => <Skeleton key={i} height="80px" />)}
        </div>
      ) : error ? (
        <EmptyState title="Erreur" description={error} />
      ) : (
        <div className="card table-card">
          <div className="table-scroll">
            <table className="data-table">
              <thead>
                <tr>
                  <th className="table-th">Rapport</th>
                  <th className="table-th">Date</th>
                  <th className="table-th">Format</th>
                  <th className="table-th">ID Réunion</th>
                  <th className="table-th">Statut</th>
                  <th className="table-th">Actions</th>
                </tr>
              </thead>
              <tbody>
                {reports.map((rep) => (
                  <tr key={rep.id} className="table-row">
                    <td className="table-cell">
                      <div className="meeting-title-cell">
                        <div className="meeting-icon" style={{ background: "rgba(139, 92, 246, 0.12)", color: "#8b5cf6" }}>
                          <FileText size={16} />
                        </div>
                        <span className="meeting-name">{rep.title}</span>
                      </div>
                    </td>
                    <td className="table-cell table-cell-secondary">
                      <Calendar size={12} style={{ marginRight: 6 }} />
                      {new Date(rep.created_at).toLocaleDateString()}
                    </td>
                    <td className="table-cell table-cell-secondary">
                      <FileType size={12} style={{ marginRight: 6 }} />
                      {rep.type}
                    </td>
                    <td className="table-cell table-cell-secondary">
                      <code className="code-inline">{rep.meeting_id}</code>
                    </td>
                    <td className="table-cell">
                      <StatusBadge status="completed" />
                    </td>
                    <td className="table-cell">
                      <div className="row-actions">
                        <button
                          className="btn btn-xs btn-primary"
                          onClick={() => downloadReport(rep.meeting_id, rep.type.toLowerCase())}
                        >
                          <Download size={12} /> Télécharger
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default Reports;
