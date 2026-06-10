from .helpers import FixedRandom


def test_stats_and_metrics_reflect_recorded_results(make_client):
    success_client = make_client(FixedRandom(0.0))
    success_client.get("/sim/tier-99")
    success_client.get("/sim/tier-99")

    failure_client = make_client(FixedRandom(0.999999))
    failure_client.get("/sim/tier-99")

    stats_response = success_client.get("/stats")
    assert stats_response.status_code == 200

    endpoints = {e["name"]: e for e in stats_response.json()["endpoints"]}
    tier_99 = endpoints["tier-99"]
    assert tier_99["total_requests"] == 3
    assert tier_99["success_count"] == 2
    assert tier_99["failure_count"] == 1
    assert abs(tier_99["observed_success_ratio"] - (2 / 3)) < 1e-9

    untouched = endpoints["tier-95"]
    assert untouched["total_requests"] == 0
    assert untouched["observed_success_ratio"] is None

    metrics_response = success_client.get("/metrics")
    assert metrics_response.status_code == 200

    body = metrics_response.text
    assert 'sim_requests_total{endpoint="tier-99",outcome="success"} 2.0' in body
    assert 'sim_requests_total{endpoint="tier-99",outcome="failure"} 1.0' in body
    assert 'sim_target_uptime_ratio{endpoint="tier-99"} 0.99' in body


def test_index_lists_configured_endpoints(client):
    response = client.get("/")

    assert response.status_code == 200
    names = {entry["name"] for entry in response.json()}
    assert names == {"tier-99", "tier-95", "tier-75"}
