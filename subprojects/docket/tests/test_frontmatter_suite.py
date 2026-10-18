"""`docket.frontmatter.keys` held to the YAML Test Suite, the oracle for what YAML refuses.

`test_frontmatter_reference.py` holds `keys` to PyYAML over front matters
PyYAML composes, so it cannot see YAML that a conformant parser refuses.
PyYAML is no judge of that either: it implements YAML 1.1, accepts 4 of the
suite's 51 in-domain error cases, and departs from the suite on 37 of the 175
valid cases that carry an expected value (measured 2026-10-12, `PL-P6LL`).
The suite itself is the judge. Its cases are vendored under
`subprojects/docket/tests/yaml-test-suite/`, whose `README.md` says where they
came from and which were kept.

`keys` reads only some of the forms YAML allows, and declines the rest by
raising `Unread`. So on a case YAML reads, `keys` may decline, or it must read
the suite's own top-level keys in order, or no key where the value is no
mapping. On a case YAML refuses, it must decline. Before `PL-P6LL` it read keys
out of 23 of the 51, so a rule's front matter that Claude Code may read no
`paths:` from still passed docket's checks.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from docket.frontmatter import Unread, keys

CASES = json.loads(
    (Path(__file__).parent / "yaml-test-suite" / "cases.json").read_text(encoding="utf-8")
)
ERRORS = [case for case in CASES if case["fail"]]


def _expected(case: dict[str, object]) -> object:
    """The one value the suite expects `case` to load as, or `Ellipsis` where it gives none."""
    text = case.get("json")
    if not isinstance(text, str):
        return ...
    try:
        return json.loads(text) if text.strip() else None
    except json.JSONDecodeError:
        return ...  # several documents


VALID = [case for case in CASES if not case["fail"] and _expected(case) is not ...]


def test_the_vendored_cases_are_the_ones_measured() -> None:
    """The counts `PL-P6LL` measured, so a copy taken again cannot shrink unnoticed."""
    assert (len(CASES), len(ERRORS), len(VALID)) == (254, 51, 175)


@pytest.mark.parametrize("case", ERRORS, ids=[case["id"] for case in ERRORS])
def test_keys_refuses_the_yaml_test_suite_error_cases(case: dict[str, object]) -> None:
    with pytest.raises(Unread):
        keys(str(case["yaml"]).splitlines())


@pytest.mark.parametrize("case", VALID, ids=[case["id"] for case in VALID])
def test_keys_declines_or_reads_the_suite_s_keys_on_its_valid_cases(
    case: dict[str, object],
) -> None:
    expected = _expected(case)
    try:
        found = [key.name for key in keys(str(case["yaml"]).splitlines())]
    except Unread:
        return

    assert found == (list(expected) if isinstance(expected, dict) else [])
