import { useState, useCallback } from "react";
import workspaceService from "../services/workspace.service";
import logger from "../utils/logger";

export const useWorkspace = () => {
  const [workspaces, setWorkspaces] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchWorkspaces = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await workspaceService.getWorkspaces();
      setWorkspaces(data);
    } catch (err) {
      logger.error("[useWorkspace] fetchWorkspaces:", err.message);
      setError(err.message || "Erreur lors de la récupération des workspaces.");
    } finally {
      setLoading(false);
    }
  }, []);

  const createWorkspace = useCallback(async (data) => {
    setLoading(true);
    try {
      const newWs = await workspaceService.createWorkspace(data);
      await fetchWorkspaces();
      return newWs;
    } catch (err) {
      logger.error("[useWorkspace] createWorkspace:", err.message);
      setError(err.message || "Erreur de création.");
      throw err;
    } finally {
      setLoading(false);
    }
  }, [fetchWorkspaces]);

  const updateWorkspace = useCallback(async (id, data) => {
    setLoading(true);
    try {
      const updated = await workspaceService.updateWorkspace(id, data);
      await fetchWorkspaces();
      return updated;
    } catch (err) {
      logger.error("[useWorkspace] updateWorkspace:", err.message);
      setError(err.message || "Erreur de modification.");
      throw err;
    } finally {
      setLoading(false);
    }
  }, [fetchWorkspaces]);

  const deleteWorkspace = useCallback(async (id) => {
    setLoading(true);
    try {
      await workspaceService.deleteWorkspace(id);
      await fetchWorkspaces();
    } catch (err) {
      logger.error("[useWorkspace] deleteWorkspace:", err.message);
      setError(err.message || "Erreur de suppression.");
      throw err;
    } finally {
      setLoading(false);
    }
  }, [fetchWorkspaces]);

  return {
    workspaces,
    loading,
    error,
    fetchWorkspaces,
    createWorkspace,
    updateWorkspace,
    deleteWorkspace
  };
};

export default useWorkspace;
