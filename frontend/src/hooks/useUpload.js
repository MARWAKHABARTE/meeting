import { useState, useCallback } from "react";
import uploadService from "../services/upload.service";
import meetingService from "../services/meeting.service";
import logger from "../utils/logger";

const ALLOWED_FORMATS = ["audio/mpeg", "audio/wav", "audio/ogg", "audio/flac", "audio/mp4", "video/mp4"];
const MAX_SIZE_MB = 500;

/**
 * Hook gérant la logique complète d'upload de fichier audio.
 * Validation, progression, déclenchement de la transcription.
 */
export const useUpload = () => {
  const [file, setFile] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadResult, setUploadResult] = useState(null);
  const [status, setStatus] = useState("idle"); // idle | validating | uploading | transcribing | done | error
  const [error, setError] = useState(null);
  const [taskId, setTaskId] = useState(null);

  const validateFile = useCallback((f) => {
    if (!f) return "Aucun fichier sélectionné.";
    if (!ALLOWED_FORMATS.includes(f.type)) {
      return `Format non supporté. Formats autorisés : MP3, WAV, OGG, FLAC, MP4.`;
    }
    if (f.size > MAX_SIZE_MB * 1024 * 1024) {
      return `Fichier trop volumineux. Maximum : ${MAX_SIZE_MB} MB.`;
    }
    return null;
  }, []);

  const selectFile = useCallback((f) => {
    const validationError = validateFile(f);
    if (validationError) {
      setError(validationError);
      setFile(null);
      return false;
    }
    setFile(f);
    setError(null);
    setStatus("idle");
    setUploadProgress(0);
    setUploadResult(null);
    return true;
  }, [validateFile]);

  const upload = useCallback(async () => {
    if (!file) {
      setError("Aucun fichier sélectionné.");
      return;
    }
    setError(null);
    setStatus("uploading");
    setUploadProgress(0);

    try {
      const result = await uploadService.uploadAudioFile(file, (percent) => {
        setUploadProgress(percent);
      });
      setUploadResult(result);
      setStatus("done");
      logger.info(`[useUpload] Upload réussi : ${file.name}`);
      return result;
    } catch (err) {
      logger.error("[useUpload] Erreur upload:", err.message);
      setError(err.response?.data?.detail || "Erreur lors de l'upload. Vérifiez votre connexion.");
      setStatus("error");
      throw err;
    }
  }, [file]);

  const reset = useCallback(() => {
    setFile(null);
    setUploadProgress(0);
    setUploadResult(null);
    setStatus("idle");
    setError(null);
    setTaskId(null);
  }, []);

  return {
    file,
    uploadProgress,
    uploadResult,
    status,
    error,
    taskId,
    allowedFormats: ALLOWED_FORMATS,
    maxSizeMB: MAX_SIZE_MB,
    selectFile,
    upload,
    reset,
  };
};

export default useUpload;
