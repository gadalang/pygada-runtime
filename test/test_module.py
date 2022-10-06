"""Tests on the **pygada_runtime.module** module."""
from __future__ import annotations
import pytest
from typing import TYPE_CHECKING
from pygada_runtime import module
from test import foo
from test.foo import bar
from test.conftest import (
    FOO_DIR,
    BAR_DIR,
    FOO_GADA_YML,
    BAR_GADA_YML,
    clean_test,
)

if TYPE_CHECKING:
    from typing import Any, Iterable
    from pkgutil import ModuleInfo
    from pygada_runtime.module import ModuleLike


def _assert_modules(
    modules: Iterable[ModuleInfo], expected: list[str], unexpected: list[str]
) -> None:
    paths = [module.module_path(_) for _ in modules]
    # Those are in PYTHONPATH and should be returned
    for _ in expected:
        assert _ in paths
    # Those are subpackages and should not be returned
    for _ in unexpected:
        assert _ not in paths


@pytest.mark.module
@pytest.mark.parametrize(
    "mod,expected",
    [
        ("foo", "foo"),
        ("test.foo", "test.foo"),
        (foo, "test.foo"),
        ("foo.bar", "foo.bar"),
        ("test.foo.bar", "test.foo.bar"),
        (bar, "test.foo.bar"),
    ],
)
@clean_test
def test_module_name(mod: ModuleLike, expected: str) -> None:
    """Test **module_name** returns the correct name."""
    assert module.module_name(mod) == expected


@pytest.mark.module
@pytest.mark.parametrize(
    "mod,expected",
    [
        ("foo", FOO_DIR),
        ("test.foo", FOO_DIR),
        (foo, FOO_DIR),
        ("foo.bar", BAR_DIR),
        ("test.foo.bar", BAR_DIR),
        (bar, BAR_DIR),
    ],
)
@clean_test
def test_module_path(mod: ModuleLike, expected: str) -> None:
    """Test **module_path** returns the correct absolute path."""
    assert module.module_path(mod) == expected


@pytest.mark.module
@pytest.mark.parametrize(
    "mod,expected",
    [
        ("foo", FOO_GADA_YML),
        ("test.foo", FOO_GADA_YML),
        (foo, FOO_GADA_YML),
        ("foo.bar", BAR_GADA_YML),
        ("test.foo.bar", BAR_GADA_YML),
        (bar, BAR_GADA_YML),
    ],
)
@clean_test
def test_gada_yml_path(mod: ModuleLike, expected: str) -> None:
    """Test **gada_yml_path** returns the correct absolute path."""
    assert module.gada_yml_path(mod) == expected


@pytest.mark.module
@pytest.mark.parametrize(
    "fun,mod,expected,unexpected",
    [
        (module.iter_modules, None, [FOO_DIR], [BAR_DIR]),
        (module.walk_modules, None, [FOO_DIR, BAR_DIR], []),
        (module.iter_modules, "test", [FOO_DIR], [BAR_DIR]),
        (module.walk_modules, "test", [FOO_DIR, BAR_DIR], []),
        (module.iter_modules, "test.foo", [BAR_DIR], []),
        (module.walk_modules, "test.foo", [BAR_DIR], []),
    ],
)
@clean_test
def test_iter_modules(
    fun: Any, mod: ModuleLike, expected: list[str], unexpected: list[str]
) -> None:
    """Test both **iter_modules** and **walk_modules**."""
    _assert_modules(fun(mod), expected, unexpected)
