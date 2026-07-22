"""
Client REST centralisé pour le serveur Ollama.
Toute communication avec Ollama transite exclusivement par cette classe.
Aucun composant ne doit appeler Ollama directement.
"""
import threading
import logging
import httpx
from app.core.settings import settings
from app.ai.exceptions import OllamaUnavailable

logger = logging.getLogger("meeting_ai")


class OllamaClient:
    """
    Client HTTP thread-safe implémentant le pattern Singleton.
    Expose generate(), chat() et health() vers le serveur Ollama local.
    Bascule automatiquement sur un Mock si OLLAMA_MODEL = 'mock'.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    instance = super().__new__(cls)
                    instance._base_url = settings.OLLAMA_HOST.rstrip("/")
                    instance._model = settings.OLLAMA_MODEL
                    instance._timeout = float(settings.OLLAMA_TIMEOUT)
                    logger.info(
                        f"[OllamaClient] Initialisé — host: {instance._base_url}, "
                        f"model: {instance._model}"
                    )
                    cls._instance = instance
        return cls._instance

    @property
    def _is_mock(self) -> bool:
        """
        Active le mode mock uniquement si OLLAMA_MODEL vaut 'mock'.
        En développement, Ollama peut tourner localement — ne pas forcer le mock.
        """
        return self._model == "mock"

    def health(self) -> bool:
        """Vérifie si le serveur Ollama est accessible."""
        if self._is_mock:
            return True
        try:
            resp = httpx.get(f"{self._base_url}/", timeout=2.0)
            return resp.status_code == 200
        except Exception:
            return False

    def generate(self, prompt: str, **kwargs) -> str:
        """
        Génère une réponse textuelle à partir d'un prompt.
        :param prompt: Prompt complet envoyé au LLM.
        :return: Texte de la réponse générée.
        :raises OllamaUnavailable: En cas d'erreur de communication.
        """
        if self._is_mock:
            logger.info("[OllamaClient] Mode Mock — réponse simulée pour generate().")
            return self._mock_generate(prompt)

        url = f"{self._base_url}/api/generate"
        payload = {"model": self._model, "prompt": prompt, "stream": False, **kwargs}
        try:
            resp = httpx.post(url, json=payload, timeout=self._timeout)
            resp.raise_for_status()
            response_text = resp.json().get("response", "")
            logger.info(
                f"[OllamaClient] generate() — "
                f"{len(response_text)} caractères reçus."
            )
            return response_text
        except httpx.HTTPStatusError as e:
            logger.error(f"[OllamaClient] Erreur HTTP generate() : {e}")
            raise OllamaUnavailable(f"Ollama a renvoyé une erreur HTTP : {e}")
        except httpx.RequestError as e:
            logger.error(f"[OllamaClient] Erreur réseau generate() : {e}")
            raise OllamaUnavailable(f"Impossible de joindre Ollama : {e}")

    def chat(self, messages: list[dict], **kwargs) -> str:
        """
        Dialogue multi-tours avec le LLM.
        :param messages: Liste de messages au format [{"role": "user", "content": "..."}].
        :return: Réponse textuelle du LLM.
        :raises OllamaUnavailable: En cas d'erreur de communication.
        """
        if self._is_mock:
            logger.info("[OllamaClient] Mode Mock — réponse simulée pour chat().")
            return "Réponse simulée du pipeline RAG. Le contexte a bien été reçu."

        url = f"{self._base_url}/api/chat"
        payload = {"model": self._model, "messages": messages, "stream": False, **kwargs}
        try:
            resp = httpx.post(url, json=payload, timeout=self._timeout)
            resp.raise_for_status()
            result = resp.json()
            content = result.get("message", {}).get("content", "")
            logger.info(f"[OllamaClient] chat() — {len(content)} caractères reçus.")
            return content
        except httpx.HTTPStatusError as e:
            logger.error(f"[OllamaClient] Erreur HTTP chat() : {e}")
            raise OllamaUnavailable(f"Ollama a renvoyé une erreur HTTP : {e}")
        except httpx.RequestError as e:
            logger.error(f"[OllamaClient] Erreur réseau chat() : {e}")
            raise OllamaUnavailable(f"Impossible de joindre Ollama : {e}")

    # ──────────────────────────────────────────────────────────
    # Réponses Mock réalistes pour le développement local
    # ──────────────────────────────────────────────────────────
    def _mock_generate(self, prompt: str) -> str:
        """Retourne une réponse simulée structurée selon le type de prompt."""
        if "résumé" in prompt.lower() or "summary" in prompt.lower():
            return (
                '{"summary": "La réunion a porté sur la validation du Sprint 8 et '
                'les perspectives du Sprint 9.", '
                '"decisions": [{"content": "Adopter le pipeline IA Whisper + Pyannote."}], '
                '"action_items": [{"description": "Implémenter le module RAG", "assignee": "Équipe IA"}], '
                '"participants": ["Alice", "Bob", "Charlie"], '
                '"topics": ["Architecture IA", "Pipeline Celery", "Tests unitaires"], '
                '"key_points": ["Le pipeline Whisper fonctionne correctement.", '
                '"ChromaDB sera utilisé pour le RAG."]}'
            )
        if "sentiment" in prompt.lower():
            return '{"label": "positive", "score": 0.85, "explanation": "Le ton de la réunion est constructif et orienté solutions."}'
        return "Réponse simulée générique du LLM Ollama."
