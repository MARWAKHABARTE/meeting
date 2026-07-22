import axiosInstance from "../api/axios";
import logger from "../utils/logger";

/**
 * Service gérant les appels API liés au pipeline RAG (Question/Réponse).
 */
class RAGService {
  /**
   * Envoie une question et reçoit une réponse enrichie de sources.
   * @param {string} meetingId - ID de la réunion à interroger
   * @param {string} question - Question en langage naturel
   * @returns {Promise<{answer, sources, meeting_id}>}
   */
  async query(meetingId, question) {
    try {
      const res = await axiosInstance.post("/v1/rag/query", {
        meeting_id: meetingId,
        question,
      });
      logger.debug(`[RAGService] Réponse reçue pour la question: "${question.slice(0, 50)}"`);
      return res.data;
    } catch (err) {
      logger.error("[RAGService] Erreur query:", err.message);
      throw err;
    }
  }

  /**
   * Vérifie la santé des services RAG (Ollama + ChromaDB).
   */
  async checkHealth() {
    const res = await axiosInstance.get("/v1/rag/health");
    return res.data;
  }
}

export default new RAGService();
