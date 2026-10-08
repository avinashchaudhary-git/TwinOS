from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.admin import router as admin_router
from app.api.v1.alerts import router as alerts_router
from app.api.v1.assistant import router as assistant_router
from app.api.v1.auth import router as auth_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.graph import router as graph_router

# Import API Routers
from app.api.v1.health import router as health_router
from app.api.v1.integrations import router as integrations_router
from app.api.v1.risk import router as risk_router
from app.api.v1.sync import router as sync_router
from app.api.v1.tasks import router as tasks_router
from app.api.v1.users import router as users_router
from app.core.config import settings
from app.core.logging import logger
from app.db.neo4j_client import neo4j_client
from app.db.postgres import Base, engine
from app.scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup sequence
    logger.info("Initializing TwinOS Platform services...")
    try:
        # Create tables (idempotent fallback)
        Base.metadata.create_all(bind=engine)
        # Bootstrap graph constraints
        neo4j_client.bootstrap_constraints()
        # Start scheduler
        start_scheduler()
    except Exception as e:
        logger.error(f"Error during TwinOS startup: {e}")

    yield

    # Shutdown sequence
    logger.info("Shutting down TwinOS Platform services...")
    stop_scheduler()
    neo4j_client.close()


def create_app() -> FastAPI:
    app = FastAPI(
        title="TwinOS API",
        description="An AI-Powered Digital Twin Operating System for Organizations",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/api/v1/openapi.json",
        lifespan=lifespan,
    )

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list + ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register Routers under /api/v1
    api_prefix = "/api/v1"
    app.include_router(health_router, prefix=api_prefix)
    app.include_router(auth_router, prefix=api_prefix)
    app.include_router(users_router, prefix=api_prefix)
    app.include_router(admin_router, prefix=api_prefix)
    app.include_router(integrations_router, prefix=api_prefix)
    app.include_router(sync_router, prefix=api_prefix)
    app.include_router(graph_router, prefix=api_prefix)
    app.include_router(assistant_router, prefix=api_prefix)
    app.include_router(risk_router, prefix=api_prefix)
    app.include_router(dashboard_router, prefix=api_prefix)
    app.include_router(alerts_router, prefix=api_prefix)
    app.include_router(tasks_router, prefix=api_prefix)

    @app.get("/")
    def root():
        return {
            "title": "TwinOS: Digital Twin Operating System",
            "version": "1.0.0",
            "docs": "/docs",
            "health": f"{api_prefix}/health",
        }

    return app


app = create_app()
