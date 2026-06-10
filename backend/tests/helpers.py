from pathlib import Path

# The endpoints config shipped with the repo, used as the test fixture too -
# keeps tests honest about what's actually deployed.
CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "endpoints.yaml"


class FixedRandom:
    """A random.Random-like stub whose .random() always returns a fixed value."""

    def __init__(self, value: float) -> None:
        self.value = value

    def random(self) -> float:
        return self.value
