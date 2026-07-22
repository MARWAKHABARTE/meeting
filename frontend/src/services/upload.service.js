import axiosInstance from "../api/axios";
import logger from "../utils/logger";

/**
 * Service gérant le téléversement de fichiers audio vers le backend MinIO.
 * Supporte la progression upload via XMLHttpRequest.
 */
class UploadService {
  /**
   * Envoie un fichier audio au backend avec suivi de progression.
   * @param {File} file - Fichier audio à uploader
   * @param {Function} onProgress - Callback (percent: number) => void
   * @returns {Promise<{name, size, url}>}
   */
  async uploadAudioFile(file, onProgress = null) {
    const formData = new FormData();
    formData.append("file", file);

    const config = {
      headers: { "Content-Type": "multipart/form-data" },
      timeout: 120000, // 2 minutes pour les gros fichiers
    };

    if (onProgress) {
      config.onUploadProgress = (progressEvent) => {
        const percent = Math.round((progressEvent.loaded * 100) / (progressEvent.total || 1));
        onProgress(percent);
      };
    }

    try {
      const res = await axiosInstance.post("/v1/storage/upload-test", formData, config);
      logger.info(`[UploadService] Fichier '${file.name}' uploadé avec succès.`);
      return res.data;
    } catch (err) {
      logger.error("[UploadService] Erreur d'upload:", err.message);
      throw err;
    }
  }

  /**
   * Vérifie la santé du stockage MinIO.
   */
  async checkStorageHealth() {
    const res = await axiosInstance.get("/v1/storage/health");
    return res.data;
  }
}

export default new UploadService();
