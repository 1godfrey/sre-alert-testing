from fastapi import APIRouter, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST

from app.schemas import EndpointStats, StatsResponse

router = APIRouter()


@router.get("/stats", response_model=StatsResponse)
async def stats(request: Request) -> StatsResponse:
    config = request.app.state.endpoints_config
    metrics = request.app.state.metrics

    endpoint_stats = []
    for endpoint in config.endpoints:
        success_count, failure_count = metrics.get_counts(endpoint.name)
        total_requests = success_count + failure_count
        observed_success_ratio = (success_count / total_requests) if total_requests else None

        endpoint_stats.append(
            EndpointStats(
                name=endpoint.name,
                path=endpoint.path,
                target_uptime=endpoint.target_uptime,
                total_requests=total_requests,
                success_count=success_count,
                failure_count=failure_count,
                observed_success_ratio=observed_success_ratio,
            )
        )

    return StatsResponse(endpoints=endpoint_stats)


@router.get("/metrics")
async def metrics_endpoint(request: Request) -> Response:
    metrics = request.app.state.metrics
    return Response(content=metrics.generate_latest(), media_type=CONTENT_TYPE_LATEST)
