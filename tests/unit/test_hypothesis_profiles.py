"""Every run repeats the property tests' inputs, and the weekly run draws new ones from its seed.

`tests/hypothesis_profiles.py` says why there are two profiles (`PL-V067`).
These tests check the three things that make the split work. The `repeatable`
profile draws the same inputs every time. The `exploring` profile draws inputs
that change with its seed and repeat for the same seed. And no property test
sets a profile's setting on its own decorator, because a decorator's setting
overrides the profile, which is how every run drew the same inputs before.
"""

from __future__ import annotations

import ast
from pathlib import Path

import hypothesis.core
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from tests.hypothesis_profiles import EXPLORING, REPEATABLE

ROOT = Path(__file__).resolve().parents[2]

#: The test trees that hold property tests.
TEST_TREES = (ROOT / "tests", ROOT / "subprojects" / "docket" / "tests")

#: The settings each profile decides, which a test's decorator must leave alone.
PROFILE_SETTINGS = frozenset({"derandomize", "database", "deadline", "print_blob"})


def _draws(profile: str) -> list[int]:
    """The integers that a five-example property test draws under `profile`."""
    drawn: list[int] = []

    @settings(settings.get_profile(profile), max_examples=5)
    @given(st.integers())
    def probe(number: int) -> None:
        drawn.append(number)

    probe()
    return drawn


def test_the_repeatable_profile_draws_the_same_inputs_every_time() -> None:
    assert _draws(REPEATABLE) == _draws(REPEATABLE)


def test_the_exploring_profile_draws_inputs_that_its_seed_fixes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The same seed draws the same inputs, and another seed draws others.

    `--hypothesis-seed` sets `hypothesis.core.global_force_seed`, which is
    what the weekly job's seed reaches.
    """
    monkeypatch.setattr(hypothesis.core, "global_force_seed", 20261111)
    first = _draws(EXPLORING)
    assert _draws(EXPLORING) == first
    monkeypatch.setattr(hypothesis.core, "global_force_seed", 20261118)
    assert _draws(EXPLORING) != first


def test_every_run_loads_one_of_the_two_profiles() -> None:
    assert settings.get_current_profile_name() in {REPEATABLE, EXPLORING}


def _decorator_settings(path: Path, root: Path = ROOT) -> list[str]:
    """Each `@settings(...)` decorator in `path` that sets a profile's setting, as `path:line name`.

    The path is written relative to `root`.
    """
    found = []
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call):
                continue
            name = decorator.func
            called = name.attr if isinstance(name, ast.Attribute) else getattr(name, "id", "")
            if called != "settings":
                continue
            for keyword in decorator.keywords:
                if keyword.arg in PROFILE_SETTINGS:
                    relative = path.relative_to(root)
                    found.append(f"{relative}:{decorator.lineno} {keyword.arg}")
    return found


def test_no_property_test_sets_a_setting_that_the_profiles_decide() -> None:
    """A decorator that sets one would keep the weekly run from drawing new inputs for its test."""
    found = [
        finding
        for tree in TEST_TREES
        for path in sorted(tree.rglob("*.py"))
        for finding in _decorator_settings(path)
    ]
    assert found == [], (
        "These property tests set a setting that tests/hypothesis_profiles.py decides. "
        "Remove it from the decorator, so that the profile applies: " + ", ".join(found)
    )


def test_the_check_finds_a_decorator_that_sets_derandomize(tmp_path: Path) -> None:
    """The scan above finds the form that every property test used before `PL-V067`."""
    probe = tmp_path / "probe.py"
    probe.write_text(
        "from hypothesis import given, settings\n"
        "\n"
        "\n"
        "@settings(derandomize=True, database=None, deadline=None, max_examples=5)\n"
        "@given()\n"
        "def test_x() -> None:\n"
        "    pass\n",
        encoding="utf-8",
    )
    assert _decorator_settings(probe, tmp_path) == [
        "probe.py:4 derandomize",
        "probe.py:4 database",
        "probe.py:4 deadline",
    ]
