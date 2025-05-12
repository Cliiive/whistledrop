import React, { useState } from 'react';

export interface ButtonProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'outlined' | 'danger';
  size?: 'small' | 'medium' | 'large';
  fullWidth?: boolean;
  disabled?: boolean;
  onClick?: () => void | Promise<void>;
  className?: string;
  icon?: React.ReactNode;
  type?: 'button' | 'submit' | 'reset';
  loading?: boolean;
}

const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'medium',
  fullWidth = false,
  disabled = false,
  onClick,
  className = '',
  icon,
  type = 'button',
  loading = false,
}) => {
  const [isLoading, setIsLoading] = useState(loading);
  const [isHovered, setIsHovered] = useState(false);

  // Moderne Pastell-Lila Farbpalette
  const colors = {
    primary: '#9C7CF1',  // Pastell-Lila (Hauptfarbe)
    primaryDark: '#7C5CD1', // Dunkleres Lila für Hover
    secondary: '#B8A1F8', // Helleres Pastell-Lila
    secondaryDark: '#A48DE8', // Dunkleres Sekundärlila für Hover
    outlined: '#EBE5FF', // Sehr heller Lila-Hintergrund
    danger: '#F76E8F', // Weiches Rosa-Rot
    dangerDark: '#E05A7A', // Dunkleres Rosa-Rot für Hover
    white: '#FFFFFF',
    gray: '#F5F3FF', // Sehr helles Grau mit Lila-Ton
    text: '#4A3B76', // Dunkles Lila für Text
  };

  const getVariantStyles = (): React.CSSProperties => {
    switch (variant) {
      case 'primary':
        return {
          backgroundColor: isHovered && !disabled ? colors.primaryDark : colors.primary,
          color: colors.white,
          border: 'none',
          boxShadow: isHovered && !disabled ? '0 4px 12px rgba(156, 124, 241, 0.4)' : '0 2px 6px rgba(156, 124, 241, 0.2)',
        };
      case 'secondary':
        return {
          backgroundColor: isHovered && !disabled ? colors.secondaryDark : colors.secondary,
          color: colors.text,
          border: 'none',
          boxShadow: isHovered && !disabled ? '0 4px 12px rgba(184, 161, 248, 0.4)' : '0 2px 6px rgba(184, 161, 248, 0.2)',
        };
      case 'outlined':
        return {
          backgroundColor: isHovered && !disabled ? colors.outlined : 'transparent',
          color: colors.primary,
          border: `1px solid ${colors.primary}`,
          boxShadow: 'none',
        };
      case 'danger':
        return {
          backgroundColor: isHovered && !disabled ? colors.dangerDark : colors.danger,
          color: colors.white,
          border: 'none',
          boxShadow: isHovered && !disabled ? '0 4px 12px rgba(247, 110, 143, 0.4)' : '0 2px 6px rgba(247, 110, 143, 0.2)',
        };
      default:
        return {};
    }
  };

  const getSizeStyles = (): React.CSSProperties => {
    switch (size) {
      case 'small':
        return {
          padding: '0.5rem 1rem',
          fontSize: '0.875rem',
        };
      case 'medium':
        return {
          padding: '0.75rem 1.5rem',
          fontSize: '1rem',
        };
      case 'large':
        return {
          padding: '1rem 2rem',
          fontSize: '1.125rem',
        };
      default:
        return {};
    }
  };

  const baseStyles: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '0.5rem',
    borderRadius: '0.75rem', // Erhöht für moderneres Aussehen
    fontWeight: 600, // Etwas stärker für bessere Lesbarkeit
    transition: 'all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1)',
    cursor: disabled || isLoading ? 'not-allowed' : 'pointer',
    opacity: disabled ? 0.6 : 1,
    width: fullWidth ? '100%' : 'auto',
    letterSpacing: '0.01em', // Subtiles Letter-Spacing für modernes Design
    position: 'relative',
    overflow: 'hidden',
  };

  const handleClick = async () => {
    if (disabled || isLoading || !onClick) return;

    try {
      setIsLoading(true);
      await onClick();
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <button
      type={type}
      className={className}
      style={{ ...baseStyles, ...getVariantStyles(), ...getSizeStyles() }}
      disabled={disabled || isLoading}
      onClick={handleClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {isLoading ? (
        <span className="loading">
          <svg
            className="animate-spin -ml-1 mr-2 h-4 w-4 text-current"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
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
        </span>
      ) : (
        icon && <span className="icon">{icon}</span>
      )}
      {children}
    </button>
  );
};

export default Button;
