from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from app.config_models import load_endpoints_config
from app.metrics import MetricsStore
from app.routers import health, stats
from app.routers.simulated import build_simulated_router
from app.schemas import EndpointInfo
from app.settings import Settings, get_settings


def create_app(settings: Settings) -> FastAPI:
    try:
        config = load_endpoints_config(
            settings.endpoints_config_path, settings.default_error_status_code
        )
    except (OSError, ValidationError) as exc:
        raise RuntimeError(
            f"Failed to load endpoints config from "
            f"'{settings.endpoints_config_path}': {exc}"
        ) from exc

    metrics = MetricsStore()

    app = FastAPI(
        title="SRE Alert Testing",
        description="Simulated endpoints with configurable uptime tiers, "
        "for practicing SRE alerting and incident dashboards.",
        version="0.1.0",
    )
    app.state.settings = settings
    app.state.endpoints_config = config
    app.state.metrics = metrics

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(build_simulated_router(config.endpoints, metrics))
    app.include_router(stats.router)

    @app.get("/", response_model=list[EndpointInfo])
    async def index() -> list[EndpointInfo]:
        """Lists the configured simulated endpoints for discoverability."""
        return [
            EndpointInfo(name=e.name, path=e.path, target_uptime=e.target_uptime)
            for e in config.endpoints
        ]

    return app


app = create_app(get_settings())


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        log_level=settings.log_level,
    )
