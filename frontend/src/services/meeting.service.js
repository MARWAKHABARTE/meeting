import axiosInstance from "../api/axios";
import logger from "../utils/logger";

/**
 * Service gérant tous les appels API liés aux réunions.
 * Aucune logique métier ici — uniquement la communication HTTP.
 */
class MeetingService {
  /**
   * Récupère la liste de toutes les réunions.
   * @returns {Promise<Array>}
   */
  async getMeetings() {
    try {
      const res = await axiosInstance.get("/v1/workers/health");
      logger.debug("[MeetingService] Réunions récupérées.");
      return res.data;
    } catch (err) {
      logger.error("[MeetingService] Erreur getMeetings:", err.message);
      throw err;
    }
  }

  /**
   * Récupère la transcription d'une réunion depuis la base.
   * @param {string} meetingId
   */
  async getTranscription(meetingId) {
    const res = await axiosInstance.get(`/v1/transcriptions/${meetingId}/result`);
    return res.data;
  }

  /**
   * Déclenche la transcription asynchrone d'une réunion.
   * @param {string} meetingId
   */
  async startTranscription(meetingId) {
    const res = await axiosInstance.post("/v1/transcriptions/start", { meeting_id: meetingId });
    return res.data;
  }

  /**
   * Vérifie le statut d'une tâche Celery.
   * @param {string} taskId
   */
  async getTaskStatus(taskId) {
    const res = await axiosInstance.get(`/v1/workers/tasks/${taskId}`);
    return res.data;
  }

  /**
   * Déclenche le pipeline NLP (résumé, sentiment, actions).
   * @param {string} meetingId
   */
  async startSummary(meetingId) {
    const res = await axiosInstance.post("/v1/summaries/start", { meeting_id: meetingId });
    return res.data;
  }

  /**
   * Récupère le résumé NLP complet d'une réunion.
   * @param {string} meetingId
   */
  async getSummary(meetingId) {
    const res = await axiosInstance.get(`/v1/summaries/${meetingId}`);
    return res.data;
  }
}

export default new MeetingService();
