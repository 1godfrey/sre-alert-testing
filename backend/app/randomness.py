import random

# Shared across requests. Override via `app.dependency_overrides` in tests
# (e.g. with a seeded `random.Random(seed)` or a stub) for deterministic
# success/failure outcomes.
_shared_random = random.Random()


def get_random_source() -> random.Random:
    return _shared_random
