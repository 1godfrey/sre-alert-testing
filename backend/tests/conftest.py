import random

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.main import create_app
from app.randomness import get_random_source
from app.settings import Settings

from .helpers import CONFIG_PATH


@pytest.fixture
def test_settings() -> Settings:
    return Settings(endpoints_config_path=CONFIG_PATH)


@pytest.fixture
def app_instance(test_settings: Settings) -> FastAPI:
    return create_app(test_settings)


@pytest.fixture
def client(app_instance: FastAPI) -> TestClient:
    return TestClient(app_instance)


@pytest.fixture
def make_client(app_instance: FastAPI):
    """Factory fixture: make_client(random_source) -> TestClient whose
    /sim/* routes draw from the given random source instead of the real one."""

    def _make_client(random_source: random.Random) -> TestClient:
        app_instance.dependency_overrides[get_random_source] = lambda: random_source
        return TestClient(app_instance)

    return _make_client
