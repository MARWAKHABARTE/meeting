import { useState, useCallback } from "react";
import ragService from "../services/rag.service";
import logger from "../utils/logger";

/**
 * Hook gérant la conversation RAG avec historique et sources.
 */
export const useRAG = (meetingId) => {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const sendMessage = useCallback(async (question) => {
    if (!question?.trim() || !meetingId) return;

    // Ajout optimiste du message utilisateur
    const userMessage = { role: "user", content: question, timestamp: new Date() };
    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);
    setError(null);

    try {
      const response = await ragService.query(meetingId, question);
      const assistantMessage = {
        role: "assistant",
        content: response.answer || "Aucune réponse générée.",
        sources: response.sources || [],
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      logger.error("[useRAG] sendMessage:", err.message);
      const errorMsg = err.response?.data?.detail || "Erreur lors de la génération de la réponse.";
      setError(errorMsg);
      // Ajout d'un message d'erreur dans la conversation
      setMessages((prev) => [
        ...prev,
        { role: "error", content: errorMsg, timestamp: new Date() },
      ]);
    } finally {
      setLoading(false);
    }
  }, [meetingId]);

  const clearConversation = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  return { messages, loading, error, sendMessage, clearConversation };
};

export default useRAG;
