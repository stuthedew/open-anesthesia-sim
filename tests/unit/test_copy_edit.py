"""Tests for `tools/copy_edit.py`, which runs the copy editor as its own `claude -p` process."""

from __future__ import annotations

import json
import os
import stat
from pathlib import Path

import copy_edit
import new_prose
import pytest
import rejected_prose

#: A stand-in for `claude` that records its arguments, its directory and what
#: that directory holds, then prints a reply in `claude -p`'s JSON form.
FAKE_CLAUDE = """\
#!/usr/bin/env python3
import json, os, sys
record = {"argv": sys.argv[1:], "cwd": os.getcwd(), "files": sorted(os.listdir("."))}
record["memory_off"] = os.environ.get("CLAUDE_CODE_DISABLE_AUTO_MEMORY")
record["prompt"] = open(sys.argv[sys.argv.index("--system-prompt-file") + 1]).read()
json.dump(record, open(os.environ["FAKE_RECORD"], "w"))
print(json.dumps({"result": "[1] keep", "is_error": False, "num_turns": 2,
                  "total_cost_usd": 0.1, "usage": {"input_tokens": 5,
                  "cache_creation_input_tokens": 100, "output_tokens": 7}}))
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


def test_the_copy_editor_runs_alone_with_its_instructions_and_only_read(
    fake: Path, tmp_path: Path
) -> None:
    """No resident instruction can load: the directory holds the request and nothing else."""
    request = tmp_path / "passages.txt"
    request.write_text("[1] some passage\n", encoding="utf-8")

    reply, counts = copy_edit.run(request)

    seen = json.loads(fake.read_text(encoding="utf-8"))
    assert reply == "[1] keep"
    assert counts == "copy_edit: read 105 tokens, wrote 7, 2 turns, $0.10"
    assert seen["files"] == [copy_edit.REQUEST_NAME]
    assert seen["cwd"] != str(copy_edit.ROOT)
    assert seen["argv"][seen["argv"].index("--tools") + 1] == "Read"
    assert seen["argv"][seen["argv"].index("--setting-sources") + 1] == ""
    assert seen["memory_off"] == "1"
    body = copy_edit.PROMPT.read_text(encoding="utf-8").split("\n---\n", 1)[1].lstrip("\n")
    assert seen["prompt"] == body
    assert "omitClaudeMd" not in seen["prompt"]


def test_the_model_is_the_one_the_models_table_chooses_for_the_copy_editor(
    fake: Path, tmp_path: Path
) -> None:
    """The run never falls to the account's default model."""
    request = tmp_path / "passages.txt"
    request.write_text("[1] some passage\n", encoding="utf-8")
    table = copy_edit.load_config(copy_edit.ROOT).models
    assert table is not None
    chosen = table.choose({"role": copy_edit.ROLE})

    copy_edit.run(request)

    argv = json.loads(fake.read_text(encoding="utf-8"))["argv"]
    assert argv[argv.index("--model") + 1] == chosen.model
    assert argv[argv.index("--effort") + 1] == chosen.effort


def test_an_error_result_is_refused_rather_than_printed_as_a_reply() -> None:
    output = json.dumps({"result": "Credit balance is too low", "is_error": True})

    with pytest.raises(copy_edit.Refused, match="Credit balance is too low"):
        copy_edit.reply_of(output)


def test_main_exits_1_with_the_reason_when_claude_is_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("PATH", str(tmp_path))
    request = tmp_path / "passages.txt"
    request.write_text("[1] some passage\n", encoding="utf-8")

    assert copy_edit.main([str(request)]) == 1
    assert "copy_edit: no reply: no `claude` on PATH" in capsys.readouterr().err


#: A stand-in for `claude` that gives the replies in `FAKE_REPLIES` in turn, and
#: records the request each run was given.
TWO_READS_CLAUDE = """\
#!/usr/bin/env python3
import json, os
record = os.environ["FAKE_RECORD"]
asked = json.load(open(record)) if os.path.exists(record) else []
asked.append(open("request.txt").read())
json.dump(asked, open(record, "w"))
reply = json.loads(os.environ["FAKE_REPLIES"])[len(asked) - 1]
print(json.dumps({"result": reply, "is_error": False, "num_turns": 1,
                  "total_cost_usd": 0.5, "usage": {"input_tokens": 10, "output_tokens": 3}}))
"""


