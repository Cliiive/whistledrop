"""
Custom exception classes for the application.
Provides standardized HTTP exceptions for common error cases.
"""
from fastapi import HTTPException, status

class NotFoundError(HTTPException):
    """Exception raised when a requested resource is not found."""
    def __init__(self, detail="Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class FileTypeNotAllowed(HTTPException):
    """Exception raised when an uploaded file has an unsupported type."""
    def __init__(self, detail="File type not allowed"):
        super().__init__(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=detail)

class AuthenticationError(HTTPException):
    """Exception raised when authentication fails."""
    def __init__(self, detail="Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )

class PermissionError(HTTPException):
    """Exception raised when a user doesn't have permission to access a resource."""
    def __init__(self, detail="Not enough permissions"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)
