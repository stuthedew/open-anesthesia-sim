"""`tools/config_home_check.py` must refuse a configuration copy that differs from its home.

The direction that matters most is the false green. A copy that changed and
was not reported, or a copy that can no longer be found and is skipped, leaves
the check passing while the files disagree. So the tests change a real home in
a copy of the tree and expect every place that repeats it to be named.
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

import pytest
from config_home_check import FACTS, Fact, Place, _minor, _paths, _ruff_target, check, main

REPO_ROOT = Path(__file__).resolve().parents[2]


def _letters(text: str) -> str:
    """Return the single letters in `text`, sorted, as a fixture's compared form."""

    return ", ".join(sorted(set(re.findall(r"\b[a-z]\b", text))))


def _copy_of_the_tree(root: Path) -> None:
    """Copy every file a fact reads into `root`, at its own path."""

    for fact in FACTS:
        for place in (fact.home, *fact.copies):
            for source in REPO_ROOT.glob(place.path):
                target = root / source.relative_to(REPO_ROOT)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)


def test_the_repository_s_configuration_copies_all_match_their_homes(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(["--root", str(REPO_ROOT)]) == 0
    assert ", 0 errors" in capsys.readouterr().out


def test_every_copy_of_every_fact_is_found_in_the_repository() -> None:
    findings, compared = check(REPO_ROOT)

    assert findings == []
    assert compared >= sum(len(fact.copies) for fact in FACTS)


def test_a_changed_python_release_names_each_file_still_giving_the_old_one(tmp_path: Path) -> None:
    _copy_of_the_tree(tmp_path)
    (tmp_path / ".python-version").write_text("3.15.2\n", encoding="utf-8")

    findings, _ = check(tmp_path)

    assert sorted((finding.path, finding.found, finding.expected) for finding in findings) == [
        ("README.md", "3.14", "3.15"),
        ("pyproject.toml", "3.14", "3.15"),
        ("pyproject.toml", "3.14", "3.15"),
    ]


def test_a_changed_workflow_action_pin_names_every_workflow_left_on_the_old_one(
    tmp_path: Path,
) -> None:
    _copy_of_the_tree(tmp_path)
    quality = tmp_path / ".github" / "workflows" / "quality.yml"
    text = quality.read_text(encoding="utf-8")
    old = text.split("uses: actions/checkout@", 1)[1].split()[0]
    quality.write_text(
        text.replace(f"actions/checkout@{old}", "actions/checkout@v99"), encoding="utf-8"
    )

    findings = [f for f in check(tmp_path)[0] if f.fact == "the version of actions/checkout"]

    assert findings
    assert {finding.found for finding in findings} == {old}
    assert ".github/workflows/quality.yml" not in {finding.path for finding in findings}


def test_a_copy_that_can_no_longer_be_found_is_a_finding(tmp_path: Path) -> None:
    (tmp_path / "home.txt").write_text("limit = 15\n", encoding="utf-8")
    (tmp_path / "copy.md").write_text("The job stops after fifteen minutes.\n", encoding="utf-8")
    fact = Fact(
        "the limit",
        Place("home.txt", r"^limit = (\d+)$"),
        (Place("copy.md", r"stops after (\d+) minutes"),),
    )

    findings, compared = check(tmp_path, (fact,))

    assert compared == 0
    assert [str(finding) for finding in findings] == [
        "copy.md: the limit is no longer found where this check reads it"
    ]


def test_a_home_that_gives_two_values_is_a_finding_and_no_copy_is_compared(tmp_path: Path) -> None:
    (tmp_path / "home.txt").write_text("limit = 15\nlimit = 20\n", encoding="utf-8")
    (tmp_path / "copy.md").write_text("stops after 15 minutes\n", encoding="utf-8")
    fact = Fact(
        "the limit",
        Place("home.txt", r"^limit = (\d+)$"),
        (Place("copy.md", r"stops after (\d+) minutes"),),
    )

    findings, compared = check(tmp_path, (fact,))

    assert compared == 0
    assert [(finding.path, finding.found) for finding in findings] == [("home.txt", "15, 20")]


def test_a_differing_copy_is_named_with_both_values(tmp_path: Path) -> None:
    (tmp_path / "home.txt").write_text("limit = 15\n", encoding="utf-8")
    (tmp_path / "copy.md").write_text("stops after 15 minutes, or 20 minutes\n", encoding="utf-8")
    fact = Fact(
        "the limit", Place("home.txt", r"^limit = (\d+)$"), (Place("copy.md", r"(\d+) minutes"),)
    )

    findings, compared = check(tmp_path, (fact,))

    assert compared == 2
    assert [str(finding) for finding in findings] == [
        "copy.md: the limit is '20' here, and '15' at its home"
    ]


def test_a_collected_place_takes_its_matches_together(tmp_path: Path) -> None:
    (tmp_path / "Makefile").write_text("\trun b\n\trun a\n", encoding="utf-8")
    (tmp_path / "doc.md").write_text("We run `a` and `b`.\n", encoding="utf-8")
    fact = Fact(
        "what runs",
        Place("Makefile", r"^\trun (\w)$", _letters, collect=True),
        (Place("doc.md", r"We run (.*)\.", _letters),),
    )

    findings, compared = check(tmp_path, (fact,))

    assert findings == []
    assert compared == 1


@pytest.mark.parametrize(
    ("read", "text", "expected"),
    [
        (_minor, "3.14.7", "3.14"),
        (_minor, "3.15", "3.15"),
        (_ruff_target, "py314", "3.14"),
        (_ruff_target, "py39", "3.9"),
        (_paths, "`src/a/`, `docs/B.md` or `src/a`", "docs/B.md, src/a"),
        (_paths, '"src/a", "docs/B.md",', "docs/B.md, src/a"),
    ],
)
def test_each_reading_turns_a_place_s_spelling_into_the_compared_form(
    read: object, text: str, expected: str
) -> None:
    assert callable(read)
    assert read(text) == expected