def request_of(*prose: str) -> str:
    """A request whose writing rule is one line, followed by the lines `prose`."""
    return "\n".join(["Write plainly.", "", copy_edit.RULE_END, "", *prose])


def draft_request(tmp_path: Path, *lines: str) -> str:
    """The request `tools/new_prose.py --draft` writes for a reply made of `lines`."""
    draft = tmp_path / "draft.md"
    draft.write_text("\n".join(lines) + "\n", encoding="utf-8")
    text = new_prose.draft_report(draft, "Replies", new_prose.rule_table())
    assert text is not None
    return request_of(text)


def test_the_second_request_holds_the_edit_numbered_from_the_passage_s_first_row(
    tmp_path: Path,
) -> None:
    """The real draft writer's header and rows are read back, and the edit replaces them."""
    request = draft_request(tmp_path, "First long line.", "Second line.", "Third line.")

    second = copy_edit.second_request(request, {1: ("One line now.",)})

    prose = second.partition(copy_edit.RULE_END)[2]
    assert prose.startswith(f"\n\n{copy_edit.SECOND_READ}\n")
    assert "[1] draft.md, rows 1-1. Draft: 7 words." in prose
    assert prose.endswith("\n    1 > One line now.")
    assert "Third line." not in prose


def test_rows_after_an_edit_are_renumbered_through_the_listing() -> None:
    """A longer edit moves the later rows, the next header and the title; a new listing does not."""
    request = request_of(
        'doc.md § "Part", rows 10-15:',
        "[1] doc.md, rows 10-11. Changed text: 40 words now. For: A reader",
        new_prose.row_line(10, ">", "Old one."),
        new_prose.row_line(11, ">", "Old two."),
        new_prose.row_line(12, "|", ""),
        "[2] doc.md, rows 13-15. Changed text: 50 words now. For: A reader",
        new_prose.row_line(13, ">", "Kept a."),
        new_prose.row_line(14, ">", "Kept b."),
        new_prose.row_line(15, ">", "Kept c."),
        "",
        "other.md, rows 3-4:",
        new_prose.row_line(3, "|", "Elsewhere."),
        new_prose.row_line(4, "|", "Still elsewhere."),
    )

    second = copy_edit.second_request(request, {1: ("New one.", "New two.", "New three.")})

    assert second.partition(copy_edit.RULE_END)[2].split("\n")[4:] == [
        'doc.md § "Part", rows 10-16:',
        "[1] doc.md, rows 10-12. Changed text: 40 words now. For: A reader",
        "   10 > New one.",
        "   11 > New two.",
        "   12 > New three.",
        "   13 | ",
        "[2] doc.md, rows 14-16. Changed text: 50 words now. For: A reader",
        "   14 > Kept a.",
        "   15 > Kept b.",
        "   16 > Kept c.",
        "",
        "other.md, rows 3-4:",
        "    3 | Elsewhere.",
        "    4 | Still elsewhere.",
    ]


def test_an_excerpt_s_code_rows_on_each_side_stay_and_shift() -> None:
    """A unit from the rejected set shows `|` code rows before and after its `>` rows."""
    request = request_of(
        "",
        "[1] src/a.py, rows 5-6, docstring, 40 words, for: A developer",
        new_prose.row_line(4, "|", "def f():"),
        new_prose.row_line(5, ">", '    """Old'),
        new_prose.row_line(6, ">", '    text."""'),
        new_prose.row_line(7, "|", "    return 1"),
    )

    second = copy_edit.second_request(request, {1: ('    """New text."""',)})

    assert second.split("\n")[-4:] == [
        "[1] src/a.py, rows 5-5, docstring, 40 words, for: A developer",
        "    4 | def f():",
        '    5 >     """New text."""',
        "    6 |     return 1",
    ]


def test_a_second_request_is_refused_where_an_edited_passage_has_no_rows_to_replace() -> None:
    request = request_of("[1] doc.md, rows 1-1. Draft: 2 words. For: A reader")

    with pytest.raises(copy_edit.Refused, match=r"passages \[1\] have no rows marked >"):
        copy_edit.second_request(request, {1: ("New.",)})


