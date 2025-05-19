import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Button from '../components/Button';
import InputField from '../components/InputField';
import { useAuth } from '../context/AuthContext';

const LandingPage: React.FC = () => {
  const [passphrase, setPassphrase] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showGeneratedPassphrase, setShowGeneratedPassphrase] = useState(false);
  const [generatedPassphrase, setGeneratedPassphrase] = useState('');
  const navigate = useNavigate();
  const { setAccessToken } = useAuth();

  const handlePassphraseChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setPassphrase(e.target.value);
    if (error) setError(null);
  };

  const handleLogin = async () => {
    if (!passphrase.trim()) {
      setError('Bitte geben Sie eine Passphrase ein');
      return;
    }
    
    setIsLoading(true);
    try {
      const response = await fetch('http://127.0.0.1:8000/api/v1/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ passphrase }),
      });
      
      if (!response.ok) {
        throw new Error('Ungültige Passphrase');
      }
      
      const data = await response.json();
      
      // Token im RAM speichern statt localStorage
      setAccessToken(data.access_token);
      window.__WHISTLEDROP_AUTH_TOKEN__ = data.access_token;
      
      // Weiterleitung zur Upload-Seite
      navigate('/upload');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGeneratePassphrase = async () => {
    setIsLoading(true);
    try {
      // API-Aufruf zum Generieren einer neuen Passphrase
      const response = await fetch('http://127.0.0.1:8000/api/v1/auth/register', {
        method: 'GET',
      });
      
      if (!response.ok) {
        throw new Error('Error generating passphrase');
      }
      
      const data = await response.json();
      setGeneratedPassphrase(data.passphrase);
      setShowGeneratedPassphrase(true);
      
      // Token im RAM speichern statt localStorage
      setAccessToken(data.access_token);
      window.__WHISTLEDROP_AUTH_TOKEN__ = data.access_token;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const handleContinueToUpload = () => {
    navigate('/upload');
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(generatedPassphrase)
      .then(() => {
        alert('Passphrase copied to clipboard!');
      })
      .catch((error) => {
        console.error('Error copying: ', error);
      });
  };

  const containerStyles: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: '100vh',
    padding: '2rem',
    maxWidth: '600px',
    margin: '0 auto',
    gap: '1.5rem',
  };

  const headerStyles: React.CSSProperties = {
    fontSize: '2rem',
    fontWeight: 700,
    color: '#4A3B76',
    marginBottom: '1rem',
    textAlign: 'center',
  };

  const subHeaderStyles: React.CSSProperties = {
    fontSize: '1.1rem',
    color: '#8878B5',
    marginBottom: '2rem',
    textAlign: 'center',
  };

  const separatorStyles: React.CSSProperties = {
    width: '100%',
    textAlign: 'center',
    margin: '1.5rem 0',
    fontSize: '0.9rem',
    color: '#A99ECC',
    position: 'relative',
  };

  const noPassphraseTextStyles: React.CSSProperties = {
    fontSize: '0.95rem',
    color: '#6C54CA',
    marginTop: '1.5rem',
    marginBottom: '0.5rem',
    textAlign: 'center',
  };

  const passphraseDisplayStyles: React.CSSProperties = {
    padding: '1rem',
    backgroundColor: '#EBE5FF',
    borderRadius: '0.5rem',
    border: '2px dashed #9C7CF1',
    fontFamily: 'monospace',
    fontSize: '1.2rem',
    fontWeight: 600,
    textAlign: 'center',
    color: '#4A3B76',
    marginBottom: '1rem',
    wordBreak: 'break-all',
    position: 'relative',
  };

  const warningBoxStyles: React.CSSProperties = {
    padding: '1rem',
    backgroundColor: 'rgba(247, 110, 143, 0.1)',
    border: '1px solid #F76E8F',
    borderRadius: '0.5rem',
    marginTop: '1rem',
    marginBottom: '1rem',
  };

  const warningTextStyles: React.CSSProperties = {
    color: '#E05A7A',
    fontWeight: 600,
    fontSize: '0.95rem',
    marginBottom: '0.5rem',
  };

  const cautionTextStyles: React.CSSProperties = {
    color: '#E05A7A',
    fontSize: '0.85rem',
  };

  const buttonGroupStyles: React.CSSProperties = {
    display: 'flex',
    gap: '1rem',
    width: '100%',
    marginTop: '1rem',
  };

  return (
    <div style={containerStyles}>
      <div>
        <h1 style={headerStyles}>WhistleDrop</h1>
        <p style={subHeaderStyles}>Secure file exchange for whistleblower</p>
      </div>
      
      {!showGeneratedPassphrase ? (
        <>
          <InputField
            label="Passphrase"
            placeholder="Please enter your passphrase"
            type="password"
            value={passphrase}
            onChange={handlePassphraseChange}
            error={error || undefined}
            fullWidth
            onSubmit={handleLogin}
            helperText="Enter your passphrase to access your files."
            endIcon={
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
              </svg>
            }
          />
          
          <Button 
            variant="primary" 
            size="medium" 
            fullWidth 
            onClick={handleLogin}
            loading={isLoading}
          >
            Login
          </Button>

          <div style={separatorStyles}>
            <hr style={{ border: 'none', borderTop: '1px solid #DCD3FA', margin: '10px 0' }} />
          </div>
          
          <p style={noPassphraseTextStyles}>Don't have a passphrase yet?</p>
          
          <Button 
            variant="secondary" 
            size="medium" 
            fullWidth 
            onClick={handleGeneratePassphrase}
            loading={isLoading}
          >
            Generate new passphrase
          </Button>
        </>
      ) : (
        <>
          <div style={warningBoxStyles}>
            <p style={warningTextStyles}>⚠️ IMPORTANT</p>
            <p style={cautionTextStyles}>
              This passphrase will only be shown once. Please save it securely.
              If you lose it, you will not be able to access your files.

            </p>
          </div>
          
          <div style={passphraseDisplayStyles}>
            {generatedPassphrase}
          </div>
          
          <div style={buttonGroupStyles}>
            <Button 
              variant="secondary" 
              size="medium" 
              onClick={copyToClipboard}
              icon={
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                  <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"></path>
                </svg>
              }
            >
              Copy Passphrase
            </Button>
            
            <Button 
              variant="primary" 
              size="medium"
              onClick={handleContinueToUpload}
            >
              Go to Upload
            </Button>
          </div>
        </>
      )}
    </div>
  );
};

export default LandingPage;
