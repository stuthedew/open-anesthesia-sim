"""`tools/duplicate_code_check.py` must refuse a copied block that its baseline does not allow.

The false green that matters is a copy that pylint reports and the check
passes: a message it cannot read, or a pair it counts wrongly. So the tests
run pylint on two small modules that share a block, and read canned messages
for each way the count can go.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from duplicate_code_check import ALLOWED_BLOCKS, compare, main, pairs, run_pylint

SHARED = """
def total(values):
    found = 0
    for value in values:
        if value > 0:
            found += value
        else:
            found -= value
    return found
"""


def _message(*spans: str) -> dict[str, object]:
    body = "\n".join(f"=={span}" for span in spans)
    return {"symbol": "duplicate-code", "message": f"Similar lines in 2 files\n{body}\n    x = 1"}


def test_two_modules_sharing_a_block_are_one_pair_with_one_block(tmp_path: Path) -> None:
    for tree in ("src", "tools", "subprojects/docket/src"):
        (tmp_path / tree).mkdir(parents=True)
    (tmp_path / "tools" / "first.py").write_text(SHARED, encoding="utf-8")
    (tmp_path / "tools" / "second.py").write_text("X = 1\n" + SHARED, encoding="utf-8")

    found = pairs(run_pylint(tmp_path))

    assert dict(found) == {("first", "second"): 1}
    assert compare(found, {}) == [
        "first and second: 1 copied block(s), and the baseline allows 0. Read the shared "
        "rule from one module; the baseline does not grow."
    ]


def test_a_pair_is_counted_the_same_whichever_module_pylint_names_first() -> None:
    found = pairs([_message("b:[1:9]", "a:[3:11]"), _message("a:[20:28]", "b:[30:38]")])

    assert dict(found) == {("a", "b"): 2}


def test_messages_other_than_duplicate_code_are_not_counted() -> None:
    assert not pairs([{"symbol": "unused-import", "message": "==a:[1:2]\n==b:[1:2]"}])


def test_a_duplicate_code_message_naming_one_module_is_refused_rather_than_skipped() -> None:
    with pytest.raises(ValueError, match="not two or more modules"):
        pairs([_message("a:[1:9]", "a:[20:28]")])


def test_a_block_in_three_modules_counts_once_for_each_pair_of_them() -> None:
    found = pairs([_message("c:[1:9]", "a:[3:11]", "b:[5:13]")])

    assert dict(found) == {("a", "b"): 1, ("a", "c"): 1, ("b", "c"): 1}


def test_a_module_pylint_cannot_parse_fails_the_run_rather_than_dropping_out(
    tmp_path: Path,
) -> None:
    for tree in ("src", "tools", "subprojects/docket/src"):
        (tmp_path / tree).mkdir(parents=True)
    (tmp_path / "src" / "first.py").write_text(SHARED, encoding="utf-8")
    (tmp_path / "src" / "broken.py").write_text("def f(:\n", encoding="utf-8")

    with pytest.raises(RuntimeError, match="src/broken.py"):
        run_pylint(tmp_path)


def test_a_pylintrc_in_the_environment_does_not_change_the_count(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    for tree in ("src", "tools", "subprojects/docket/src"):
        (tmp_path / tree).mkdir(parents=True)
    (tmp_path / "src" / "first.py").write_text(SHARED, encoding="utf-8")
    (tmp_path / "src" / "second.py").write_text(SHARED, encoding="utf-8")
    rc = tmp_path / "pylintrc"
    rc.write_text("[SIMILARITIES]\nmin-similarity-lines=50\n", encoding="utf-8")
    monkeypatch.setenv("PYLINTRC", str(rc))

    assert dict(pairs(run_pylint(tmp_path))) == {("first", "second"): 1}


def test_a_count_below_the_baseline_asks_for_the_baseline_to_be_lowered() -> None:
    lines = compare({}, {("a", "b"): 1})

    assert lines == [
        "a and b: 0 copied block(s), below the baseline of 1. Lower `ALLOWED_BLOCKS` to 0, "
        "so the count stays a ratchet."
    ]


def test_a_count_at_the_baseline_passes() -> None:
    assert compare({("a", "b"): 1}, {("a", "b"): 1}) == []


def test_output_pylint_cannot_give_as_json_is_an_error_not_a_pass(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("duplicate_code_check.sys.executable", "false")

    with pytest.raises(RuntimeError, match="without JSON output"):
        run_pylint(tmp_path)


def test_the_repository_holds_no_copied_block_beyond_its_baseline(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main([]) == 0
    printed = capsys.readouterr().out

    assert f"against a baseline of {sum(ALLOWED_BLOCKS.values())}, 0 errors" in printed


def test_the_json_pylint_prints_is_what_pairs_reads(tmp_path: Path) -> None:
    """Pin the shape `pairs` reads: pylint's JSON names both modules in the message."""
    for tree in ("src", "tools", "subprojects/docket/src"):
        (tmp_path / tree).mkdir(parents=True)
    (tmp_path / "src" / "first.py").write_text(SHARED, encoding="utf-8")
    (tmp_path / "src" / "second.py").write_text(SHARED, encoding="utf-8")

    messages = run_pylint(tmp_path)

    assert [message["symbol"] for message in messages] == ["duplicate-code"]
    assert "==first:[" in json.dumps(messages) and "==second:[" in json.dumps(messages)
