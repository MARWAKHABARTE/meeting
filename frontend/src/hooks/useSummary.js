import { useState, useCallback } from "react";
import meetingService from "../services/meeting.service";
import logger from "../utils/logger";

/**
 * Hook gérant la récupération et la présentation du résumé NLP.
 */
export const useSummary = (meetingId) => {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchSummary = useCallback(async (id) => {
    const targetId = id || meetingId;
    if (!targetId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await meetingService.getSummary(targetId);
      setSummary(data);
    } catch (err) {
      if (err.response?.status === 404) {
        setSummary(null);
        setError("Aucun résumé disponible. Lancez d'abord l'analyse NLP.");
      } else {
        logger.error("[useSummary] fetchSummary:", err.message);
        setError(err.message || "Erreur lors du chargement du résumé.");
      }
    } finally {
      setLoading(false);
    }
  }, [meetingId]);

  const triggerSummary = useCallback(async (id) => {
    const targetId = id || meetingId;
    if (!targetId) return;
    try {
      const result = await meetingService.startSummary(targetId);
      return result;
    } catch (err) {
      logger.error("[useSummary] triggerSummary:", err.message);
      throw err;
    }
  }, [meetingId]);

  return { summary, loading, error, fetchSummary, triggerSummary };
};

export default useSummary;
