import { useState, useCallback } from "react";
import reportService from "../services/report.service";
import logger from "../utils/logger";

export const useReport = () => {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchReports = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await reportService.getReports();
      setReports(data);
    } catch (err) {
      logger.error("[useReport] fetchReports:", err.message);
      setError(err.message || "Erreur de récupération des rapports.");
    } finally {
      setLoading(false);
    }
  }, []);

  const downloadReport = useCallback(async (meetingId, format) => {
    try {
      await reportService.downloadReport(meetingId, format);
    } catch (err) {
      logger.error("[useReport] downloadReport:", err.message);
      throw err;
    }
  }, []);

  return {
    reports,
    loading,
    error,
    fetchReports,
    downloadReport
  };
};

export default useReport;
