from typing import Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    service: str = "sre-alert-testing"


class SimulatedResponse(BaseModel):
    status: Literal["ok", "error"]
    endpoint: str
    message: str | None = None


class EndpointInfo(BaseModel):
    name: str
    path: str
    target_uptime: float


class EndpointStats(EndpointInfo):
    total_requests: int
    success_count: int
    failure_count: int
    observed_success_ratio: float | None = None


class StatsResponse(BaseModel):
    endpoints: list[EndpointStats]
