"""Tests for `tools/prose_judge.py`, which judges the copy editor's edits blind with `claude -p`."""

from __future__ import annotations

import json
import os
import stat
from pathlib import Path

import copy_edit
import new_prose
import prose_judge
import pytest

#: A stand-in for `claude` that records its arguments, its directory and what
#: that directory holds, then prints `FAKE_RESULT` in `claude -p`'s JSON form.
FAKE_CLAUDE = """\
#!/usr/bin/env python3
import json, os, sys
record = {"argv": sys.argv[1:], "files": sorted(os.listdir(".")),
          "request": open("request.txt").read()}
record["prompt"] = open(sys.argv[sys.argv.index("--system-prompt-file") + 1]).read()
json.dump(record, open(os.environ["FAKE_RECORD"], "w"))
print(json.dumps({"result": os.environ["FAKE_RESULT"], "is_error": False, "num_turns": 1,
                  "total_cost_usd": 0.2, "usage": {"input_tokens": 9, "output_tokens": 4}}))
"""

README = """\
# A simulator

## How it runs

It runs in a window.
It has two plots.

## What comes next

More.
"""

REWRITE = """\
[1] rewrite

```
## How it runs

It runs in a window with two plots.
```

- Merged two short sentences.
"""


@pytest.fixture
def fake(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Put the stand-in `claude` first on PATH, and return the file it records into."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    claude = bin_dir / "claude"
    claude.write_text(FAKE_CLAUDE, encoding="utf-8")
    claude.chmod(claude.stat().st_mode | stat.S_IEXEC)
    record = tmp_path / "record.json"
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ['PATH']}")
    monkeypatch.setenv("FAKE_RECORD", str(record))
    return record


def section_request(tmp_path: Path) -> str:
    """The request that `tools/new_prose.py --section` writes for README's "How it runs"."""
    (tmp_path / "README.md").write_text(README, encoding="utf-8")
    text = new_prose.section_report(tmp_path, "README.md", "How it runs", new_prose.rule_table())
    return "\n".join(["Write plainly.", "", new_prose.RULE_END, "", text])


def pair(name: str, original: str, edited: str) -> prose_judge.Pair:
    return prose_judge.Pair(
        name=name, where="README.md", readers="", original=original, edited=edited
    )


def test_a_rewritten_passage_becomes_one_pair_with_its_readers(tmp_path: Path) -> None:
    """The real section writer's rows and readers are read back, beside the reply's text."""
    (found,) = prose_judge.pairs_of("s1", section_request(tmp_path), REWRITE)

    assert found.name == "s1 [1]"
    assert found.where == 'README.md § "How it runs"'
    assert found.readers.startswith(new_prose.readers_heading("README.md"))
    assert "Does not know:" in found.readers
    assert "It runs in a window.\nIt has two plots." in found.original
    assert "What comes next" not in found.original
    assert found.edited == "## How it runs\n\nIt runs in a window with two plots."


def test_a_passage_the_reply_keeps_makes_no_pair(tmp_path: Path) -> None:
    assert prose_judge.pairs_of("s1", section_request(tmp_path), "[1] keep\n\nIt is fine.") == []


def test_a_reply_that_rewrites_a_passage_the_request_lacks_is_refused(tmp_path: Path) -> None:
    with pytest.raises(copy_edit.Refused, match=r"passages \[2\]"):
        prose_judge.pairs_of("s1", section_request(tmp_path), REWRITE.replace("[1]", "[2]"))


def test_the_key_says_which_version_holds_the_edit_and_the_order_repeats_by_seed() -> None:
    pairs = [pair(f"p{n}", f"Old text {n}.", f"New text {n}.") for n in range(1, 9)]

    text, key = prose_judge.blind(pairs, seed=7)

    for entry, (number, sections) in zip(
        key, enumerate(text.split("## Pair ")[1:], 1), strict=True
    ):
        version_a = sections.partition("### Version A")[2].partition("### Version B")[0]
        edited_in_a = f"New text {number}." in version_a
        assert entry["edit"] == ("A" if edited_in_a else "B")
        assert entry["words"] == [3, 3]
    assert {entry["edit"] for entry in key} == {"A", "B"}
    assert prose_judge.blind(pairs, seed=7) == (text, key)
    assert prose_judge.blind(pairs, seed=8)[1] != key


def test_neither_version_is_named_as_the_original_in_the_judge_s_request() -> None:
    text, _ = prose_judge.blind([pair("p1", "Old.", "New.")])

    assert "original" not in text.lower()
    assert "edit" not in text.lower()


def test_each_pair_takes_its_first_verdict_whatever_its_marks() -> None:
    reply = "**[1] verdict: B**\nWhy.\n[2] Verdict: same\n[1] verdict: A\n`[3] verdict: a`"

    assert prose_judge.verdicts(reply) == {1: "B", 2: "same", 3: "a"}


def test_a_verdict_is_read_against_the_key() -> None:
    assert prose_judge.won("A", "A") == "edit"
    assert prose_judge.won("A", "b") == "original"
    assert prose_judge.won("B", "same") == "same"
    assert prose_judge.won("B", None) == "?"


def test_main_runs_the_judge_alone_and_writes_the_key_and_result(
    fake: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The judge sees only its request, with its own instructions, and the result unblinds it."""
    request, reply, out = tmp_path / "s1" / "request.txt", tmp_path / "reply.txt", tmp_path / "out"
    request.parent.mkdir()
    request.write_text(section_request(tmp_path), encoding="utf-8")
    reply.write_text(REWRITE, encoding="utf-8")
    monkeypatch.setenv("FAKE_RESULT", "[1] verdict: A\n\nA is plainer.")

    assert prose_judge.main([str(out), str(request), str(reply)]) == 0

    seen = json.loads(fake.read_text(encoding="utf-8"))
    assert seen["files"] == [copy_edit.REQUEST_NAME]
    assert seen["argv"][seen["argv"].index("--tools") + 1] == "Read"
    body = prose_judge.JUDGE_PROMPT.read_text(encoding="utf-8").split("\n---\n", 1)[1].lstrip("\n")
    assert seen["prompt"] == body
    (entry,) = json.loads((out / "key.json").read_text(encoding="utf-8"))
    (result,) = json.loads((out / "result.json").read_text(encoding="utf-8"))
    assert result["won"] == ("edit" if entry["edit"] == "A" else "original")
    assert (out / "request.txt").read_text(encoding="utf-8") == seen["request"]
    assert f"s1 [1]: {result['won']}" in capsys.readouterr().out


def test_main_exits_1_where_the_judge_leaves_a_pair_without_a_verdict(
    fake: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    request, reply = tmp_path / "request.txt", tmp_path / "reply.txt"
    request.write_text(section_request(tmp_path), encoding="utf-8")
    reply.write_text(REWRITE, encoding="utf-8")
    monkeypatch.setenv("FAKE_RESULT", "Both read well.")

    assert prose_judge.main([str(tmp_path / "out"), str(request), str(reply)]) == 1
    assert "pairs 1 have no verdict" in capsys.readouterr().err


def test_main_exits_1_where_no_reply_rewrote_a_passage(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    request, reply = tmp_path / "request.txt", tmp_path / "reply.txt"
    request.write_text(section_request(tmp_path), encoding="utf-8")
    reply.write_text("[1] keep\n\nIt is fine.", encoding="utf-8")

    assert prose_judge.main([str(tmp_path / "out"), str(request), str(reply)]) == 1
    assert "nothing to judge" in capsys.readouterr().err
