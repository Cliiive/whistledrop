import React, { useState, useEffect } from 'react';

export interface InputFieldProps {
  id?: string;
  label?: string;
  placeholder?: string;
  type?: string;
  value?: string;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onBlur?: (e: React.FocusEvent<HTMLInputElement>) => void;
  error?: string;
  success?: string;
  disabled?: boolean;
  required?: boolean;
  className?: string;
  fullWidth?: boolean;
  endIcon?: React.ReactNode;
  helperText?: string;
  name?: string;
  // API props
  onSubmit?: (value: string) => Promise<any>;
  autoSubmit?: boolean;
  submitDelay?: number;
}

const InputField: React.FC<InputFieldProps> = ({
  id,
  label,
  placeholder,
  type = 'text',
  value: propValue,
  onChange,
  onBlur,
  error,
  success,
  disabled = false,
  required = false,
  className = '',
  fullWidth = false,
  endIcon,
  helperText,
  name,
  onSubmit,
  autoSubmit = false,
  submitDelay = 500,
}) => {
  const [value, setValue] = useState(propValue || '');
  const [isLoading, setIsLoading] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);
  const [apiSuccess, setApiSuccess] = useState<string | null>(null);
  const [submitTimeout, setSubmitTimeout] = useState<ReturnType<typeof setTimeout> | null>(null);
  const [isFocused, setIsFocused] = useState(false);
  const [inputId] = useState(`input-${Math.random().toString(36).substring(2, 11)}`);

  // Moderne Pastell-Lila Farbpalette
  const colors = {
    primary: '#9C7CF1',       // Pastell-Lila (Hauptfarbe)
    secondary: '#B8A1F8',     // Helleres Pastell-Lila
    border: '#DCD3FA',        // Heller Lila-Rand
    focusBorder: '#9C7CF1',   // Lila bei Fokus
    error: '#F76E8F',         // Weiches Rosa-Rot
    success: '#58D6A8',       // Weiches Mintgrün
    labelText: '#6C54CA',     // Dunkles Lila für Labels
    inputText: '#4A3B76',     // Dunkles Lila für Eingabetext
    placeholder: '#A99ECC',   // Mittleres Lila für Placeholder
    disabled: '#F5F3FF',      // Sehr helles Lila für disabled
    disabledText: '#A99ECC',  // Mittleres Lila für disabled Text
    helperText: '#8878B5',    // Mittleres Lila für Hilfstexte
  };

  // Erstelle dynamische Styles für den Placeholder
  useEffect(() => {
    // Erstelle ein style-Element für den Placeholder
    const styleEl = document.createElement('style');
    styleEl.innerHTML = `
      #${inputId}::placeholder {
        color: ${colors.placeholder};
      }
    `;
    document.head.appendChild(styleEl);
    
    // Clean-up beim Unmount
    return () => {
      document.head.removeChild(styleEl);
    };
  }, [inputId, colors.placeholder]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setValue(newValue);
    
    if (onChange) {
      onChange(e);
    }

    if (autoSubmit && onSubmit) {
      if (submitTimeout) {
        clearTimeout(submitTimeout);
      }
      
      const timeout = setTimeout(() => {
        handleSubmit(newValue);
      }, submitDelay);
      
      setSubmitTimeout(timeout);
    }
    
    // Clear previous API messages when input changes
    setApiError(null);
    setApiSuccess(null);
  };

  const handleSubmit = async (submitValue: string) => {
    if (!onSubmit || disabled || isLoading) return;
    
    try {
      setIsLoading(true);
      setApiError(null);
      const response = await onSubmit(submitValue);
      
      setApiSuccess('Erfolgreich!');
      return response;
    } catch (err) {
      setApiError(err instanceof Error ? err.message : 'Ein Fehler ist aufgetreten');
      return null;
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && onSubmit) {
      handleSubmit(value);
    }
  };

  const containerStyles: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'column',
    width: fullWidth ? '100%' : 'auto',
    marginBottom: '1.25rem',
    position: 'relative',
  };

  const inputContainerStyles: React.CSSProperties = {
    position: 'relative',
    display: 'flex',
    alignItems: 'center',
    width: '100%',
  };

  const getBorderColor = () => {
    if (error || apiError) return colors.error;
    if (success || apiSuccess) return colors.success;
    if (isFocused) return colors.focusBorder;
    return colors.border;
  };

  const inputStyles: React.CSSProperties = {
    padding: '0.875rem 1rem',
    fontSize: '1rem',
    lineHeight: '1.5',
    borderRadius: '0.75rem',
    border: `1.5px solid ${getBorderColor()}`,
    width: '100%',
    transition: 'all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1)',
    backgroundColor: disabled ? colors.disabled : 'white',
    color: disabled ? colors.disabledText : colors.inputText,
    outline: 'none',
    boxShadow: isFocused ? `0 0 0 2px rgba(156, 124, 241, 0.1)` : 'none',
  };

  const labelStyles: React.CSSProperties = {
    fontSize: '0.875rem',
    fontWeight: 600,
    marginBottom: '0.5rem',
    color: colors.labelText,
    letterSpacing: '0.01em',
    transition: 'color 0.2s ease',
  };

  const endIconStyles: React.CSSProperties = {
    position: 'absolute',
    right: '1rem',
    top: '50%',
    transform: 'translateY(-50%)',
    color: colors.helperText,
    display: 'flex',
    alignItems: 'center',
  };

  const messageStyles: React.CSSProperties = {
    fontSize: '0.75rem',
    marginTop: '0.5rem',
    fontWeight: 500,
  };

  const errorStyles: React.CSSProperties = {
    ...messageStyles,
    color: colors.error,
  };

  const successStyles: React.CSSProperties = {
    ...messageStyles,
    color: colors.success,
  };

  const helperTextStyles: React.CSSProperties = {
    ...messageStyles,
    color: colors.helperText,
  };

  return (
    <div style={containerStyles} className={className}>
      {label && (
        <label 
          htmlFor={id} 
          style={{
            ...labelStyles,
            color: isFocused ? colors.primary : colors.labelText
          }}
        >
          {label}
          {required && <span style={{ color: colors.error }}> *</span>}
        </label>
      )}
      <div style={inputContainerStyles}>
        <input
          id={id || inputId}
          name={name}
          type={type}
          placeholder={placeholder}
          value={propValue !== undefined ? propValue : value}
          onChange={handleChange}
          onBlur={(e) => {
            setIsFocused(false);
            if (onBlur) onBlur(e);
          }}
          onFocus={() => setIsFocused(true)}
          disabled={disabled || isLoading}
          required={required}
          onKeyDown={handleKeyDown}
          style={inputStyles}
        />
        {isLoading ? (
          <div style={endIconStyles}>
            <svg
              className="animate-spin h-4 w-4"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              style={{ color: colors.primary }}
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              ></circle>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
          </div>
        ) : (
          endIcon && <div style={endIconStyles}>{endIcon}</div>
        )}
      </div>
      {(error || apiError) && <div style={errorStyles}>{error || apiError}</div>}
      {(success || apiSuccess) && <div style={successStyles}>{success || apiSuccess}</div>}
      {helperText && !error && !success && !apiError && !apiSuccess && (
        <div style={helperTextStyles}>{helperText}</div>
      )}
    </div>
  );
};

export default InputField;
