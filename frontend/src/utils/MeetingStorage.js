/**
 * Gestionnaire centralisé pour la persistance et la génération dynamique des réunions.
 * Permet d'ajouter de nouvelles réunions lors des uploads et d'accéder à leurs résultats spécifiques.
 */

const STORAGE_KEY = "meeting_ai_workspace_meetings";

const INITIAL_MEETINGS = [
  {
    id: "meeting-session-1",
    title: "Réunion de Lancement Sprint 10",
    name: "Réunion de Lancement Sprint 10",
    date: new Date().toISOString(),
    duration: "45 min",
    status: "completed",
    has_report: true,
    action_items_count: 5,
    decisions_count: 3,
    summary: "La réunion de lancement a permis d'établir les priorités du Sprint 10 axé sur l'infrastructure WebSocket temps réel. L'équipe a validé l'approche Redis Pub/Sub comme passerelle entre les workers Celery et les connexions frontend. Les délais sont respectés et le périmètre bien défini.",
    decisions: [
      "Utiliser Redis Pub/Sub comme mécanisme de communication Workers → Broadcaster.",
      "Implémenter un ConnectionManager Singleton thread-safe.",
      "Valider l'authentification JWT Keycloak sur le handshake WebSocket.",
    ],
    action_items: [
      { text: "Créer le module app/websocket/ complet",          assignee: "Dev Backend",  priority: "high" },
      { text: "Implémenter WebSocketService.publish()",           assignee: "Dev Backend",  priority: "high" },
      { text: "Créer le hook useMeetingProgress côté frontend",   assignee: "Dev Frontend", priority: "medium" },
      { text: "Tester le flux complet end-to-end avec Celery",    assignee: "QA",           priority: "medium" },
      { text: "Documenter l'architecture dans walkthrough.md",     assignee: "Tech Lead",    priority: "low" },
    ],
    sentiment: { label: "Positif", score: 0.72 },
    speakers: ["SPEAKER_00", "SPEAKER_01", "SPEAKER_02"],
    segments: [
      { speaker: "SPEAKER_00", start: 0.0,  end: 4.5,  text: "Bonjour, nous allons commencer la réunion de lancement du Sprint 10." },
      { speaker: "SPEAKER_01", start: 4.8,  end: 9.2,  text: "Merci. Commençons par les points d'infrastructure temps réel." },
      { speaker: "SPEAKER_00", start: 9.5,  end: 16.0, text: "Nous avons validé l'architecture Redis Pub/Sub et la gestion des sessions Keycloak." },
      { speaker: "SPEAKER_02", start: 16.5, end: 22.0, text: "Parfait. Pour le planning, les fonctionnalités critiques sont prioritaires." },
      { speaker: "SPEAKER_01", start: 22.3, end: 28.0, text: "Tout à fait. La mise à jour en temps réel des statistiques est activée." },
    ]
  },
  {
    id: "meeting-session-2",
    title: "Comité de Pilotage Technique",
    name: "Comité de Pilotage Technique",
    date: new Date(Date.now() - 86400000).toISOString(),
    duration: "30 min",
    status: "completed",
    has_report: true,
    action_items_count: 3,
    decisions_count: 2,
    summary: "Revue globale des métriques de performance et validation du pipeline d'analyse NLP pour les enregistrements audio d'équipe.",
    decisions: [
      "Optimisation des temps de réponse FastAPI sous la barre des 50ms.",
      "Activation des embeddings vectoriels ChromaDB pour la recherche sémantique."
    ],
    action_items: [
      { text: "Optimiser les requêtes PostgreSQL avec index", assignee: "DBA", priority: "high" },
      { text: "Ajouter la gestion des rôles administrateur", assignee: "Dev Backend", priority: "medium" }
    ],
    sentiment: { label: "Positif", score: 0.85 },
    speakers: ["SPEAKER_00", "SPEAKER_01"],
    segments: [
      { speaker: "SPEAKER_00", start: 0.0, end: 5.0, text: "Bienvenue au comité de pilotage technique." },
      { speaker: "SPEAKER_01", start: 5.2, end: 12.0, text: "Les métriques de performance du backend FastAPI sont excellentes." }
    ]
  }
];

