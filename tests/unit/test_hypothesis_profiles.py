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

#: This file, whose probe names a profile as its parent on purpose.
THIS_FILE = Path(__file__).resolve()

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
    """Each call in `path` that fixes a property test's inputs, as `path:line what`.

    That is a `settings(...)` call that sets a profile's setting or names a
    parent settings object, which may set one, and any call of Hypothesis's
    `seed`. The scan reads every call, not only decorators, so a settings
    object built once and applied by name is found where it is built. The path
    is written relative to `root`.
    """
    found = []
    relative = path.relative_to(root)
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if not isinstance(node, ast.Call):
            continue
        name = node.func
        called = name.attr if isinstance(name, ast.Attribute) else getattr(name, "id", "")
        if called == "seed":
            found.append(f"{relative}:{node.lineno} seed")
        elif called == "settings":
            if node.args:
                found.append(f"{relative}:{node.lineno} parent")
            found.extend(
                f"{relative}:{node.lineno} {keyword.arg}"
                for keyword in node.keywords
                if keyword.arg in PROFILE_SETTINGS
            )
    return found


def test_no_property_test_sets_a_setting_that_the_profiles_decide() -> None:
    """Such a call would keep the weekly run from drawing new inputs for its test."""
    found = [
        finding
        for tree in TEST_TREES
        for path in sorted(tree.rglob("*.py"))
        if path != THIS_FILE
        for finding in _decorator_settings(path)
    ]
    assert found == [], (
        "These calls fix a property test's inputs, which tests/hypothesis_profiles.py "
        "decides. Set only max_examples, so that the profile applies: " + ", ".join(found)
    )


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (
            "@settings(derandomize=True, database=None, deadline=None, max_examples=5)\n",
            ["probe.py:1 derandomize", "probe.py:1 database", "probe.py:1 deadline"],
        ),
        (
            "@settings(settings(derandomize=True), max_examples=5)\n",
            ["probe.py:1 parent", "probe.py:1 derandomize"],
        ),
        ("PINNED = settings(derandomize=True)\n", ["probe.py:1 derandomize"]),
        ("@seed(1)\n", ["probe.py:1 seed"]),
        ("@settings(max_examples=5)\n", []),
    ],
)
def test_the_check_finds_each_way_a_test_fixes_its_inputs(
    tmp_path: Path, source: str, expected: list[str]
) -> None:
    """The form every property test used before `PL-V067`, and the three others a review named."""
    probe = tmp_path / "probe.py"
    probe.write_text(source + "def test_x() -> None:\n    pass\n", encoding="utf-8")
    assert _decorator_settings(probe, tmp_path) == expected
