import React, { useState, useEffect, useRef } from 'react';
import Button from '../components/Button';

const UploadPage: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [files, setFiles] = useState<any[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);
  // Neue Zustände für den Löschdialog
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [fileToDelete, setFileToDelete] = useState<any | null>(null);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    // Beim Laden der Komponente die bereits hochgeladenen Dateien abrufen
    fetchUploadedFiles();

    // Polling-Mechanismus einrichten, der alle 5 Sekunden nach Updates sucht
    const pollingInterval = setInterval(() => {
      fetchUploadedFiles();
    }, 5000); // 5000ms = 5 Sekunden

    // Aufräumen beim Unmounten der Komponente
    return () => {
      clearInterval(pollingInterval);
    };
  }, []);

  const fetchUploadedFiles = async () => {
    try {
      const token = window.__WHISTLEDROP_AUTH_TOKEN__;
      const response = await fetch('/api/v1/upload/', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Error fetching files');
      }
      
      const data = await response.json();
      setFiles(data);
    } catch (err) {
      console.error('Error:', err);
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
      setUploadError('Please select a file to upload');
      return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);
    
    setUploading(true);
    setUploadError(null);
    
    try {
      const token = window.__WHISTLEDROP_AUTH_TOKEN__;
      // Vollständige URL für den Upload-Endpunkt
      const response = await fetch('/api/v1/upload/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.detail || 'Upload failed');
      }
      
      // const data = await response.json();
      setUploadSuccess(true);
      setSelectedFile(null);
      
      // Zurücksetzen des Datei-Input-Felds
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      
      // Aktualisieren der Dateien-Liste
      fetchUploadedFiles();
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : 'An error occurred');
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

  // Funktion zum Öffnen des Löschdialogs
  const handleDeleteClick = (file: any) => {
    setFileToDelete(file);
    setShowDeleteDialog(true);
  };

  // Funktion zum Schließen des Löschdialogs
  const handleCancelDelete = () => {
    setShowDeleteDialog(false);
    setFileToDelete(null);
  };

  // Funktion zum Löschen der Datei
  const handleConfirmDelete = async () => {
    if (!fileToDelete) return;
    
    setDeleting(true);
    try {
      const token = window.__WHISTLEDROP_AUTH_TOKEN__;
      const response = await fetch(`/api/v1/upload/${fileToDelete.id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Error deleting file');
      }
      
      // Datei aus der lokalen Liste entfernen
      setFiles(files.filter(file => file.id !== fileToDelete.id));
      
    } catch (err) {
      console.error('Error:', err);
      // Optional: Fehlermeldung anzeigen
    } finally {
      setDeleting(false);
      setShowDeleteDialog(false);
      setFileToDelete(null);
    }
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

  // const fileInputStyles: React.CSSProperties = {
  //   marginBottom: '1.5rem',
  // };

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

  // Styles für den Dialog
  const dialogOverlayStyles: React.CSSProperties = {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    display: showDeleteDialog ? 'flex' : 'none',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 1000
  };

  const dialogStyles: React.CSSProperties = {
    backgroundColor: 'white',
    borderRadius: '0.75rem',
    padding: '1.5rem',
    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.15)',
    width: '90%',
    maxWidth: '500px'
  };

  const dialogButtonsStyles: React.CSSProperties = {
    display: 'flex',
    justifyContent: 'flex-end',
    gap: '0.75rem',
    marginTop: '1.5rem'
  };

  // const trashIconStyles: React.CSSProperties = {
  //   color: 'var(--color-danger)',
  //   cursor: 'pointer',
  //   padding: '0.25rem',
  //   borderRadius: '50%',
  //   transition: 'all 0.2s ease',
  //   marginLeft: '0.5rem',
  // };

  return (
    <div style={containerStyles}>
      <h1 style={headerStyles}>Upload files</h1>
      
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
              Place your file here or click to upload
            </p>
            <p style={{ color: 'var(--color-text-light)', fontSize: '0.875rem' }}>
              Only pdf files are allowed
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
              Change
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
          {uploading ? 'Your file is beeing uploaded...' : 'Upload file'}
        </Button>
        
        {uploadSuccess && (
          <p style={{ color: 'var(--color-success)', marginTop: '1rem', textAlign: 'center' }}>
            Uploaded file successfully!
          </p>
        )}
        
        {uploadError && (
          <p style={{ color: 'var(--color-danger)', marginTop: '1rem', textAlign: 'center' }}>
            Error: {uploadError}
          </p>
        )}
      </div>
      
      <div style={fileListStyles}>
        <h2 style={{ ...headerStyles, fontSize: '1.5rem' }}>Your uploaded files</h2>
        
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
              <div style={{ display: 'flex', alignItems: 'center' }}>

                {/* Eye icon for seen files */}
                {file.seen && (
                  <div
                    style={{
                      marginLeft: '0.75rem',
                      marginRight: '0.75rem',
                      display: 'flex',
                      alignItems: 'center',
                      color: 'var(--color-success)',
                    }}
                    title="Your file has been downloaded by the journalist"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="18"
                      height="18"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                      <circle cx="12" cy="12" r="3"></circle>
                    </svg>
                  </div>
                )}
                <span>{new Date(file.created_at).toLocaleString('us-US', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })}</span>

                {/* Lösch-Button */}
                <button
                  onClick={() => handleDeleteClick(file)}
                  style={{
                    background: 'none',
                    border: 'none',
                    cursor: 'pointer',
                    marginLeft: '1rem',
                    padding: '0.25rem',
                    borderRadius: '50%',
                    transition: 'all 0.2s ease',
                  }}
                  onMouseOver={(e) => {
                    e.currentTarget.style.backgroundColor = 'rgba(255, 0, 0, 0.1)';
                  }}
                  onMouseOut={(e) => {
                    e.currentTarget.style.backgroundColor = 'transparent';
                  }}
                  title="Delete file"
                >
                  <svg 
                    xmlns="http://www.w3.org/2000/svg" 
                    width="18" 
                    height="18" 
                    viewBox="0 0 24 24" 
                    fill="none" 
                    stroke="currentColor" 
                    strokeWidth="2"
                    strokeLinecap="round" 
                    strokeLinejoin="round" 
                    style={{ color: '#ff5757' }}
                  >
                    <polyline points="3 6 5 6 21 6"></polyline>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                    <line x1="10" y1="11" x2="10" y2="17"></line>
                    <line x1="14" y1="11" x2="14" y2="17"></line>
                  </svg>
                </button>
              </div>
            </div>
          ))
        ) : (
          <p style={{ textAlign: 'center', color: 'var(--color-text-light)' }}>
            Did not find any uploaded files.
          </p>
        )}
      </div>

      {/* Lösch-Bestätigungsdialog */}
      <div style={dialogOverlayStyles}>
        <div style={dialogStyles}>
          <h3 style={{ color: '#4A3B76', marginTop: 0 }}>Delete file</h3>
          <p>
            Do you really want to delete the file <strong>{fileToDelete?.file_name}</strong>? This action cannot be undone.
          </p>
          <div style={dialogButtonsStyles}>
            <Button 
              variant="outlined" 
              onClick={handleCancelDelete} 
              disabled={deleting}
            >
              Abbrechen
            </Button>
            <Button 
              variant="danger" 
              onClick={handleConfirmDelete} 
              loading={deleting}
              disabled={deleting}
            >
              {deleting ? 'Wird gelöscht...' : 'Löschen'}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UploadPage;

