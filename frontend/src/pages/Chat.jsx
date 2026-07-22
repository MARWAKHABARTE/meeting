import React, { useState, useRef, useEffect, useCallback } from "react";
import { useParams, Link } from "react-router-dom";
import { useRAG } from "../hooks/useRAG";
import {
  MessageSquare, Send, ChevronLeft, Trash2,
  Brain, User, Loader, BookOpen, Lightbulb
} from "lucide-react";

/* ─── Suggestions de questions ─────────────────────────────────────────── */
const SUGGESTIONS = [
  "Quelles sont les décisions prises durant cette réunion ?",
  "Qui a participé à cette réunion ?",
  "Quels sont les points d'action identifiés ?",
  "Quel est le sentiment général de la réunion ?",
  "Résumé les points clés en 3 bullet points.",
];

/* ─── Bulle de message ─────────────────────────────────────────────────── */
const MessageBubble = ({ message }) => {
  const isUser      = message.role === "user";
  const isAssistant = message.role === "assistant";
  const isError     = message.role === "error";

  const timeStr = message.timestamp?.toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" });

  if (isError) {
    return (
      <div className="chat-message chat-message--error" role="alert">
        <div className="chat-bubble chat-bubble--error">⚠️ {message.content}</div>
      </div>
    );
  }

  return (
    <div className={`chat-message chat-message--${message.role}`}>
      {isAssistant && (
        <div className="chat-avatar chat-avatar--ai" aria-hidden="true">
          <Brain size={16} />
        </div>
      )}

      <div className={`chat-bubble chat-bubble--${message.role}`}>
        <p className="chat-bubble-text">{message.content}</p>

        {/* Sources RAG */}
        {isAssistant && message.sources?.length > 0 && (
          <div className="chat-sources">
            <div className="chat-sources-header">
              <BookOpen size={12} /> Sources ({message.sources.length})
            </div>
            {message.sources.map((src, i) => (
              <div key={i} className="chat-source-item">
                <span className="chat-source-num">{i + 1}</span>
                <span className="chat-source-text">{typeof src === "string" ? src : src.text || JSON.stringify(src)}</span>
              </div>
            ))}
          </div>
        )}

        <span className="chat-bubble-time">{timeStr}</span>
      </div>

      {isUser && (
        <div className="chat-avatar chat-avatar--user" aria-hidden="true">
          <User size={16} />
        </div>
      )}
    </div>
  );
};

/* ─── Page Chat ────────────────────────────────────────────────────────── */
const Chat = () => {
  const { meetingId } = useParams();
  const activeMeetingId = meetingId || "meeting-session-1";

  const { messages, loading, error, sendMessage, clearConversation } = useRAG(activeMeetingId);
  const [inputValue, setInputValue] = useState("");
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll en bas à chaque nouveau message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = useCallback(async () => {
    const q = inputValue.trim();
    if (!q || loading) return;
    setInputValue("");
    await sendMessage(q);
    inputRef.current?.focus();
  }, [inputValue, loading, sendMessage]);

  const handleKeyDown = useCallback((e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }, [handleSend]);

  const handleSuggestion = useCallback((q) => {
    setInputValue(q);
    inputRef.current?.focus();
  }, []);

  const isEmpty = messages.length === 0;

  return (
    <div className="page page--chat">
      {/* En-tête */}
      <div className="chat-header">
        <div className="chat-header-left">
          <Link to="/meetings" className="back-link" aria-label="Retour aux réunions">
            <ChevronLeft size={16} />
          </Link>
          <div className="chat-avatar chat-avatar--ai chat-avatar--lg" aria-hidden="true">
            <Brain size={22} />
          </div>
          <div>
            <h1 className="chat-title">Chat IA — Réunion</h1>
            <p className="chat-subtitle">
              <code className="code-inline">{activeMeetingId}</code>
              {" "}· Alimenté par Ollama + ChromaDB RAG
            </p>
          </div>
        </div>
        <button
          className="btn btn-ghost btn-sm"
          onClick={clearConversation}
          disabled={isEmpty}
          aria-label="Vider la conversation"
          title="Vider la conversation"
        >
          <Trash2 size={15} />
          Vider
        </button>
      </div>

      {/* Zone de messages */}
      <div className="chat-messages" role="log" aria-live="polite" aria-label="Conversation avec l'IA">
        {isEmpty ? (
          /* État vide — suggestions */
          <div className="chat-welcome">
            <div className="chat-welcome-icon"><Brain size={48} strokeWidth={1.5} /></div>
            <h2 className="chat-welcome-title">Comment puis-je vous aider ?</h2>
            <p className="chat-welcome-desc">
              Posez n'importe quelle question sur cette réunion. L'IA cherchera dans la transcription et le résumé.
            </p>
            <div className="chat-suggestions">
              <div className="chat-suggestions-label">
                <Lightbulb size={14} /> Suggestions
              </div>
              <div className="chat-suggestions-grid">
                {SUGGESTIONS.map((q, i) => (
                  <button
                    key={i}
                    className="chat-suggestion-chip"
                    onClick={() => handleSuggestion(q)}
                    aria-label={`Suggestion : ${q}`}
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <>
            {messages.map((msg, i) => (
              <MessageBubble key={i} message={msg} />
            ))}
            {/* Indicateur de frappe IA */}
            {loading && (
              <div className="chat-message chat-message--assistant">
                <div className="chat-avatar chat-avatar--ai"><Brain size={16} /></div>
                <div className="chat-bubble chat-bubble--assistant chat-bubble--typing">
                  <span className="typing-dot" />
                  <span className="typing-dot" />
                  <span className="typing-dot" />
                </div>
              </div>
            )}
          </>
        )}
        <div ref={messagesEndRef} aria-hidden="true" />
      </div>

      {/* Zone de saisie */}
      <div className="chat-input-area">
        <div className="chat-input-wrapper">
          <textarea
            ref={inputRef}
            className="chat-input"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Posez votre question sur la réunion... (Entrée pour envoyer)"
            rows={1}
            disabled={loading}
            aria-label="Message à envoyer à l'IA"
          />
          <button
            className="chat-send-btn"
            onClick={handleSend}
            disabled={!inputValue.trim() || loading}
            aria-label="Envoyer le message"
          >
            {loading
              ? <Loader size={18} className="spin" />
              : <Send size={18} />
            }
          </button>
        </div>
        <p className="chat-hint">Shift + Entrée pour une nouvelle ligne · Entrée pour envoyer</p>
      </div>
    </div>
  );
};

export default Chat;
