# exceptions.py
from fastapi import Request, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

def register_exception_handlers(app: FastAPI):
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        errors = []
        for err in exc.errors():
            loc = list(err.get("loc", []))
            if loc and loc[0] == "body":
                loc = loc[1:]
            errors.append({
                "field": ".".join(str(item) for item in loc),
                "message": err.get("msg")
            })
        return JSONResponse(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error_code": "VALIDATION_ERROR",
                "error_message": "One or more validation errors occurred.",
                "errors": errors
            }
        )
