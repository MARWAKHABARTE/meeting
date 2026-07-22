import React from "react";
import { FileX, FolderOpen, MessageSquare, Search } from "lucide-react";

const ICONS = {
  meetings: FolderOpen,
  search: Search,
  chat: MessageSquare,
  default: FileX,
};

/**
 * Composant EmptyState — affiche un message engageant quand une liste est vide.
 */
export const EmptyState = ({
  type = "default",
  title = "Aucun élément",
  description = "Il n'y a rien ici pour l'instant.",
  action = null,
}) => {
  const Icon = ICONS[type] || ICONS.default;

  return (
    <div className="empty-state" role="status">
      <div className="empty-state-icon">
        <Icon size={48} strokeWidth={1.5} />
      </div>
      <h3 className="empty-state-title">{title}</h3>
      <p className="empty-state-description">{description}</p>
      {action && <div className="empty-state-action">{action}</div>}
    </div>
  );
};

export default EmptyState;
