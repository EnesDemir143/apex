"""FastAPI exception handler registration."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from apex.core.exceptions import ApexError


def register_error_handlers(app: FastAPI) -> None:
    """Register structured JSON exception handlers."""

    @app.exception_handler(ApexError)
    async def apex_error_handler(request: Request, exc: ApexError) -> JSONResponse:
        del request
        return JSONResponse(
            status_code=400,
            content={"error": {"type": exc.__class__.__name__, "message": str(exc)}},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        del request
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "type": "ValidationError",
                    "message": "Request validation failed",
                    "details": exc.errors(),
                }
            },
        )

    @app.exception_handler(Exception)
    async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
        del request, exc
        return JSONResponse(
            status_code=500,
            content={"error": {"type": "InternalServerError", "message": "Internal server error"}},
        )
