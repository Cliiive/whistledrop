import React, { useState, useEffect, useRef } from 'react';
import Button from '../components/Button';
import InputField from '../components/InputField';

const UploadPage: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [files, setFiles] = useState<any[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    // Beim Laden der Komponente die bereits hochgeladenen Dateien abrufen
    fetchUploadedFiles();
  }, []);

  const fetchUploadedFiles = async () => {
    try {
      const token = localStorage.getItem('accessToken');
      const response = await fetch('http://127.0.0.1:8000/api/v1/upload/', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Fehler beim Abrufen der Dateien');
      }
      
      const data = await response.json();
      setFiles(data);
    } catch (err) {
      console.error('Fehler beim Laden der Dateien:', err);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
      // Zurücksetzen der Status
      setUploadSuccess(false);
      setUploadError(null);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadError('Bitte wählen Sie eine Datei aus');
      return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);
    
    setUploading(true);
    setUploadError(null);
    
    try {
      const token = localStorage.getItem('accessToken');
      // Vollständige URL für den Upload-Endpunkt
      const response = await fetch('http://127.0.0.1:8000/api/v1/upload/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.detail || 'Upload fehlgeschlagen');
      }
      
      const data = await response.json();
      setUploadSuccess(true);
      setSelectedFile(null);
      
      // Zurücksetzen des Datei-Input-Felds
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      
      // Aktualisieren der Dateien-Liste
      fetchUploadedFiles();
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : 'Ein Fehler ist aufgetreten');
    } finally {
      setUploading(false);
    }
  };

  // Neue Funktion, um die Dateiauswahl auszulösen
  const handleFileButtonClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  // Funktion für das Formatieren der Dateigröße
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const containerStyles: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'column',
    maxWidth: '800px',
    margin: '0 auto',
    padding: '2rem',
  };

  const cardStyles: React.CSSProperties = {
    backgroundColor: 'white',
    borderRadius: '0.75rem',
    padding: '1.5rem',
    boxShadow: '0 4px 12px rgba(156, 124, 241, 0.08)',
    border: '1px solid var(--color-border)',
    marginBottom: '2rem',
  };

  const headerStyles: React.CSSProperties = {
    fontSize: '1.75rem',
    fontWeight: 700,
    color: '#4A3B76',
    marginBottom: '1.5rem',
    textAlign: 'center',
  };

  const fileInputStyles: React.CSSProperties = {
    marginBottom: '1.5rem',
  };

  const fileListStyles: React.CSSProperties = {
    marginTop: '2rem',
  };

  const fileItemStyles: React.CSSProperties = {
    padding: '0.75rem',
    borderRadius: '0.5rem',
    backgroundColor: 'var(--color-background-light)',
    marginBottom: '0.5rem',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
  };

  // Neue Styles für die verbesserte Dateiauswahl
  const dropzoneStyles: React.CSSProperties = {
    border: '2px dashed var(--color-border)',
    borderRadius: '0.75rem',
    backgroundColor: 'var(--color-background-light)',
    padding: '2rem',
    textAlign: 'center',
    cursor: 'pointer',
    marginBottom: '1.5rem',
    transition: 'all 0.2s ease',
  };

  const fileInfoStyles: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    padding: '0.75rem 1rem',
    backgroundColor: 'var(--color-outlined)',
    borderRadius: '0.5rem',
    marginBottom: '1.5rem',
  };

  const fileIconStyles: React.CSSProperties = {
    marginRight: '1rem',
    color: 'var(--color-primary)',
  };

  const fileDetailsStyles: React.CSSProperties = {
    flex: 1,
  };

  const fileNameStyles: React.CSSProperties = {
    fontWeight: 600,
    color: 'var(--color-text)',
    marginBottom: '0.25rem',
  };

  const fileSizeStyles: React.CSSProperties = {
    fontSize: '0.875rem',
    color: 'var(--color-text-light)',
  };

  return (
    <div style={containerStyles}>
      <h1 style={headerStyles}>Dateien hochladen</h1>
      
      <div style={cardStyles}>
        <input
          ref={fileInputRef}
          type="file"
          onChange={handleFileChange}
          disabled={uploading}
          style={{ display: 'none' }}
          id="file-input"
        />
        
        {!selectedFile ? (
          <div 
            style={dropzoneStyles}
            onClick={handleFileButtonClick}
            onDragOver={(e) => {
              e.preventDefault();
              e.stopPropagation();
            }}
            onDrop={(e) => {
              e.preventDefault();
              e.stopPropagation();
              
              if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
                setSelectedFile(e.dataTransfer.files[0]);
                setUploadSuccess(false);
                setUploadError(null);
              }
            }}
          >
            <svg 
              xmlns="http://www.w3.org/2000/svg" 
              width="48" 
              height="48" 
              viewBox="0 0 24 24" 
              fill="none" 
              stroke="currentColor" 
              strokeWidth="1.5"
              strokeLinecap="round" 
              strokeLinejoin="round" 
              style={{ color: 'var(--color-primary)', margin: '0 auto 1rem' }}
            >
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14 2 14 8 20 8"></polyline>
              <line x1="12" y1="18" x2="12" y2="12"></line>
              <line x1="9" y1="15" x2="15" y2="15"></line>
            </svg>
            
            <p style={{ color: 'var(--color-text)', fontSize: '1.1rem', fontWeight: 600, marginBottom: '0.5rem' }}>
              Datei hier ablegen oder klicken, um auszuwählen
            </p>
            <p style={{ color: 'var(--color-text-light)', fontSize: '0.875rem' }}>
              Ausschließlich PDF dateien sind erlaubt
            </p>
          </div>
        ) : (
          <div style={fileInfoStyles}>
            <svg 
              xmlns="http://www.w3.org/2000/svg" 
              width="24" 
              height="24" 
              viewBox="0 0 24 24" 
              fill="none" 
              stroke="currentColor" 
              strokeWidth="2"
              strokeLinecap="round" 
              strokeLinejoin="round" 
              style={fileIconStyles}
            >
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14 2 14 8 20 8"></polyline>
            </svg>
            
            <div style={fileDetailsStyles}>
              <div style={fileNameStyles}>{selectedFile.name}</div>
              <div style={fileSizeStyles}>{formatFileSize(selectedFile.size)}</div>
            </div>
            
            <Button 
              variant="outlined" 
              size="small" 
              onClick={() => {
                setSelectedFile(null);
                if (fileInputRef.current) fileInputRef.current.value = '';
              }}
            >
              Ändern
            </Button>
          </div>
        )}
        
        <Button
          variant="primary"
          fullWidth
          onClick={handleUpload}
          loading={uploading}
          disabled={!selectedFile || uploading}
        >
          {uploading ? 'Wird hochgeladen...' : 'Datei hochladen'}
        </Button>
        
        {uploadSuccess && (
          <p style={{ color: 'var(--color-success)', marginTop: '1rem', textAlign: 'center' }}>
            Datei erfolgreich hochgeladen!
          </p>
        )}
        
        {uploadError && (
          <p style={{ color: 'var(--color-danger)', marginTop: '1rem', textAlign: 'center' }}>
            Fehler: {uploadError}
          </p>
        )}
      </div>
      
      <div style={fileListStyles}>
        <h2 style={{ ...headerStyles, fontSize: '1.5rem' }}>Ihre hochgeladenen Dateien</h2>
        
        {files.length > 0 ? (
          files.map((file, index) => (
            <div key={index} style={fileItemStyles}>
              <div style={{ display: 'flex', alignItems: 'center' }}>
                <svg 
                  xmlns="http://www.w3.org/2000/svg" 
                  width="20" 
                  height="20" 
                  viewBox="0 0 24 24" 
                  fill="none" 
                  stroke="currentColor" 
                  strokeWidth="2"
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  style={{ marginRight: '0.75rem', color: 'var(--color-primary)' }}
                >
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                  <polyline points="14 2 14 8 20 8"></polyline>
                </svg>
                <span>{file.file_name}</span>
              </div>
              <span>{new Date(file.created_at).toLocaleDateString()}</span>
            </div>
          ))
        ) : (
          <p style={{ textAlign: 'center', color: 'var(--color-text-light)' }}>
            Keine Dateien gefunden
          </p>
        )}
      </div>
    </div>
  );
};

export default UploadPage;
