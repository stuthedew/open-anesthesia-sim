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


#: A stand-in `claude` command that gives the replies in `FAKE_REPLIES` in turn,
#: and records the request each run was given.
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
    """Return the request that `tools/new_prose.py --draft` writes for a README draft of `lines`."""
    draft = tmp_path / "draft.md"
    draft.write_text("\n".join(lines) + "\n", encoding="utf-8")
    text = new_prose.draft_report(draft, "README", new_prose.rule_table())
    assert text is not None
    return request_of(text)


def test_the_second_request_holds_the_edit_numbered_from_the_passage_s_first_row(
    tmp_path: Path,
) -> None:
    """The real draft writer's header and rows are read back, and the edit replaces them."""
    request = draft_request(tmp_path, "First long line.", "Second line.", "Third line.")

    second = copy_edit.second_request(request, {1: ("One line now.",)})

    prose, heading, before = second.partition(copy_edit.RULE_END)[2].partition(
        f"\n{copy_edit.BEFORE}:\n"
    )
    assert prose.startswith(f"\n\n{copy_edit.SECOND_READ}\n")
    assert "[1] draft.md, rows 1-1. Draft: 7 words." in prose
    assert prose.endswith("\n    1 > One line now.\n")
    assert "Third line." not in prose
    assert before.split("\n")[-4:] == ["First long line.", "Second line.", "Third line.", "```"]


