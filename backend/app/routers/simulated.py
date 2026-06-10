import random

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.config_models import EndpointConfig
from app.metrics import MetricsStore
from app.randomness import get_random_source
from app.schemas import SimulatedResponse


def simulate_request(
    name: str,
    target_uptime: float,
    error_status_code: int,
    random_source: random.Random,
) -> tuple[int, dict]:
    """Roll the dice for one request to a simulated endpoint.

    A roll strictly less than `target_uptime` is a success (200);
    otherwise `error_status_code` is returned. This makes
    target_uptime=1.0 always succeed and target_uptime=0.0 always fail.
    """
    roll = random_source.random()

    if roll < target_uptime:
        return 200, SimulatedResponse(status="ok", endpoint=name).model_dump()

    return error_status_code, SimulatedResponse(
        status="error", endpoint=name, message="Simulated failure"
    ).model_dump()


def build_simulated_router(endpoints: list[EndpointConfig], metrics: MetricsStore) -> APIRouter:
    """Programmatically register one GET route per configured endpoint."""
    router = APIRouter()

    for endpoint in endpoints:
        metrics.register_endpoint(endpoint.name, endpoint.target_uptime)
        router.add_api_route(
            endpoint.path,
            _make_handler(endpoint, metrics),
            methods=["GET"],
            name=endpoint.name,
            summary=f"Simulated endpoint with target uptime {endpoint.target_uptime:.0%}",
            response_model=SimulatedResponse,
        )

    return router


def _make_handler(endpoint: EndpointConfig, metrics: MetricsStore):
    async def handler(random_source: random.Random = Depends(get_random_source)) -> JSONResponse:
        status_code, body = simulate_request(
            endpoint.name,
            endpoint.target_uptime,
            endpoint.error_status_code,
            random_source,
        )
        metrics.record_result(endpoint.name, success=status_code == 200)
        return JSONResponse(content=body, status_code=status_code)

    return handler
