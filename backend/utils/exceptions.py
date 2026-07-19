"""Custom exceptions and error handlers."""
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


class DeployHubException(Exception):
    """Base exception for DeployHub."""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundException(DeployHubException):
    """Resource not found exception."""
    def __init__(self, resource: str = "Resource"):
        super().__init__(f"{resource} not found", 404)


class ConflictException(DeployHubException):
    """Resource conflict exception."""
    def __init__(self, message: str = "Resource already exists"):
        super().__init__(message, 409)


class ValidationException(DeployHubException):
    """Validation error exception."""
    def __init__(self, message: str = "Validation error"):
        super().__init__(message, 422)


async def deployhub_exception_handler(request: Request, exc: DeployHubException):
    """Handle custom DeployHub exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message, "status_code": exc.status_code}
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code}
    )
