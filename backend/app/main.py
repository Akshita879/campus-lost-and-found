import logging
from pathlib import Path
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings
from app.routers import auth_router, reports_router, claims_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("campus_lost_found")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Campus Lost & Found Portal REST API — Centralized platform for reporting and matching lost & found campus belongings.",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Uploads directory
app.mount(
    f"/{settings.UPLOAD_DIR}",
    StaticFiles(directory=str(settings.upload_path)),
    name="uploads"
)

# Optional: Mount frontend directory if it exists
frontend_dir = Path(__file__).resolve().parent.parent.parent / "frontend"
if frontend_dir.exists():
    app.mount(
        "/ui",
        StaticFiles(directory=str(frontend_dir), html=True),
        name="frontend"
    )

# Include Routers under API_V1_STR
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(reports_router, prefix=settings.API_V1_STR)
app.include_router(claims_router, prefix=settings.API_V1_STR)


# Centralized Exception Handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "status_code": exc.status_code,
            "message": exc.detail,
            "error_type": "HTTPException"
        },
        headers=getattr(exc, "headers", None)
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error.get("loc", []))
        errors.append({
            "field": field,
            "message": error.get("msg"),
            "type": error.get("type")
        })
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "status_code": 422,
            "message": "Validation failed for request parameters or body",
            "errors": errors,
            "error_type": "ValidationError"
        }
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error processing {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "status_code": 500,
            "message": "An unexpected internal server error occurred. Please try again later.",
            "error_type": "InternalServerError"
        }
    )


@app.get("/health", tags=["System"])
def health_check():
    """Health check endpoint to verify backend operational readiness."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }


@app.get("/", tags=["System"])
def root():
    """Root endpoint providing service metadata and documentation links."""
    return {
        "message": f"Welcome to the {settings.PROJECT_NAME} API",
        "documentation": "/docs",
        "redoc": "/redoc",
        "ui": "/ui/",
        "api_v1": settings.API_V1_STR
    }