def test_rows_after_an_edit_are_renumbered_through_the_listing() -> None:
    """A longer edit renumbers later rows, the next header and the title, but not a new listing."""
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

    prose = second.partition(copy_edit.RULE_END)[2].partition(f"\n{copy_edit.BEFORE}:")[0]
    assert prose.split("\n")[4:] == [
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
        "",
    ]
    assert "Passage 2" not in second.partition(f"\n{copy_edit.BEFORE}:")[2]


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

    prose, _, before = second.partition(f"\n{copy_edit.BEFORE}:\n")
    assert '    """Old' in before
    assert prose.split("\n")[-5:] == [
        "[1] src/a.py, rows 5-5, docstring, 40 words, for: A developer",
        "    4 | def f():",
        '    5 >     """New text."""',
        "    6 |     return 1",
        "",
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
    merged = copy_edit.merge([FIRST, SECOND], 3)

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
        copy_edit.merge([FIRST, "[1] keep\n"], 3)


def test_a_fenced_block_s_fence_is_longer_than_any_fence_inside_it() -> None:
    assert copy_edit.fenced(["a", "  ````", "b"]) == ["`````", "a", "  ````", "b", "`````"]
    assert copy_edit.fenced(["a"]) == ["```", "a", "```"]


@pytest.fixture
def two_reads(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Put the stand-in for `claude` first on PATH, and return the file it records into."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    claude = bin_dir / "claude"
    claude.write_text(TWO_READS_CLAUDE, encoding="utf-8")
    claude.chmod(claude.stat().st_mode | stat.S_IEXEC)
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ['PATH']}")
    monkeypatch.setenv("FAKE_RECORD", str(tmp_path / "asked.json"))
    return tmp_path / "asked.json"


#: A meaning check's reply that finds nothing lost in one passage.
SAME = "[1] same\n\nThe edit says everything the original said.\n"
#: The replies of one round of meaning checks that all find nothing lost.
PANEL_SAME = [SAME] * copy_edit.CHECK_PANEL


def test_audits_run_until_one_changes_nothing_and_the_replies_merge(
    two_reads: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The second read changes the edit, so a third read audits it. The third changes nothing."""
    request = tmp_path / "passages.txt"
    request.write_text(draft_request(tmp_path, "Old one.", "Old two."), encoding="utf-8")
    second = "[1] rewrite\n\n```\nSecond edit.\n```\n\nCut a repeat.\n"
    third = "[1] keep\n\nNo fault found.\n"
    monkeypatch.setenv(
        "FAKE_REPLIES",
        json.dumps([FIRST.partition("**[2]")[0], second, third, *PANEL_SAME, "unused"]),
    )

    reply, counts = copy_edit.run(request, reads=tmp_path / "reads")

    asked = json.loads(two_reads.read_text(encoding="utf-8"))
    assert len(asked) == 3 + copy_edit.CHECK_PANEL
    assert copy_edit.SECOND_READ in asked[1]
    assert "    1 > First edit of one." in asked[1]
    assert "    1 > Second edit." in asked[2]
    assert "Old one." in asked[2].partition(copy_edit.BEFORE)[2]
    assert rejected_prose.rewrites(reply) == {1: ("Second edit.",)}
    assert "Notes from the third read:" in reply
    assert counts == (
        "copy_edit: read 10 tokens, wrote 3, 1 turns, $0.50; "
        "second read: read 10 tokens, wrote 3, 1 turns, $0.50; "
        "third read: read 10 tokens, wrote 3, 1 turns, $0.50; "
        "meaning check 1: read 10 tokens, wrote 3, 1 turns, $0.50; "
        "meaning check 1, reader 2: read 10 tokens, wrote 3, 1 turns, $0.50"
    )
    assert (tmp_path / "reads" / "second-reply.txt").read_text(encoding="utf-8") == second


def test_an_audit_that_returns_the_same_text_ends_the_reads(
    two_reads: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    request = tmp_path / "passages.txt"
    request.write_text(draft_request(tmp_path, "Old one."), encoding="utf-8")
    same = "[1] rewrite\n\n```\nFirst edit of one.\n```\n"
    monkeypatch.setenv("FAKE_REPLIES", json.dumps([same, same, *PANEL_SAME, "unused"]))

    copy_edit.run(request)

    assert len(json.loads(two_reads.read_text(encoding="utf-8"))) == 2 + copy_edit.CHECK_PANEL


def test_a_passage_that_never_settles_stops_at_max_reads(
    two_reads: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    request = tmp_path / "passages.txt"
    request.write_text(draft_request(tmp_path, "Old one."), encoding="utf-8")
    edits = [f"[1] rewrite\n\n```\nEdit {n}.\n```\n" for n in range(1, 7)]
    monkeypatch.setenv("FAKE_REPLIES", json.dumps(edits[: copy_edit.MAX_READS] + PANEL_SAME))

    reply, _ = copy_edit.run(request)

    assert len(json.loads(two_reads.read_text(encoding="utf-8"))) == (
        copy_edit.MAX_READS + copy_edit.CHECK_PANEL
    )
    assert rejected_prose.rewrites(reply) == {1: (f"Edit {copy_edit.MAX_READS}.",)}


def test_an_audit_whose_reply_cannot_be_read_is_left_out_and_the_earlier_reads_kept(
    two_reads: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A reply cut off before its verdicts ends the audits without losing the reads before it."""
    request = tmp_path / "passages.txt"
    request.write_text(draft_request(tmp_path, "Old one."), encoding="utf-8")
    second = "[1] rewrite\n\n```\nSecond edit.\n```\n"
    cut_off = "the end of a reply whose verdicts were lost\n"
    monkeypatch.setenv(
        "FAKE_REPLIES",
        json.dumps(["[1] rewrite\n\n```\nFirst.\n```\n", second, cut_off, *PANEL_SAME, "unused"]),
    )

    reply, counts = copy_edit.run(request)

    assert len(json.loads(two_reads.read_text(encoding="utf-8"))) == 3 + copy_edit.CHECK_PANEL
    assert rejected_prose.rewrites(reply) == {1: ("Second edit.",)}
    assert "Notes from the third read:" not in reply
    assert "third read: reply unreadable, so it was left out ([1] has no verdict)" in counts


def test_a_first_read_that_rewrites_nothing_is_the_whole_reply(
    two_reads: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    request = tmp_path / "passages.txt"
    request.write_text(draft_request(tmp_path, "Fine as it is."), encoding="utf-8")
    monkeypatch.setenv("FAKE_REPLIES", json.dumps(["[1] keep\n\nIt serves its reader."]))

    reply, _ = copy_edit.run(request)

    assert reply == "[1] keep\n\nIt serves its reader."
    assert len(json.loads(two_reads.read_text(encoding="utf-8"))) == 1


def test_the_copy_editor_s_instructions_name_the_second_read_s_opening() -> None:
    """The copy editor's prompt must quote a second read's opening to say what to do with one."""
    opening = copy_edit.SECOND_READ.partition(".")[0]

    assert f'"{opening}."' in copy_edit.PROMPT.read_text(encoding="utf-8")


def test_a_docstring_rewrite_passes_the_code_check() -> None:
    before = ["def f():", '    """Old text."""', "    return 1"]
    after = ["def f():", '    """New text."""', "    return 1"]

    assert copy_edit.check_code("src/a.py", before, before, after) == copy_edit.CodeCheck()


@pytest.mark.parametrize(
    ("before", "after"),
    [
        (["x = 1  # Old note."], ["x = 2  # New note."]),
        (
            ["def f():", '    """Text."""', "    return 1"],
            ["def g():", '    """Text."""', "    return 1"],
        ),
        # An excerpt that starts inside a block does not tokenize, so its code lines are compared.
        (["        x = 1", "    y = 2"], ["        x = 1", "    y = 3"]),
    ],
)
def test_a_rewrite_that_changes_python_code_is_refused(before: list[str], after: list[str]) -> None:
    found = copy_edit.check_code("src/a.py", before, before, after)

    assert found.refused == ("it changed code outside the docstrings, comments and strings",)


@pytest.mark.parametrize(
    ("after", "reason"),
    [
        (["Text.", "", "```", "y = 2", "```"], "it changed, added or removed a fenced block"),
        (["Text, 5 mL.", ""], "it changed, added or removed a fenced block"),
        (["Text.", "", "```", "x = 1", "```", "<!-- marker -->"], "an HTML comment"),
        (["## A heading", "", "```", "x = 1", "```"], "a heading"),
    ],
)
def test_a_markdown_rewrite_that_changes_a_block_comment_or_heading_is_refused(
    after: list[str], reason: str
) -> None:
    before = ["Text.", "", "```", "x = 1", "```"]

    found = copy_edit.check_code("docs/MODEL.md", before, before, after)

    assert any(reason in refused for refused in found.refused)


def test_a_comment_cut_whole_is_listed_and_not_refused() -> None:
    before = ["Two percent.", "<!-- provenance: a.json x = 2 -->", "Three.", "<!-- marker = 3 -->"]
    after = ["Three.", "<!-- marker = 3 -->"]

    found = copy_edit.check_code("docs/MODEL.md", before, before, after)

    assert found.refused == ()
    assert found.cut_comments == ("<!-- provenance: a.json x = 2 -->",)
    altered = ["Three.", "<!-- marker = 4 -->"]
    assert copy_edit.check_code("docs/MODEL.md", before, before, altered).refused == (
        "it changed an HTML comment or wrote a new one",
    )
    copied = [*before, "Three again.", "<!-- marker = 3 -->"]
    assert copy_edit.check_code("docs/MODEL.md", before, before, copied).refused == ()


def test_a_decision_tag_cut_with_its_item_id_is_refused() -> None:
    before = [
        "The dialog locks the window (project owner, 2026-10-18,",
        "ratified, over a modeless notice, `PL-W5WX`). It also holds (`PL-TPBH`).",
    ]
    kept_id = ["The dialog locks the window (`PL-W5WX`). It also holds."]
    lost_id = ["The dialog locks the window. It also holds (`PL-TPBH`)."]

    assert copy_edit.check_code("docs/MODEL.md", before, before, kept_id).refused == ()
    assert copy_edit.check_code("docs/MODEL.md", before, before, lost_id).refused == (
        "it cut the decision that `PL-W5WX` records without naming the item",
    )


def test_a_new_code_name_is_refused_and_a_dropped_one_is_listed() -> None:
    before = ["The check (`check_a`) reads `docs/x.md`."]
    seen = [*before, "The list `check_b` reads."]

    renamed = copy_edit.check_code("docs/MODEL.md", before, seen, ["The check reads `docs/y.md`."])
    borrowed = copy_edit.check_code("docs/MODEL.md", before, seen, ["The check (`check_b`) reads."])

    assert renamed.refused == ("it wrote code names the passage does not hold: `docs/y.md`",)
    assert renamed.dropped == ("check_a", "docs/x.md")
    assert borrowed.refused == ()


def test_a_merge_turns_a_rewrite_that_changed_code_into_keep_with_the_reason(
    tmp_path: Path,
) -> None:
    request = request_of(
        "[1] src/a.py, rows 1-1, comment, 4 words, for: A developer",
        new_prose.row_line(1, ">", "x = 1  # Old note."),
    )
    first = "[1] rewrite\n\n```\nx = 2  # New note.\n```\n"

    reply = copy_edit.merge([first, "[1] keep"], 1, copy_edit.code_report(request))

    assert reply.startswith("[1] keep\n")
    assert (
        "- Passage 1: the rewrite was refused, because it changed code outside the "
        "docstrings, comments and strings."
    ) in reply


#: A document longer than one chapter when the limit is 40 words.
DOCUMENT = (
    "# Model\n\n## One\n\n"
    + " ".join(["first"] * 30)
    + "\n\n## Two\n\n"
    + " ".join(["second"] * 30)
    + "\n"
)


@pytest.fixture
def document(tmp_path: Path) -> Path:
    """A root holding `DOCUMENT` as `docs/MODEL.md` and a `docket.toml` with a models table."""
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "MODEL.md").write_text(DOCUMENT, encoding="utf-8")
    (tmp_path / "docket.toml").write_text(
        '[models]\ndefault = { model = "claude-opus-5-5", effort = "high" }\n', encoding="utf-8"
    )
    return tmp_path


def test_a_short_document_s_structure_read_is_one_read(
    two_reads: Path, document: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FAKE_REPLIES", json.dumps(["[1] keep\n\nStructure: no change."]))

    reply, _ = copy_edit.structure("docs/MODEL.md", root=document)

    asked = json.loads(two_reads.read_text(encoding="utf-8"))
    assert len(asked) == 1
    assert new_prose.STRUCTURE_READ in asked[0]
    assert reply == "[1] keep\n\nStructure: no change."


def test_a_long_document_is_read_a_chapter_at_a_time_then_as_one_outline(
    two_reads: Path, document: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(new_prose, "REQUEST_LIMIT_WORDS", 40)
    chapter = "[1] keep\n\nStructure: no change.\n\nOutline:\n- rows {}: the {} point."
    monkeypatch.setenv(
        "FAKE_REPLIES",
        json.dumps([chapter.format(5, "first"), chapter.format(9, "second"), "[1] keep\n\nFine."]),
    )

    reply, counts = copy_edit.structure("docs/MODEL.md", root=document)

    asked = json.loads(two_reads.read_text(encoding="utf-8"))
    assert [request.count(new_prose.CHAPTER_READ) for request in asked] == [1, 1, 0]
    assert new_prose.OUTLINE_READ in asked[2]
    assert "  - rows 9: the second point." in asked[2]
    assert reply.startswith("Structure read of docs/MODEL.md in 2 chapters.")
    assert 'Chapter 2 of 2: docs/MODEL.md § "Two", rows 7-9' in reply
    assert reply.endswith("The whole document:\n\nPassage 1 keep\n\nFine.")
    assert counts.count("read 10 tokens") == 3


def test_a_chapter_read_without_an_outline_is_refused(
    two_reads: Path, document: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(new_prose, "REQUEST_LIMIT_WORDS", 40)
    monkeypatch.setenv("FAKE_REPLIES", json.dumps(["[1] keep\n\nFine."] * 2))

    with pytest.raises(copy_edit.Refused, match='§ "One", rows 1-5 gave no outline'):
        copy_edit.structure("docs/MODEL.md", root=document)


def test_a_structure_read_that_rewrites_rows_is_refused(
    two_reads: Path, document: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FAKE_REPLIES", json.dumps(["[1] rewrite\n\n```\nNew.\n```\n"]))

    with pytest.raises(copy_edit.Refused, match="rewrote rows"):
        copy_edit.structure("docs/MODEL.md", root=document)


def test_each_section_is_line_edited_alone_under_a_line_that_names_it(
    two_reads: Path, document: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FAKE_REPLIES", json.dumps(["[1] keep\n\nFine."] * 2))

    reply, _ = copy_edit.sections("docs/MODEL.md", root=document)

    asked = json.loads(two_reads.read_text(encoding="utf-8"))
    assert len(asked) == 2
    assert "first first" in asked[0] and "second" not in asked[0].partition("[1]")[2]
    assert reply == (
        'Section 1 of 2: docs/MODEL.md § "One", rows 3-5\n\n[1] keep\n\nFine.\n\n'
        'Section 2 of 2: docs/MODEL.md § "Two", rows 7-9\n\n[1] keep\n\nFine.'
    )


def test_the_copy_editor_s_instructions_name_each_structure_read_s_opening() -> None:
    text = copy_edit.PROMPT.read_text(encoding="utf-8")

    for opening in (new_prose.STRUCTURE_READ, new_prose.CHAPTER_READ, new_prose.OUTLINE_READ):
        assert f'"{opening.partition(".")[0]}."' in text


#: A meaning check's reply that finds one statement lost in passage 1.
LOST_ONE = """[1] lost

- OLD: "Old one must hold."
- NEW: "First edit of one."
- KIND: 1. A requirement's force
- WHY: The requirement became a description.
"""


def test_a_statement_the_meaning_check_finds_lost_is_restored_and_checked_again(
    two_reads: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The check sees the edit and the original. The restore read sees what the check found."""
    request = tmp_path / "passages.txt"
    request.write_text(draft_request(tmp_path, "Old one must hold."), encoding="utf-8")
    first = "[1] rewrite\n\n```\nFirst edit of one.\n```\n"
    restored = "[1] rewrite\n\n```\nOne must hold.\n```\n\nPut back the requirement.\n"
    round_one = [LOST_ONE, *PANEL_SAME[1:]]
    monkeypatch.setenv(
        "FAKE_REPLIES",
        json.dumps([first, "[1] keep\n", *round_one, restored, *PANEL_SAME, "unused"]),
    )

    reply, counts = copy_edit.run(request, reads=tmp_path / "reads")

    asked = json.loads(two_reads.read_text(encoding="utf-8"))
    restore = 2 + copy_edit.CHECK_PANEL
    assert len(asked) == restore + 1 + copy_edit.CHECK_PANEL
    assert copy_edit.MEANING_CHECK in asked[2]
    assert "    1 > First edit of one." in asked[2]
    assert "Old one must hold." in asked[2].partition(copy_edit.BEFORE)[2]
    assert asked[3] == asked[2]
    assert copy_edit.RESTORE_READ in asked[restore]
    assert "The requirement became a description." in asked[restore].partition(copy_edit.LOST)[2]
    assert "    1 > One must hold." in asked[restore + 1]
    assert rejected_prose.rewrites(reply) == {1: ("One must hold.",)}
    assert "Notes from the restore 1 read:" in reply
    assert "Notes from meaning check 1, reader 2:" in reply
    assert "Notes from meaning check 2:" in reply
    assert "Meaning check:" not in reply
    assert "restore 1 read: read 10 tokens" in counts
    assert (tmp_path / "reads" / "meaning-1-reply.txt").read_text(encoding="utf-8") == LOST_ONE
    assert (tmp_path / "reads" / "meaning-1-2-reply.txt").read_text(encoding="utf-8") == SAME


def test_a_statement_that_only_the_second_check_finds_lost_is_restored(
    two_reads: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Runs of one check on one edit find different losses, so each round pools their findings."""
    request = tmp_path / "passages.txt"
    request.write_text(draft_request(tmp_path, "Old one must hold."), encoding="utf-8")
    first = "[1] rewrite\n\n```\nFirst edit of one.\n```\n"
    restored = "[1] rewrite\n\n```\nOne must hold.\n```\n"
    round_one = [*PANEL_SAME[1:], LOST_ONE]
    monkeypatch.setenv(
        "FAKE_REPLIES",
        json.dumps([first, "[1] keep\n", *round_one, restored, *PANEL_SAME, "unused"]),
    )

    reply, _ = copy_edit.run(request)

    asked = json.loads(two_reads.read_text(encoding="utf-8"))
    restore = 2 + copy_edit.CHECK_PANEL
    assert copy_edit.RESTORE_READ in asked[restore]
    assert "The requirement became a description." in asked[restore].partition(copy_edit.LOST)[2]
    assert rejected_prose.rewrites(reply) == {1: ("One must hold.",)}


def test_a_passage_that_still_loses_a_statement_after_the_last_round_is_kept_as_it_was(
    two_reads: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    request = tmp_path / "passages.txt"
    request.write_text(draft_request(tmp_path, "Old one must hold."), encoding="utf-8")
    first = "[1] rewrite\n\n```\nFirst edit of one.\n```\n"
    replies = [first, "[1] keep\n"]
    for _ in range(copy_edit.MAX_CHECK_ROUNDS - 1):
        replies += [LOST_ONE] * copy_edit.CHECK_PANEL + [first]
    replies += [LOST_ONE] * copy_edit.CHECK_PANEL
    monkeypatch.setenv("FAKE_REPLIES", json.dumps([*replies, "unused"]))

    reply, _ = copy_edit.run(request)

    assert len(json.loads(two_reads.read_text(encoding="utf-8"))) == len(replies)
    assert reply.startswith("[1] keep\n")
    assert rejected_prose.rewrites(reply) == {}
    refused = reply.partition("Meaning check:")[2].partition("Notes from")[0]
    assert "Passage 1: the rewrite was refused" in refused
    assert "The requirement became a description." in refused


def test_a_meaning_check_whose_reply_cannot_be_read_keeps_every_edited_passage_as_it_was(
    two_reads: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Nothing then shows that the edit kept the original's meaning."""
    request = tmp_path / "passages.txt"
    request.write_text(draft_request(tmp_path, "Old one."), encoding="utf-8")
    first = "[1] rewrite\n\n```\nFirst.\n```\n"
    monkeypatch.setenv("FAKE_REPLIES", json.dumps([first, "[1] keep\n", "cut off", "unused"]))

    reply, counts = copy_edit.run(request)

    assert reply.startswith("[1] keep\n")
    assert "The reply of meaning check 1 could not be read" in reply
    assert "meaning check 1: reply unreadable" in counts


def test_the_meaning_check_s_findings_are_read_by_passage() -> None:
    reply = '[1] same\n\nAll kept.\n\n**[2]** lost\n\n- OLD: "x"\n- WHY: gone.\n\n[3] same\n'

    assert copy_edit.meaning_findings(reply, 3) == {2: '- OLD: "x"\n- WHY: gone.'}


@pytest.mark.parametrize(
    ("reply", "problem"),
    [
        ("[1] same\n", r"\[2\] has no verdicts"),
        ("[1] same\n[1] lost\n[2] same\n", r"\[1\] has 2 verdicts"),
        ("[1] same\n[2] same\n[3] lost\n", r"\[3\] was not shown"),
    ],
)
def test_a_meaning_check_reply_without_one_verdict_per_passage_is_refused(
    reply: str, problem: str
) -> None:
    with pytest.raises(ValueError, match=problem):
        copy_edit.meaning_findings(reply, 2)


def test_the_meaning_check_holds_an_edit_to_the_copy_editor_s_own_list(fake: Path) -> None:
    """One list, kept in the copy editor's instructions, is given to both."""
    check = copy_edit.checker()
    listed = copy_edit.never_loses(
        copy_edit.instructions(copy_edit.PROMPT.read_text(encoding="utf-8"))
    )

    assert listed.startswith(copy_edit.NEVER_LOSES)
    assert "A requirement's force" in listed and "A stated reason" in listed
    assert check.prompt.rstrip().endswith(listed)
    assert check.prompt.startswith(
        copy_edit.instructions(copy_edit.CHECK_PROMPT.read_text(encoding="utf-8")).rstrip()
    )
    table = copy_edit.load_config(copy_edit.ROOT).models
    assert table is not None
    chosen = table.choose({"role": copy_edit.CHECK_ROLE})
    assert (check.model, check.effort) == (chosen.model, chosen.effort)


def test_instructions_without_the_list_are_refused() -> None:
    with pytest.raises(copy_edit.Refused, match="What an edit never loses"):
        copy_edit.never_loses("## How to edit\n\nTake these steps.\n")


def test_the_instructions_name_the_meaning_check_s_and_the_restore_read_s_layout() -> None:
    """Each prompt must quote the headings its request uses, to say what to do with them."""
    editor_text = copy_edit.PROMPT.read_text(encoding="utf-8")
    check_text = copy_edit.CHECK_PROMPT.read_text(encoding="utf-8")

    assert f'"{copy_edit.RESTORE_READ.partition(".")[0]}."' in editor_text
    assert f'"{copy_edit.LOST}"' in editor_text
    assert f'"{copy_edit.BEFORE}"' in check_text