def test_a_request_without_the_writing_rule_s_last_line_is_refused() -> None:
    with pytest.raises(copy_edit.Refused, match="has no line"):
        copy_edit.passage_count("[1] doc.md, rows 1-1. Draft: 2 words.")


def test_the_passages_must_be_numbered_from_one_in_order() -> None:
    request = request_of(
        "[1] doc.md, rows 1-1. Draft: 2 words.", "[3] doc.md, rows 2-2. Draft: 2 words."
    )

    with pytest.raises(copy_edit.Refused, match=r"numbers its passages \[1, 3\]"):
        copy_edit.passage_count(request)


FIRST = """\
[1] rewrite

```
First edit of one.
```

Cut "really": the reader can do without it.

**[2] keep**

It serves its reader.

[3] keep
"""

SECOND = """\
[1] keep

The first edit reads well.

[2] rewrite

````
Second edit of two, with a fence:
```
code
```
````

Query: the reader needs the unit, and [2] does not give it.

[3] keep
"""


def test_each_passage_takes_the_second_read_s_text_then_the_first_s_then_keep() -> None:
    merged = copy_edit.merge(FIRST, SECOND, 3)

    assert rejected_prose.verdicts(merged, 3) == ["rewrite", "rewrite", "keep"]
    assert rejected_prose.rewrites(merged) == {
        1: ("First edit of one.",),
        2: ("Second edit of two, with a fence:", "```", "code", "```"),
    }
    notes = merged.partition("Notes from the first read:")[2]
    assert 'Cut "really"' in notes
    assert "Query: the reader needs the unit, and Passage 2 does not give it." in notes
    assert "First edit of one." not in notes
    assert "[" not in notes


def test_a_merge_is_refused_where_the_second_read_gives_a_passage_no_verdict() -> None:
    with pytest.raises(copy_edit.Refused, match=r"second read's reply cannot be read: \[2\]"):
        copy_edit.merge(FIRST, "[1] keep\n", 3)


def test_a_fenced_block_s_fence_is_longer_than_any_fence_inside_it() -> None:
    assert copy_edit.fenced(["a", "  ````", "b"]) == ["`````", "a", "  ````", "b", "`````"]
    assert copy_edit.fenced(["a"]) == ["```", "a", "```"]


@pytest.fixture
def two_reads(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Put the two-reads stand-in first on PATH, and return the file it records into."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    claude = bin_dir / "claude"
    claude.write_text(TWO_READS_CLAUDE, encoding="utf-8")
    claude.chmod(claude.stat().st_mode | stat.S_IEXEC)
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ['PATH']}")
    monkeypatch.setenv("FAKE_RECORD", str(tmp_path / "asked.json"))
    return tmp_path / "asked.json"


def test_a_rewrite_is_read_a_second_time_and_the_replies_merged(
    two_reads: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    request = tmp_path / "passages.txt"
    request.write_text(draft_request(tmp_path, "Old one.", "Old two."), encoding="utf-8")
    second = "[1] rewrite\n\n```\nSecond edit.\n```\n\nCut a repeat.\n"
    monkeypatch.setenv("FAKE_REPLIES", json.dumps([FIRST.partition("**[2]")[0], second]))

    reply, counts = copy_edit.run(request, reads=tmp_path / "reads")

    asked = json.loads(two_reads.read_text(encoding="utf-8"))
    assert len(asked) == 2
    assert copy_edit.SECOND_READ in asked[1]
    assert "    1 > First edit of one." in asked[1]
    assert rejected_prose.rewrites(reply) == {1: ("Second edit.",)}
    assert counts == (
        "copy_edit: read 10 tokens, wrote 3, 1 turns, $0.50; "
        "second read: read 10 tokens, wrote 3, 1 turns, $0.50"
    )
    assert (tmp_path / "reads" / "second-reply.txt").read_text(encoding="utf-8") == second


def test_a_first_read_that_rewrites_nothing_is_the_whole_reply(
    two_reads: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    request = tmp_path / "passages.txt"
    request.write_text(draft_request(tmp_path, "Fine as it is."), encoding="utf-8")
    monkeypatch.setenv("FAKE_REPLIES", json.dumps(["[1] keep\n\nIt serves its reader."]))

    reply, _ = copy_edit.run(request)

    assert reply == "[1] keep\n\nIt serves its reader."
    assert len(json.loads(two_reads.read_text(encoding="utf-8"))) == 1
