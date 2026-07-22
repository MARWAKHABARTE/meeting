"""
Couche d'abstraction ChromaDB (VectorStore).
Toutes les opérations sur la base vectorielle passent UNIQUEMENT par cette classe.
Aucun composant ne doit appeler ChromaDB directement.
"""
import threading
import logging
from app.core.settings import settings
from app.ai.embeddings.embedding_model import EmbeddingModelProvider
from app.ai.exceptions import VectorStoreException

logger = logging.getLogger("meeting_ai")


class _SentenceTransformerEmbeddingFn:
    """
    Fonction d'embedding compatible avec l'interface ChromaDB.
    Délègue le calcul au singleton EmbeddingModelProvider.
    """
    def __call__(self, input: list[str]) -> list[list[float]]:
        return EmbeddingModelProvider.encode(input)


class VectorStore:
    """
    Singleton thread-safe encapsulant le client ChromaDB persistant.
    Expose uniquement les opérations nécessaires : create, delete, upsert, search.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    instance = super().__new__(cls)
                    instance._client = None
                    instance._embedding_fn = _SentenceTransformerEmbeddingFn()
                    cls._instance = instance
        return cls._instance

    def _get_client(self):
        """Initialise le client ChromaDB persistant au premier accès (Lazy Loading)."""
        if self._client is None:
            try:
                import chromadb
                self._client = chromadb.PersistentClient(
                    path=settings.CHROMA_PERSIST_DIRECTORY
                )
                logger.info(
                    f"[VectorStore] Client ChromaDB initialisé dans "
                    f"'{settings.CHROMA_PERSIST_DIRECTORY}'."
                )
            except Exception as e:
                logger.error(f"[VectorStore] Échec d'initialisation ChromaDB : {e}")
                raise VectorStoreException(f"Impossible d'initialiser ChromaDB : {e}")
        return self._client

    def create_collection(self, name: str):
        """
        Crée ou récupère une collection ChromaDB existante.
        :param name: Nom de la collection.
        """
        try:
            client = self._get_client()
            collection = client.get_or_create_collection(
                name=name,
                embedding_function=self._embedding_fn
            )
            logger.info(f"[VectorStore] Collection '{name}' prête.")
            return collection
        except VectorStoreException:
            raise
        except Exception as e:
            raise VectorStoreException(f"Erreur lors de la création de la collection : {e}")

    def delete_collection(self, name: str):
        """Supprime une collection et toutes ses données."""
        try:
            client = self._get_client()
            client.delete_collection(name=name)
            logger.info(f"[VectorStore] Collection '{name}' supprimée.")
        except Exception as e:
            raise VectorStoreException(f"Erreur lors de la suppression de la collection : {e}")

    def upsert_documents(
        self,
        collection_name: str,
        ids: list[str],
        documents: list[str],
        metadatas: list[dict],
    ):
        """
        Insère ou met à jour des documents dans la collection.
        :param collection_name: Nom de la collection cible.
        :param ids: Identifiants uniques par document.
        :param documents: Textes à vectoriser et indexer.
        :param metadatas: Métadonnées associées à chaque document.
        """
        try:
            collection = self.create_collection(collection_name)
            collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
            logger.info(
                f"[VectorStore] {len(documents)} documents indexés dans '{collection_name}'."
            )
        except VectorStoreException:
            raise
        except Exception as e:
            raise VectorStoreException(f"Erreur lors de l'indexation des documents : {e}")

    def delete_documents(self, collection_name: str, ids: list[str]):
        """Supprime des documents par leurs identifiants."""
        try:
            collection = self.create_collection(collection_name)
            collection.delete(ids=ids)
            logger.info(
                f"[VectorStore] {len(ids)} documents supprimés de '{collection_name}'."
            )
        except VectorStoreException:
            raise
        except Exception as e:
            raise VectorStoreException(f"Erreur lors de la suppression des documents : {e}")

    def search(
        self,
        collection_name: str,
        query_text: str,
        top_k: int | None = None,
    ) -> list[dict]:
        """
        Recherche sémantique des documents les plus proches.
        :param collection_name: Nom de la collection à interroger.
        :param query_text: Texte de la requête utilisateur.
        :param top_k: Nombre maximum de résultats à retourner.
        :return: Liste de dicts {"content": str, "metadata": dict, "distance": float}.
        """
        n = top_k or settings.RAG_TOP_K
        try:
            collection = self.create_collection(collection_name)
            results = collection.query(
                query_texts=[query_text],
                n_results=n,
                include=["documents", "metadatas", "distances"]
            )
            documents = results.get("documents", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]
            distances = results.get("distances", [[]])[0]

            formatted = [
                {"content": doc, "metadata": meta, "distance": dist}
                for doc, meta, dist in zip(documents, metadatas, distances)
            ]
            logger.info(
                f"[VectorStore] Recherche dans '{collection_name}' — "
                f"{len(formatted)} résultats retournés."
            )
            return formatted

        except VectorStoreException:
            raise
        except Exception as e:
            raise VectorStoreException(f"Erreur lors de la recherche vectorielle : {e}")
