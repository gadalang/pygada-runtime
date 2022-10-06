"""Common stuff for tests."""
from pathlib import Path
from pygada_runtime import _cache
from functools import wraps
from typing import Any

TEST_DIR = str(Path(__file__).parent.absolute())
FOO_DIR = str(Path(TEST_DIR) / "foo")
FOO_GADA_YML = str(Path(FOO_DIR) / "gada.yml")
BAR_DIR = str(Path(FOO_DIR) / "bar")
BAR_GADA_YML = str(Path(BAR_DIR) / "gada.yml")


def clean_test(fun: Any) -> Any:
    """Clear gada cache before running test."""

    @wraps(fun)
    def wrapper(*args: list, **kwargs: dict) -> Any:
        _cache.clear()
        return fun(*args, **kwargs)

    return wrapper
