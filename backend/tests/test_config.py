import pytest
from pydantic import ValidationError

from app.config_models import EndpointsConfig, load_endpoints_config

from .helpers import CONFIG_PATH


def test_load_default_config():
    config = load_endpoints_config(CONFIG_PATH, default_error_status_code=503)

    by_name = {endpoint.name: endpoint for endpoint in config.endpoints}
    assert set(by_name) == {"tier-99", "tier-95", "tier-75"}

    assert by_name["tier-99"].path == "/sim/tier-99"
    assert by_name["tier-99"].target_uptime == 0.99
    assert by_name["tier-99"].error_status_code == 500

    assert by_name["tier-95"].error_status_code == 503
    assert by_name["tier-75"].error_status_code == 503


def test_default_error_status_code_applied_when_omitted(tmp_path):
    config_file = tmp_path / "endpoints.yaml"
    config_file.write_text(
        "endpoints:\n  - name: a\n    path: /a\n    target_uptime: 0.5\n"
    )

    config = load_endpoints_config(config_file, default_error_status_code=502)

    assert config.endpoints[0].error_status_code == 502


def test_target_uptime_out_of_range_rejected():
    with pytest.raises(ValidationError):
        EndpointsConfig.model_validate(
            {"endpoints": [{"name": "bad", "path": "/bad", "target_uptime": 1.5}]}
        )


def test_path_must_start_with_slash():
    with pytest.raises(ValidationError):
        EndpointsConfig.model_validate(
            {"endpoints": [{"name": "bad", "path": "bad", "target_uptime": 0.5}]}
        )


def test_duplicate_names_rejected():
    with pytest.raises(ValidationError):
        EndpointsConfig.model_validate(
            {
                "endpoints": [
                    {"name": "dup", "path": "/a", "target_uptime": 0.5},
                    {"name": "dup", "path": "/b", "target_uptime": 0.5},
                ]
            }
        )


def test_duplicate_paths_rejected():
    with pytest.raises(ValidationError):
        EndpointsConfig.model_validate(
            {
                "endpoints": [
                    {"name": "a", "path": "/dup", "target_uptime": 0.5},
                    {"name": "b", "path": "/dup", "target_uptime": 0.5},
                ]
            }
        )