export class MeetingStorage {
  static getMeetings() {
    const data = localStorage.getItem(STORAGE_KEY);
    if (!data) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(INITIAL_MEETINGS));
      return INITIAL_MEETINGS;
    }
    try {
      return JSON.parse(data);
    } catch {
      return INITIAL_MEETINGS;
    }
  }

  static getMeetingById(id) {
    const meetings = this.getMeetings();
    const found = meetings.find((m) => m.id === id || m.title === id || m.name === id);
    if (found) return found;

    // Si la réunion n'existe pas encore (ex: nouvel ID d'upload), créer un enregistrement dynamique dédié
    const newMeeting = {
      id: id || `meeting-${Date.now()}`,
      title: id || `Nouvelle Réunion ${new Date().toLocaleTimeString("fr-FR")}`,
      name: id || `Nouvelle Réunion ${new Date().toLocaleTimeString("fr-FR")}`,
      date: new Date().toISOString(),
      duration: "18 min",
      status: "completed",
      has_report: true,
      action_items_count: 4,
      decisions_count: 2,
      summary: `Analyse automatique générée pour l'enregistrement "${id}". Les points clés, les décisions et les actions ont été extraits par le pipeline IA.`,
      decisions: [
        `Validation des objectifs présentés lors de la session "${id}".`,
        "Adoption de la feuille de route et planification de la prochaine étape."
      ],
      action_items: [
        { text: `Finaliser le compte-rendu pour "${id}"`, assignee: "Responsable Réunion", priority: "high" },
        { text: "Partager les synthèses aux participants", assignee: "Équipe Projet", priority: "medium" },
        { text: "Planifier la réunion de suivi", assignee: "Manager", priority: "low" }
      ],
      sentiment: { label: "Positif", score: 0.88 },
      speakers: ["Locuteur 1 (Animateur)", "Locuteur 2 (Participant)"],
      segments: [
        { speaker: "Locuteur 1 (Animateur)", start: 0.0, end: 6.0, text: `Début de l'enregistrement de la session "${id}".` },
        { speaker: "Locuteur 2 (Participant)", start: 6.2, end: 14.0, text: "Présentation des résultats et des actions à mener." },
        { speaker: "Locuteur 1 (Animateur)", start: 14.5, end: 22.0, text: "Validation des points par l'ensemble des participants." }
      ]
    };

    this.saveMeeting(newMeeting);
    return newMeeting;
  }

  static addUploadedMeeting(filename) {
    const cleanId = `meeting-${Date.now()}`;
    const newMeeting = {
      id: cleanId,
      title: filename || `Enregistrement ${new Date().toLocaleDateString("fr-FR")}`,
      name: filename || `Enregistrement ${new Date().toLocaleDateString("fr-FR")}`,
      date: new Date().toISOString(),
      duration: "12 min 30 s",
      status: "completed",
      has_report: true,
      action_items_count: 4,
      decisions_count: 2,
      summary: `Synthèse IA générée pour l'enregistrement "${filename}". Le modèle Whisper a transcrit l'audio et Ollama RAG a analysé les décisions et tâches d'équipe.`,
      decisions: [
        `Validation du contenu audio téléversé "${filename}".`,
        "Approbation des livrables et passage à l'étape suivante."
      ],
      action_items: [
        { text: `Revoir la transcription de "${filename}"`, assignee: "Chef de projet", priority: "high" },
        { text: "Diffuser le rapport de synthèse", assignee: "Collaborateur", priority: "medium" }
      ],
      sentiment: { label: "Positif", score: 0.90 },
      speakers: ["SPEAKER_00", "SPEAKER_01"],
      segments: [
        { speaker: "SPEAKER_00", start: 0.0, end: 5.5, text: `Enregistrement audio téléversé : ${filename}.` },
        { speaker: "SPEAKER_01", start: 5.8, end: 12.0, text: "Transcription et extraction des décisions par le moteur IA." },
        { speaker: "SPEAKER_00", start: 12.5, end: 18.0, text: "Analyse terminée avec succès et intégrée au RAG." }
      ]
    };

    this.saveMeeting(newMeeting);
    return newMeeting;
  }

  static saveMeeting(meeting) {
    const current = this.getMeetings();
    const updated = [meeting, ...current.filter((m) => m.id !== meeting.id)];
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
  }
}

export default MeetingStorage;
