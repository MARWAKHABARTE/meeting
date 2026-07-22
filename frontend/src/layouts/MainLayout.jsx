import React from "react";
import { Outlet } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";
import NotificationCenter from "../components/NotificationCenter";

/**
 * Layout principal pour les pages sécurisées.
 * Dispose le Sidebar à gauche, le Navbar en haut et la zone de contenu scrollable.
 */
const MainLayout = () => {
  return (
    <div className="app-layout">
      <NotificationCenter />
      <Sidebar />
      <div className="main-container">
        <Navbar />
        <main className="content-area">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default MainLayout;
