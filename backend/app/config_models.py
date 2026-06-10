from pathlib import Path

import yaml
from pydantic import BaseModel, Field, field_validator, model_validator


class EndpointConfig(BaseModel):
    """A single simulated endpoint and its target uptime."""

    name: str
    path: str
    target_uptime: float = Field(ge=0.0, le=1.0)
    error_status_code: int | None = None

    @field_validator("path")
    @classmethod
    def path_must_start_with_slash(cls, value: str) -> str:
        if not value.startswith("/"):
            raise ValueError("path must start with '/'")
        return value


class EndpointsConfig(BaseModel):
    endpoints: list[EndpointConfig]

    @model_validator(mode="after")
    def check_unique_names_and_paths(self) -> "EndpointsConfig":
        names = [endpoint.name for endpoint in self.endpoints]
        paths = [endpoint.path for endpoint in self.endpoints]

        if len(names) != len(set(names)):
            raise ValueError("endpoint 'name' values must be unique")
        if len(paths) != len(set(paths)):
            raise ValueError("endpoint 'path' values must be unique")

        return self


def load_endpoints_config(path: Path, default_error_status_code: int) -> EndpointsConfig:
    """Load and validate the simulated endpoints config from a YAML file.

    Any endpoint that omits `error_status_code` falls back to
    `default_error_status_code`.
    """
    with open(path, "r", encoding="utf-8") as config_file:
        raw_config = yaml.safe_load(config_file)

    config = EndpointsConfig.model_validate(raw_config)

    for endpoint in config.endpoints:
        if endpoint.error_status_code is None:
            endpoint.error_status_code = default_error_status_code

    return config
