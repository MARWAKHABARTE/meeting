import React, { useCallback } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import {
  LayoutDashboard, Mic, Upload, FileText, Brain,
  MessageSquare, BarChart2, Settings, LogOut, Zap
} from "lucide-react";

const NAV_ITEMS = [
  { to: "/dashboard",   label: "Dashboard",        icon: LayoutDashboard },
  { to: "/meetings",    label: "Réunions",          icon: Mic },
  { to: "/upload",      label: "Upload",            icon: Upload },
];

const NAV_AI = [
  { to: "/transcription", label: "Transcriptions", icon: FileText },
  { to: "/summary",       label: "Résumés NLP",    icon: Brain },
  { to: "/chat",          label: "Chat IA (RAG)",  icon: MessageSquare },
];

const NAV_OTHER = [
  { to: "/reports",   label: "Rapports",    icon: BarChart2 },
  { to: "/settings",  label: "Paramètres",  icon: Settings },
];

const NavItem = ({ to, label, icon: Icon }) => (
  <NavLink
    to={to}
    className={({ isActive }) => `sidebar-nav-item ${isActive ? "sidebar-nav-item--active" : ""}`}
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
      {/* Logo */}
      <div className="sidebar-logo">
        <div className="sidebar-logo-icon" aria-hidden="true">
          <Zap size={22} />
        </div>
        <div>
          <span className="sidebar-logo-name">Meeting AI</span>
          <span className="sidebar-logo-sub">Platform</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        {/* Section principale */}
        <div className="sidebar-nav-section">
          <span className="sidebar-nav-label">Général</span>
          {NAV_ITEMS.map((item) => <NavItem key={item.to} {...item} />)}
        </div>

        {/* Section IA */}
        <div className="sidebar-nav-section">
          <span className="sidebar-nav-label">Pipeline IA</span>
          {NAV_AI.map((item) => <NavItem key={item.to} {...item} />)}
        </div>

        {/* Section autre */}
        <div className="sidebar-nav-section">
          <span className="sidebar-nav-label">Application</span>
          {NAV_OTHER.map((item) => <NavItem key={item.to} {...item} />)}
        </div>
      </nav>

      {/* Bouton déconnexion */}
      <button className="sidebar-logout" onClick={logout} aria-label="Se déconnecter">
        <LogOut size={16} aria-hidden="true" />
        <span>Déconnexion</span>
      </button>
    </aside>
  );
};

export default Sidebar;
