import { useState, useCallback } from "react";
import meetingService from "../services/meeting.service";
import MeetingStorage from "../utils/MeetingStorage";
import logger from "../utils/logger";

/**
 * Hook encapsulant la logique de chargement et traitement des réunions.
 * Aucune logique métier ici — uniquement la communication HTTP.
 */
export const useMeetings = () => {
  const [meetings, setMeetings] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchMeetings = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const stored = MeetingStorage.getMeetings();
      setMeetings(stored);
    } catch (err) {
      logger.error("[useMeetings] fetchMeetings:", err.message);
      setError(err.message || "Erreur lors du chargement des réunions.");
    } finally {
      setLoading(false);
    }
  }, []);

  const startTranscription = useCallback(async (meetingId) => {
    try {
      const result = await meetingService.startTranscription(meetingId);
      logger.info(`[useMeetings] Transcription démarrée pour ${meetingId}`);
      return result;
    } catch (err) {
      logger.error("[useMeetings] startTranscription:", err.message);
      throw err;
    }
  }, []);

  const startSummary = useCallback(async (meetingId) => {
    try {
      const result = await meetingService.startSummary(meetingId);
      logger.info(`[useMeetings] Résumé NLP démarré pour ${meetingId}`);
      return result;
    } catch (err) {
      logger.error("[useMeetings] startSummary:", err.message);
      throw err;
    }
  }, []);

  return { meetings, loading, error, fetchMeetings, startTranscription, startSummary };
};

export default useMeetings;
