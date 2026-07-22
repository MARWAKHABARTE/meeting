import React from "react";
import { NavLink } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import {
  LayoutDashboard,
  Mic,
  Upload,
  FileText,
  Brain,
  MessageSquare,
  FileSpreadsheet,
  Settings,
  LogOut,
  Sparkles
} from "lucide-react";

const NAV_ITEMS = [
  { to: "/dashboard",     label: "Dashboard",       icon: LayoutDashboard },
  { to: "/meetings",      label: "Réunions",        icon: Mic },
  { to: "/upload",        label: "Upload",          icon: Upload },
  { to: "/transcription", label: "Transcriptions",  icon: FileText },
  { to: "/summary",       label: "Résumés",         icon: Brain },
  { to: "/chat",          label: "Chat IA",         icon: MessageSquare },
  { to: "/reports",       label: "Rapports",        icon: FileSpreadsheet },
  { to: "/settings",      label: "Paramètres",      icon: Settings },
];

const NavItem = ({ to, label, icon: Icon }) => (
  <NavLink
    to={to}
    className={({ isActive }) =>
      `sidebar-nav-item ${isActive ? "sidebar-nav-item--active" : ""}`
    }
    aria-label={label}
  >
    <Icon size={18} aria-hidden="true" />
    <span>{label}</span>
  </NavLink>
);

const Sidebar = () => {
  const { logout } = useAuth();

  return (
    <aside className="sidebar" aria-label="Navigation principale">
      {/* Brand Header */}
      <div className="sidebar-logo">
        <div className="sidebar-logo-icon" aria-hidden="true">
          <Sparkles size={20} />
        </div>
        <div className="sidebar-logo-text">
          <span className="sidebar-logo-name">Meeting AI</span>
          <span className="sidebar-logo-sub">Enterprise</span>
        </div>
      </div>

      {/* Navigation List */}
      <nav className="sidebar-nav">
        <div className="sidebar-nav-section">
          {NAV_ITEMS.map((item) => (
            <NavItem key={item.to} {...item} />
          ))}
        </div>
      </nav>

      {/* Footer / Logout */}
      <div className="sidebar-footer">
        <button className="sidebar-logout" onClick={logout} aria-label="Se déconnecter">
          <LogOut size={16} aria-hidden="true" />
          <span>Déconnexion</span>
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
