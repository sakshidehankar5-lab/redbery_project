"""
FastAPI Application Entry Point
"""
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes.documents import router as doc_router
from app.core.config import get_settings
from app.core.exceptions import IDEPBaseException
from app.core.logging import configure_logging, get_logger, request_id_ctx

settings = get_settings()
configure_logging()
log = get_logger(__name__)


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown hooks."""
    log.info(
        f"🚀 {settings.app_name} v{settings.app_version} starting "
        f"[{settings.app_env}]"
    )
    import os
    from pathlib import Path
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    Path("./logs").mkdir(parents=True, exist_ok=True)
    yield
    log.info("👋 Shutting down IDEP")


# ── Application ───────────────────────────────────────────────────────────────

def create_app() -> FastAPI:
    app = FastAPI(
        title="Intelligent Document Extraction Platform",
        description=(
            "AI-powered document data extraction for Aadhaar, "
            "Driving Licence, Passport, and Invoices."
        ),
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # ── CORS ──────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Request ID Middleware (Aspect: logging context) ───────────
    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next):
        req_id = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])
        token = request_id_ctx.set(req_id)
        response = await call_next(request)
        response.headers["X-Request-ID"] = req_id
        request_id_ctx.reset(token)
        return response

    # ── Access Log Middleware ─────────────────────────────────────
    @app.middleware("http")
    async def access_log_middleware(request: Request, call_next):
        import time
        t0 = time.perf_counter()
        response = await call_next(request)
        elapsed = (time.perf_counter() - t0) * 1000
        log.info(
            f"{request.method} {request.url.path} "
            f"→ {response.status_code} [{elapsed:.1f}ms]"
        )
        return response

    # ── Global Exception Handler ──────────────────────────────────
    @app.exception_handler(IDEPBaseException)
    async def idep_exception_handler(request: Request, exc: IDEPBaseException):
        log.error(f"IDEPException: {exc.message} | code={exc.error_code}")
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.to_dict(),
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        log.exception(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=500,
            content={"error_code": "INTERNAL_ERROR", "message": "An unexpected error occurred."},
        )

    # ── Routers ───────────────────────────────────────────────────
    app.include_router(doc_router, prefix="/api/v1")

    return app


app = create_app()
