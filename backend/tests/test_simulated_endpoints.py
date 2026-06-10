import random

from app.routers.simulated import simulate_request

from .helpers import FixedRandom


def test_simulate_request_success_when_roll_below_target():
    status_code, body = simulate_request("tier-99", 0.99, 500, FixedRandom(0.0))

    assert status_code == 200
    assert body == {"status": "ok", "endpoint": "tier-99", "message": None}


def test_simulate_request_failure_when_roll_at_or_above_target():
    status_code, body = simulate_request("tier-99", 0.99, 500, FixedRandom(0.99))

    assert status_code == 500
    assert body["status"] == "error"
    assert body["endpoint"] == "tier-99"
    assert body["message"]


def test_target_uptime_one_always_succeeds():
    status_code, _ = simulate_request("always-up", 1.0, 500, FixedRandom(0.999999))

    assert status_code == 200


def test_target_uptime_zero_always_fails():
    status_code, _ = simulate_request("always-down", 0.0, 500, FixedRandom(0.0))

    assert status_code == 500


def test_simulate_request_statistical_distribution():
    rng = random.Random(12345)
    target_uptime = 0.95
    iterations = 10_000

    successes = sum(
        1
        for _ in range(iterations)
        if simulate_request("tier-95", target_uptime, 503, rng)[0] == 200
    )

    observed_ratio = successes / iterations
    assert abs(observed_ratio - target_uptime) < 0.02


def test_sim_endpoint_success_via_http(make_client):
    client = make_client(FixedRandom(0.0))

    response = client.get("/sim/tier-99")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "endpoint": "tier-99", "message": None}


def test_sim_endpoint_failure_via_http(make_client):
    client = make_client(FixedRandom(0.999999))

    response = client.get("/sim/tier-99")

    assert response.status_code == 500
    body = response.json()
    assert body["status"] == "error"
    assert body["endpoint"] == "tier-99"


def test_unconfigured_path_returns_404(client):
    response = client.get("/sim/does-not-exist")

    assert response.status_code == 404
