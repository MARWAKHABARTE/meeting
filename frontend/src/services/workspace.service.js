import logger from "../utils/logger";

/**
 * Service mock pour la gestion des Workspaces (stockage localStorage).
 * Permet de respecter SOLID et Clean Architecture en simulant l'API.
 */
class WorkspaceService {
  constructor() {
    this.storageKey = "meeting_ai_workspaces";
    this._initDemoData();
  }

  _initDemoData() {
    if (!localStorage.getItem(this.storageKey)) {
      const demo = [
        { id: "ws-1", name: "Équipe Produit", description: "Workspace pour le design et le product management", created_at: new Date().toISOString() },
        { id: "ws-2", name: "R&D Technique", description: "Workspace pour le développement backend et IA", created_at: new Date().toISOString() },
      ];
      localStorage.setItem(this.storageKey, JSON.stringify(demo));
    }
  }

  async getWorkspaces() {
    const list = JSON.parse(localStorage.getItem(this.storageKey) || "[]");
    logger.debug("[WorkspaceService] Liste récupérée");
    return list;
  }

  async getWorkspaceDetails(id) {
    const list = await this.getWorkspaces();
    return list.find(w => w.id === id) || null;
  }

  async createWorkspace(data) {
    const list = await this.getWorkspaces();
    const newWs = {
      id: `ws-${Math.random().toString(36).substr(2, 9)}`,
      name: data.name,
      description: data.description || "",
      created_at: new Date().toISOString()
    };
    list.push(newWs);
    localStorage.setItem(this.storageKey, JSON.stringify(list));
    logger.info(`[WorkspaceService] Workspace créé: ${newWs.name}`);
    return newWs;
  }

  async updateWorkspace(id, data) {
    const list = await this.getWorkspaces();
    const idx = list.findIndex(w => w.id === id);
    if (idx === -1) throw new Error("Workspace introuvable");
    list[idx] = { ...list[idx], ...data };
    localStorage.setItem(this.storageKey, JSON.stringify(list));
    logger.info(`[WorkspaceService] Workspace mis à jour: ${list[idx].name}`);
    return list[idx];
  }

  async deleteWorkspace(id) {
    const list = await this.getWorkspaces();
    const filtered = list.filter(w => w.id !== id);
    localStorage.setItem(this.storageKey, JSON.stringify(filtered));
    logger.info(`[WorkspaceService] Workspace supprimé: ${id}`);
    return true;
  }
}

export default new WorkspaceService();
