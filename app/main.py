from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.config import settings
from app.storage.redis_client import redis_manager
from app.utils.logger import app_logger
from app.utils.metrics import MetricsCollectorMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown event lifecycle manager."""
    app_logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}...")

    # Pre-warm heavy ML models at startup so first request is fast
    try:
        from app.embeddings.embedding_model import EmbeddingModel
        app_logger.info(f"Pre-warming embedding model '{settings.MODEL_NAME}'...")
        EmbeddingModel.load(settings.MODEL_NAME)
        app_logger.success("Embedding model ready.")
    except Exception as e:
        app_logger.warning(f"Embedding model pre-warm skipped: {e}")

    # The large cross-encoder is intentionally opt-in on CPU.  It can add tens
    # of seconds per query; enable it only when the precision trade-off is worth it.
    if settings.ENABLE_RERANKER:
        try:
            from app.reranker.model import RerankerModel
            app_logger.info(f"Pre-warming reranker model '{settings.RERANKER_MODEL_NAME}'...")
            RerankerModel.load(settings.RERANKER_MODEL_NAME)
            app_logger.success("Reranker model ready.")
        except Exception as e:
            app_logger.warning(f"Reranker model pre-warm skipped: {e}")

    yield
    app_logger.info("Closing Redis connection pool...")
    await redis_manager.close()
    app_logger.info(f"{settings.APP_NAME} shutdown complete.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# Enable CORS for Enterprise Web Apps & Microservices
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Metrics middleware
app.add_middleware(MetricsCollectorMiddleware)

from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Include API Router under /api/v1
app.include_router(api_router, prefix="/api/v1")

# Mount frontend static assets & landing page
frontend_dir = Path(__file__).parent.parent / "enterprise-rag-frontend" / "dist"
if not frontend_dir.exists():
    frontend_dir = Path(__file__).parent.parent / "frontend"

if frontend_dir.exists():
    if (frontend_dir / "assets").exists():
        app.mount("/assets", StaticFiles(directory=str(frontend_dir / "assets")), name="assets")

    @app.get("/{full_path:path}", response_class=FileResponse)
    async def serve_frontend(full_path: str):
        if full_path.startswith("api/") or full_path in ["docs", "openapi.json", "redoc"]:
            raise HTTPException(status_code=404, detail="API endpoint not found")
        file_path = frontend_dir / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(frontend_dir / "index.html")
