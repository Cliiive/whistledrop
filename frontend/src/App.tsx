import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
// Import ohne Dateiendung (das war der Fehler)
import UploadPage from './pages/UploadPage';
import './App.css';

// Korrigierte ProtectedRoute-Komponente
const ProtectedRoute = ({ element }: { element: React.ReactElement }) => {
  const isAuthenticated = localStorage.getItem('accessToken') !== null;
  return isAuthenticated ? element : <Navigate to="/" replace />;
};

const App: React.FC = () => {
  return (
    <Router>
      <div className="app">
        <main className="app-content">
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route 
              path="/upload" 
              element={<ProtectedRoute element={<UploadPage />} />} 
            />
            {/* Fallback für alle nicht definierten Routen */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
        <footer className="app-footer">
          <p>&copy; {new Date().getFullYear()} WhistleDrop - Sicherer Datenaustausch für Whistleblower</p>
        </footer>
      </div>
    </Router>
  );
};

export default App;
