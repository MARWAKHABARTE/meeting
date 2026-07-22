"""
Générateur de résumés NLP structurés via Ollama.
"""
import json
import logging
from app.ai.llm.ollama_client import OllamaClient
from app.ai.llm.prompt_builder import PromptBuilder
from app.ai.schemas.summary import SummaryResult, DecisionSchema, ActionItemSchema
from app.ai.exceptions import SummaryException

logger = logging.getLogger("meeting_ai")


class SummaryGenerator:
    """
    Génère un résumé NLP structuré d'une réunion à partir de sa transcription.
    Utilise OllamaClient pour l'inférence et valide la réponse avec Pydantic.
    """

    def __init__(self):
        self._client = OllamaClient()

    def generate(self, meeting_id: str, transcript_text: str) -> SummaryResult:
        """
        Génère le résumé complet d'une réunion.
        :param meeting_id: ID de la réunion.
        :param transcript_text: Texte de la transcription brute.
        :return: Objet SummaryResult validé par Pydantic.
        :raises SummaryException: En cas d'erreur d'inférence ou de parsing.
        """
        logger.info(f"[SummaryGenerator] Génération du résumé pour la réunion '{meeting_id}'...")
        try:
            prompt = PromptBuilder.build_summary_prompt(transcript_text)
            raw_response = self._client.generate(prompt)

            # Nettoyage du JSON (Ollama peut parfois ajouter du texte autour)
            raw_response = raw_response.strip()
            if "```json" in raw_response:
                raw_response = raw_response.split("```json")[1].split("```")[0].strip()
            elif "```" in raw_response:
                raw_response = raw_response.split("```")[1].split("```")[0].strip()

            data = json.loads(raw_response)

            result = SummaryResult(
                meeting_id=meeting_id,
                summary=data.get("summary", ""),
                decisions=[
                    DecisionSchema(content=d.get("content", ""))
                    for d in data.get("decisions", [])
                ],
                action_items=[
                    ActionItemSchema(
                        description=a.get("description", ""),
                        assignee=a.get("assignee")
                    )
                    for a in data.get("action_items", [])
                ],
                participants=data.get("participants", []),
                topics=data.get("topics", []),
                key_points=data.get("key_points", [])
            )
            logger.info(
                f"[SummaryGenerator] Résumé généré avec succès — "
                f"{len(result.decisions)} décisions, {len(result.action_items)} actions."
            )
            return result

        except json.JSONDecodeError as e:
            logger.error(f"[SummaryGenerator] Erreur de parsing JSON : {e}")
            raise SummaryException(f"Le LLM n'a pas retourné un JSON valide : {e}")
        except Exception as e:
            logger.error(f"[SummaryGenerator] Erreur inattendue : {e}")
            raise SummaryException(str(e))
