import logger from "../utils/logger";

/**
 * Service pour la génération et le téléchargement des rapports de réunions (PDF/TXT mock).
 */
class ReportService {
  constructor() {
    this.storageKey = "meeting_ai_reports";
    this._initDemoData();
  }

  _initDemoData() {
    if (!localStorage.getItem(this.storageKey)) {
      const demo = [
        { id: "rep-1", title: "Rapport Sprint 10", meeting_id: "1", type: "PDF", created_at: new Date().toISOString() },
        { id: "rep-2", title: "Compte Rendu Hebdomadaire", meeting_id: "2", type: "TXT", created_at: new Date().toISOString() },
      ];
      localStorage.setItem(this.storageKey, JSON.stringify(demo));
    }
  }

  async getReports() {
    const list = JSON.parse(localStorage.getItem(this.storageKey) || "[]");
    return list;
  }

  async downloadReport(meetingId, format = "pdf") {
    logger.info(`[ReportService] Téléchargement du rapport pour le meeting ${meetingId} au format ${format}`);
    // Simuler le téléchargement d'un fichier text/plain
    const content = `Meeting AI Platform - Rapport de Réunion\nID: ${meetingId}\nDate: ${new Date().toLocaleDateString()}\n\nRésumé:\nCeci est le contenu du rapport généré automatiquement.`;
    const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `rapport-${meetingId}.${format}`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
}

export default new ReportService();
