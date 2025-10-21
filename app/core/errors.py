from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class DomainError(Exception):
    def __init__(
        self, message: str, code: str = "domain_error", status_code: int = 400
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code

    # Example usage:
    # raise DomainError("Payment failed", code="payment_failed", status_code=402)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def handle_domain_error(request: Request, exc: DomainError):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {"code": exc.code, "message": exc.message},
                "path": str(request.url),
            },
        )

    # handle generic 500 errors.
    @app.exception_handler(500)
    async def handle_generic_500_exception(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "internal_server_error",
                    "message": str(exc),
                },
                "path": str(request.url),
            },
        )

    # handle 404 errors.
    @app.exception_handler(404)
    async def handle_404_error(request: Request, exc: Exception):
        return JSONResponse(
            status_code=404,
            content={
                "error": {
                    "code": "not_found",
                    "message": f"Resource not found. {str(exc)}",
                },
                "path": str(request.url),
            },
        )
