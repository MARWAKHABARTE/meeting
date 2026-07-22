"""
Composant de découpage sémantique de texte (Chunker).
Prépare les données textuelles pour l'indexation dans ChromaDB.
"""
import logging
from app.core.settings import settings

logger = logging.getLogger("meeting_ai")


class TextChunker:
    """
    Découpe un texte long en segments chevauchants de taille configurable.
    Le chevauchement (overlap) garantit la continuité sémantique entre chunks,
    ce qui améliore la qualité du RAG lors de la récupération documentaire.
    """

    def __init__(
        self,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
    ):
        self._chunk_size = chunk_size or settings.CHUNK_SIZE
        self._chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP

    def chunk(self, text: str, metadata: dict | None = None) -> list[dict]:
        """
        Découpe un texte en chunks avec métadonnées associées.
        :param text: Texte source à découper.
        :param metadata: Métadonnées partagées à attacher à chaque chunk (ex: meeting_id).
        :return: Liste de dictionnaires {"text": str, "metadata": dict}.
        """
        if not text or not text.strip():
            logger.warning("[TextChunker] Texte vide reçu — aucun chunk généré.")
            return []

        words = text.split()
        chunks = []
        step = max(1, self._chunk_size - self._chunk_overlap)
        meta = metadata or {}

        for i, start in enumerate(range(0, len(words), step)):
            chunk_words = words[start:start + self._chunk_size]
            chunk_text = " ".join(chunk_words).strip()
            if chunk_text:
                chunks.append({
                    "text": chunk_text,
                    "metadata": {**meta, "chunk_index": i}
                })

        logger.info(
            f"[TextChunker] Texte découpé en {len(chunks)} chunks "
            f"(taille: {self._chunk_size}, overlap: {self._chunk_overlap})."
        )
        return chunks
