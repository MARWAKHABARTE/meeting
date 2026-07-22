"""
Générateur d'analyse de sentiment via Ollama.
"""
import json
import logging
from app.ai.llm.ollama_client import OllamaClient
from app.ai.llm.prompt_builder import PromptBuilder
from app.ai.schemas.sentiment import SentimentResult
from app.ai.exceptions import SummaryException

logger = logging.getLogger("meeting_ai")


class SentimentGenerator:
    """
    Analyse le sentiment global d'une réunion à partir de sa transcription.
    """

    def __init__(self):
        self._client = OllamaClient()

    def generate(self, meeting_id: str, transcript_text: str) -> SentimentResult:
        """
        Génère une analyse de sentiment.
        :param meeting_id: ID de la réunion.
        :param transcript_text: Texte de transcription brut.
        :return: Objet SentimentResult validé par Pydantic.
        :raises SummaryException: En cas d'erreur d'inférence ou de parsing JSON.
        """
        logger.info(
            f"[SentimentGenerator] Analyse de sentiment pour la réunion '{meeting_id}'..."
        )
        try:
            prompt = PromptBuilder.build_sentiment_prompt(transcript_text)
            raw_response = self._client.generate(prompt).strip()

            # Nettoyage du JSON si Ollama ajoute du Markdown
            if "```json" in raw_response:
                raw_response = raw_response.split("```json")[1].split("```")[0].strip()
            elif "```" in raw_response:
                raw_response = raw_response.split("```")[1].split("```")[0].strip()

            data = json.loads(raw_response)

            result = SentimentResult(
                meeting_id=meeting_id,
                label=data.get("label", "neutral"),
                score=float(data.get("score", 0.5)),
                explanation=data.get("explanation", "")
            )
            logger.info(
                f"[SentimentGenerator] Sentiment détecté : {result.label} "
                f"(score : {result.score:.2f})"
            )
            return result

        except json.JSONDecodeError as e:
            logger.error(f"[SentimentGenerator] Erreur de parsing JSON : {e}")
            raise SummaryException(f"Le LLM n'a pas retourné un JSON valide : {e}")
        except Exception as e:
            logger.error(f"[SentimentGenerator] Erreur inattendue : {e}")
            raise SummaryException(str(e))
