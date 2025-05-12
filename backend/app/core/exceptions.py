from fastapi import HTTPException, status

class NotFoundError(HTTPException):
    def __init__(self, detail="Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class FileTypeNotAllowed(HTTPException):
    def __init__(self, detail="File type not allowed"):
        super().__init__(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=detail)

class AuthenticationError(HTTPException):
    def __init__(self, detail="Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )

class PermissionError(HTTPException):
    def __init__(self, detail="Not enough permissions"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)