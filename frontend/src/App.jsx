import React, { lazy, Suspense } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import { WebSocketProvider } from "./context/WebSocketContext";
import ProtectedRoute from "./components/ProtectedRoute";
import MainLayout from "./layouts/MainLayout";
import ErrorBoundary from "./components/ErrorBoundary";
import Loader from "./components/Loader";

// Routes publiques (pas de lazy — critique)
import Login from "./pages/Login";
import NotFound from "./pages/NotFound";

// Routes privées — Lazy Loading pour Code Splitting
const Dashboard    = lazy(() => import("./pages/Dashboard"));
const Meetings     = lazy(() => import("./pages/Meetings"));
const Upload       = lazy(() => import("./pages/Upload"));
const Transcript   = lazy(() => import("./pages/Transcript"));
const Summary      = lazy(() => import("./pages/Summary"));
const Chat         = lazy(() => import("./pages/Chat"));
const Reports      = lazy(() => import("./pages/Reports"));
const Settings     = lazy(() => import("./pages/Settings"));

const SuspenseFallback = () => (
  <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "60vh" }}>
    <Loader />
  </div>
);

function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <WebSocketProvider>
          <Router>
            <Suspense fallback={<SuspenseFallback />}>
              <Routes>
                {/* ─── Public ────────────────────────────────────────── */}
                <Route path="/login" element={<Login />} />

                {/* ─── Protected — MainLayout ─────────────────────────── */}
                <Route
                  path="/"
                  element={
                    <ProtectedRoute>
                      <MainLayout />
                    </ProtectedRoute>
                  }
                >
                  <Route index element={<Navigate to="/dashboard" replace />} />
                  <Route path="dashboard"               element={<Dashboard />} />
                  <Route path="meetings"                element={<Meetings />} />
                  <Route path="meetings/:id"            element={<Meetings />} />
                  <Route path="upload"                  element={<Upload />} />
                  <Route path="transcription/:id"       element={<Transcript />} />
                  <Route path="transcription"           element={<Transcript />} />
                  <Route path="summary/:id"             element={<Summary />} />
                  <Route path="summary"                 element={<Summary />} />
                  <Route path="chat/:meetingId"         element={<Chat />} />
                  <Route path="chat"                    element={<Chat />} />
                  <Route path="reports"                 element={<Reports />} />
                  <Route path="settings"                element={<Settings />} />
                </Route>

                {/* ─── 404 ─────────────────────────────────────────── */}
                <Route path="*" element={<NotFound />} />
              </Routes>
            </Suspense>
          </Router>
        </WebSocketProvider>
      </AuthProvider>
    </ErrorBoundary>
  );
}

export default App;
