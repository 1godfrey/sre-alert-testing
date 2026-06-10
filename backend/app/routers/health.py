from fastapi import APIRouter

from app.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Always returns 200. Indicates the test harness itself is up,
    independent of whatever the simulated endpoints are doing."""
    return HealthResponse()
