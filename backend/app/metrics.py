import threading
from dataclasses import dataclass

from prometheus_client import CollectorRegistry, Counter, Gauge, generate_latest


@dataclass
class _Counts:
    success: int = 0
    failure: int = 0


class MetricsStore:
    """Tracks observed request outcomes per simulated endpoint.

    Backs both the Prometheus-format `/metrics` endpoint (via the wrapped
    `CollectorRegistry`) and the JSON `/stats` endpoint (via the plain
    in-memory counters). Each app instance gets its own registry so tests
    don't hit prometheus_client's duplicate-registration errors.
    """

    def __init__(self) -> None:
        self.registry = CollectorRegistry()
        self._lock = threading.Lock()
        self._counts: dict[str, _Counts] = {}

        self.requests_total = Counter(
            "sim_requests_total",
            "Total simulated requests, partitioned by outcome",
            ["endpoint", "outcome"],
            registry=self.registry,
        )
        self.target_uptime_ratio = Gauge(
            "sim_target_uptime_ratio",
            "Configured target success ratio for a simulated endpoint",
            ["endpoint"],
            registry=self.registry,
        )

    def register_endpoint(self, name: str, target_uptime: float) -> None:
        with self._lock:
            self._counts.setdefault(name, _Counts())

        self.target_uptime_ratio.labels(endpoint=name).set(target_uptime)
        # Touch both outcome series so they appear in /metrics at 0 before
        # the first request, rather than only after a failure/success occurs.
        self.requests_total.labels(endpoint=name, outcome="success")
        self.requests_total.labels(endpoint=name, outcome="failure")

    def record_result(self, name: str, success: bool) -> None:
        outcome = "success" if success else "failure"
        self.requests_total.labels(endpoint=name, outcome=outcome).inc()

        with self._lock:
            counts = self._counts.setdefault(name, _Counts())
            if success:
                counts.success += 1
            else:
                counts.failure += 1

    def get_counts(self, name: str) -> tuple[int, int]:
        with self._lock:
            counts = self._counts.get(name, _Counts())
            return counts.success, counts.failure

    def generate_latest(self) -> bytes:
        return generate_latest(self.registry)
