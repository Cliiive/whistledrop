import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import UploadPage from './pages/UploadPage';
import { AuthProvider } from './context/AuthContext';

// Protected Route Komponente, die prüft, ob der Benutzer eingeloggt ist
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  // Wir führen jetzt eine Prüfung auf window-Ebene durch, ob der Auth-Context einen Token hat
  // Falls nicht, leiten wir zur Landing Page um
  const isAuthenticated = window.__WHISTLEDROP_AUTH_TOKEN__ !== undefined;
  
  if (!isAuthenticated) {
    return <Navigate to="/" replace />;
  }
  
  return <>{children}</>;
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route 
            path="/upload" 
            element={
              <ProtectedRoute>
                <UploadPage />
              </ProtectedRoute>
            } 
          />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;

// Ergänze die globale Typendefinition
declare global {
  interface Window {
    __WHISTLEDROP_AUTH_TOKEN__?: string;
  }
}
