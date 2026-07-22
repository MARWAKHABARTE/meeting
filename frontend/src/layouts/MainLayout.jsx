import React from "react";
import { Outlet } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";
import NotificationCenter from "../components/NotificationCenter";

/**
 * Layout principal pour les pages sécurisées.
 * Dispose le Sidebar à gauche (colonne 1: 260px) et le main-container à droite (colonne 2: 1fr).
 */
const MainLayout = () => {
  return (
    <>
      <NotificationCenter />
      <div className="app-layout">
        <Sidebar />
        <div className="main-container">
          <Navbar />
          <main className="content-area">
            <Outlet />
          </main>
        </div>
      </div>
    </>
  );
};

export default MainLayout;
