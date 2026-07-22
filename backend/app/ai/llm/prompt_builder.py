"""
Constructeur de prompts centralisé pour l'ensemble du module LLM.
Aucun autre composant ne doit construire des chaînes de prompts en dur.
"""
from app.core.settings import settings


class PromptBuilder:
    """
    Générateur de prompts structurés pour les tâches NLP et RAG.
    Toutes les instructions système et utilisateurs passent par cette classe.
    """

    @staticmethod
    def build_summary_prompt(transcript_text: str) -> str:
        """
        Construit le prompt de résumé NLP complet pour une réunion.
        :param transcript_text: Texte de transcription brut de la réunion.
        :return: Prompt formaté prêt à être envoyé à Ollama.
        """
        return f"""Tu es un assistant expert en analyse de réunions professionnelles.

Voici la transcription complète d'une réunion :

---
{transcript_text}
---

Analyse cette réunion et réponds UNIQUEMENT avec un JSON valide respectant exactement ce format :
{{
  "summary": "Résumé concis de la réunion en 3 à 5 phrases.",
  "decisions": [{{"content": "Décision 1"}}, {{"content": "Décision 2"}}],
  "action_items": [{{"description": "Action 1", "assignee": "Nom ou null"}}],
  "participants": ["Participant 1", "Participant 2"],
  "topics": ["Sujet 1", "Sujet 2"],
  "key_points": ["Point clé 1", "Point clé 2"]
}}

Ne fournis que du JSON valide, sans aucun texte supplémentaire avant ou après.
"""

    @staticmethod
    def build_sentiment_prompt(transcript_text: str) -> str:
        """
        Construit le prompt d'analyse de sentiment d'une réunion.
        :param transcript_text: Texte de transcription brut.
        :return: Prompt formaté pour l'analyse de sentiment.
        """
        return f"""Tu es un expert en analyse psycholinguistique des réunions professionnelles.

Voici la transcription d'une réunion :

---
{transcript_text}
---

Analyse le sentiment global de cette réunion. Réponds UNIQUEMENT avec un JSON valide :
{{
  "label": "positive" | "neutral" | "negative",
  "score": 0.0 à 1.0,
  "explanation": "Explication concise du sentiment détecté."
}}

Ne fournis que du JSON valide, sans aucun texte supplémentaire.
"""

    @staticmethod
    def build_rag_prompt(question: str, context: str) -> str:
        """
        Construit le prompt RAG avec le contexte récupéré depuis ChromaDB.
        :param question: Question en langage naturel de l'utilisateur.
        :param context: Contexte documentaire assemblé par le ContextBuilder.
        :return: Prompt RAG formaté.
        """
        max_ctx = settings.MAX_CONTEXT_LENGTH
        truncated_context = context[:max_ctx] if len(context) > max_ctx else context

        return f"""Tu es un assistant expert en analyse de réunions. Réponds à la question en te basant UNIQUEMENT sur le contexte fourni.

CONTEXTE :
---
{truncated_context}
---

QUESTION : {question}

Règles :
- Réponds en français, de manière concise et directe.
- Si la réponse ne se trouve pas dans le contexte, dis-le clairement.
- Ne génère jamais d'informations inventées.

RÉPONSE :"""
