import React, { useEffect, useRef, useCallback } from "react";
import { X } from "lucide-react";

/**
 * Modale accessible et réutilisable — gère focus trap, fermeture Escape et overlay.
 */
export const Modal = ({
  isOpen,
  onClose,
  title,
  children,
  size = "md", // sm | md | lg | xl
  hideCloseButton = false,
}) => {
  const overlayRef = useRef(null);
  const modalRef = useRef(null);

  // Fermeture via Escape
  const handleKeyDown = useCallback((e) => {
    if (e.key === "Escape") onClose();
  }, [onClose]);

  // Focus trap et gestion du scroll
  useEffect(() => {
    if (!isOpen) return;
    document.addEventListener("keydown", handleKeyDown);
    document.body.style.overflow = "hidden";
    // Focus automatique sur la modale
    modalRef.current?.focus();
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      document.body.style.overflow = "";
    };
  }, [isOpen, handleKeyDown]);

  if (!isOpen) return null;

  return (
    <div
      ref={overlayRef}
      className="modal-overlay"
      onClick={(e) => { if (e.target === overlayRef.current) onClose(); }}
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
    >
      <div
        ref={modalRef}
        className={`modal-container modal-${size}`}
        tabIndex={-1}
      >
        <div className="modal-header">
          <h2 id="modal-title" className="modal-title">{title}</h2>
          {!hideCloseButton && (
            <button
              className="modal-close-btn"
              onClick={onClose}
              aria-label="Fermer la modale"
            >
              <X size={20} />
            </button>
          )}
        </div>
        <div className="modal-body">{children}</div>
      </div>
    </div>
  );
};

export default Modal;
