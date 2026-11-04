"""`tools/rejected_prose.py` must refuse a prompt change that no run of the test set has tested.

The prompt is the copy-editing agent's instructions, `.claude/agents/copy-editor.md`.
The test set holds paragraphs that the project owner rejected after a review
passed them (`PL-FYGJ`), and paragraphs the owner named gold standards, which
a review must keep (`PL-556C`). These tests pin what an entry must hold, how
the agent's verdicts and rewrites are read, and when `check` refuses: no run
for the current prompt and reader rows, a run that kept a rejected entry or
flagged a gold-standard one, a gold-standard entry that no run read or that
repeats another entry's text, and a kind of failure above its cap.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import new_prose
import pytest
from new_prose import MIN_WORDS, reader_table
from rejected_prose import (
    CAP_PER_KIND,
    FAILURE_KINDS,
    GOLD_DIR,
    GOLD_KIND,
    REJECTED_DIR,
    ROOT,
    RUNS_DIR,
    check,
    digest,
    expected_verdict,
    main,
    parse_entry,
    read_set,
    readers_digest,
    record,
    rewrites,
    show,
    verdicts,
)

READERS = """\
| Kind of text | Reader | What they know | What they do not know | What they will do with it |
| --- | --- | --- | --- | --- |
| `docs/MODEL.md` | A clinician | Anesthesia. | E-notation. | Trust a value. |
| Code in `src/` | A developer | Python. | Our history. | Change the code. |
"""
TABLE = reader_table(READERS)
PROMPT = "Review the prose below.\n"
PARAGRAPH = " ".join(["word"] * MIN_WORDS)
#: A paragraph the owner named a gold standard, which differs from every rejected one.
KEPT = " ".join(["plain"] * MIN_WORDS)


def _words(count: int) -> str:
    return " ".join(["word"] * count)


def _reply(*verdicts: str, words: int = MIN_WORDS) -> str:
    """A reply giving unit N the Nth verdict, and a rewrite of `words` words after each rewrite."""
    out = []
    for number, verdict in enumerate(verdicts, start=1):
        out.append(f"[{number}] {verdict}")
        if verdict == "rewrite":
            out += ["```", _words(words), "```"]
    return "\n".join(out) + "\n"


def _entry(
    *,
    kind: str = "jargon",
    path: str = "docs/MODEL.md",
    rejected: str = "2026-11-02",
    paragraph: str = PARAGRAPH,
    sections: str = "",
) -> str:
    """An entry's text, with every required section unless `sections` replaces the last two."""
    tail = sections or (
        '## The owner\'s words\n\n"Unintelligible" (2026-11-02).\n\n'
        "## Where it came from\n\nA test.\n"
    )
    return (
        f"---\nkind: {kind}\nfile: {path}\nrejected: {rejected}\n---\n\n"
        f"## Paragraph\n\n```text\n{paragraph}\n```\n\n{tail}"
    )


def _gold(*, named: str = "2026-11-05", paragraph: str = KEPT) -> str:
    """A gold-standard entry's text, with every required section."""
    return (
        f"---\nfile: docs/MODEL.md\nnamed: {named}\n---\n\n"
        f"## Paragraph\n\n```text\n{paragraph}\n```\n\n"
        '## The owner\'s words\n\n"Good" (2026-11-05).\n\n## Where it came from\n\nA test.\n'
    )


def _root(tmp_path: Path, entries: dict[str, str], gold: dict[str, str] | None = None) -> Path:
    """A tree holding `entries` in the rejected folder and `gold` in the gold-standard one."""
    for directory, files in ((REJECTED_DIR, entries), (GOLD_DIR, gold or {})):
        folder = tmp_path / directory.relative_to(ROOT)
        folder.mkdir(parents=True)
        for name, text in files.items():
            (folder / name).write_text(text, encoding="utf-8")
    return tmp_path


def _in_order(root: Path, by_name: dict[str, str]) -> list[str]:
    """The verdict `by_name` gives each entry, in the order `show` numbers the entries."""
    entries, problems = read_set(root, TABLE)
    assert problems == []
    return [by_name[entry.name] for entry in entries]


def _run(root: Path, name: str, reply: str, *, prompt: str = PROMPT) -> None:
    """Record `reply` as the run `name`, against the entries `root` holds now."""
    entries, problems = read_set(root, TABLE)
    assert problems == []
    folder = root / RUNS_DIR.relative_to(ROOT)
    folder.mkdir(parents=True, exist_ok=True)
    data = record(prompt, entries, TABLE, reply, datetime(2026, 11, 3, tzinfo=UTC))
    (folder / name).write_text(json.dumps(data), encoding="utf-8")


def test_an_entry_records_its_kind_file_date_and_paragraph() -> None:
    entry = parse_entry("jargon-2026-11-02-a.md", _entry(paragraph="  " + PARAGRAPH), TABLE)

    assert (entry.kind, entry.file, entry.judged.isoformat()) == (
        "jargon",
        "docs/MODEL.md",
        "2026-11-02",
    )
    assert entry.lines == ("  " + PARAGRAPH,)
    assert (entry.unit.kind, entry.unit.first, entry.unit.last) == ("paragraph", 1, 1)


def test_an_entry_may_add_the_accepted_rewrite_last() -> None:
    sections = (
        "## The owner's words\n\nNo.\n\n## Where it came from\n\nA test.\n\n"
        "## Accepted rewrite\n\n```text\nA plainer paragraph.\n```\n"
    )
    entry = parse_entry("jargon-2026-11-02-a.md", _entry(sections=sections), TABLE)

    assert entry.accepted_lines == ("A plainer paragraph.",)
    assert parse_entry("jargon-2026-11-02-a.md", _entry(), TABLE).accepted_lines is None


@pytest.mark.parametrize(
    ("name", "text", "reason"),
    [
        ("jargon-2026-11-02-a.md", _entry(kind="typo"), "kind 'typo' is not one of"),
        ("typo-2026-11-02-a.md", _entry(kind="typo"), "kind 'typo' is not one of"),
        ("jargon-2026-11-02-a.md", _entry(rejected="yesterday"), "is not a date"),
        ("jargon-2026-11-03-a.md", _entry(), "its name must be jargon-2026-11-02-SLUG.md"),
        ("jargon-2026-11-02-a.md", _entry(path="CHANGELOG.md"), "no row of the reader table"),
        (
            "jargon-2026-11-02-a.md",
            _entry().replace("rejected: 2026-11-02\n", "rejected: 2026-11-02\nwho: me\n"),
            "exactly kind, file, rejected",
        ),
        (
            "jargon-2026-11-02-a.md",
            _entry(sections="## The owner's words\n\nNo.\n"),
            "its sections are Paragraph, The owner's words, and must be",
        ),
        (
            "jargon-2026-11-02-a.md",
            _entry(sections="## Where it came from\n\nA.\n\n## The owner's words\n\nNo.\n"),
            "its sections are",
        ),
        (
            "jargon-2026-11-02-a.md",
            _entry(sections="## The owner's words\n\n## Where it came from\n\nA test.\n"),
            'section "The owner\'s words" is empty',
        ),
        (
            "jargon-2026-11-02-a.md",
            _entry(sections="### The owner's words\n\nNo.\n"),
            "is not a second-level heading",
        ),
        (
            "jargon-2026-11-02-a.md",
            _entry().replace("```text\n" + PARAGRAPH + "\n```", PARAGRAPH),
            "one closed fenced block and nothing else",
        ),
        (
            "jargon-2026-11-02-a.md",
            _entry(paragraph=" ".join(["word"] * (MIN_WORDS - 1))),
            f"the review reads only units of {MIN_WORDS} or more",
        ),
        (
            "jargon-2026-11-02-a.md",
            _entry(paragraph=PARAGRAPH + "\n\n" + PARAGRAPH),
            "reads as 2 units of docs/MODEL.md, not one",
        ),
        (
            "jargon-2026-11-02-a.md",
            _entry(path="src/pkg/model.py", paragraph='"""' + PARAGRAPH),
            "does not parse as src/pkg/model.py would",
        ),
        (
            "jargon-2026-11-02-a.md",
            _entry(
                sections="## The owner's words\n\nNo.\n\n## Where it came from\n\nA.\n\n"
                "## Accepted rewrite\n\nA plainer paragraph.\n"
            ),
            "the Accepted rewrite section must hold one closed fenced block",
        ),
    ],
)
def test_a_malformed_entry_is_refused_with_its_reason(name: str, text: str, reason: str) -> None:
    with pytest.raises(ValueError) as raised:
        parse_entry(name, text, TABLE)
    assert reason in str(raised.value)


def test_a_docstring_entry_is_read_with_its_indent_removed() -> None:
    paragraph = f'    """{PARAGRAPH}"""'
    entry = parse_entry(
        "jargon-2026-11-02-a.md", _entry(path="src/pkg/m.py", paragraph=paragraph), TABLE
    )

    assert entry.unit.kind == "docstring"
    assert entry.lines == (paragraph,)


def test_verdicts_are_read_through_emphasis_and_code_marks() -> None:
    reply = "Notes on [1].\n**[1] rewrite**\n\n`[2] keep`\n### [3] Rewrite\n"

    assert verdicts(reply, 3) == ["rewrite", "keep", "rewrite"]


@pytest.mark.parametrize(
    ("reply", "reason"),
    [
        ("[1] rewrite\n", "[2] has no verdict"),
        ("[1] rewrite\n[2] keep\n[2] rewrite\n", "[2] has keep and rewrite"),
        ("[1] rewrite\n[2] keep\n[3] keep\n", "[3] was not shown"),
    ],
)
def test_a_reply_without_one_verdict_per_unit_is_refused(reply: str, reason: str) -> None:
    with pytest.raises(ValueError) as raised:
        verdicts(reply, 2)
    assert reason in str(raised.value)


def test_show_gives_the_reviewer_the_rule_and_the_paragraph_only() -> None:
    """The copy editor loads no project rule, so `show` must open with the writing rule."""
    entry = parse_entry("jargon-2026-11-02-a.md", _entry(), TABLE)

    shown = show([entry], TABLE)

    assert shown.startswith(new_prose.RULE.read_text(encoding="utf-8").rstrip("\n"))
    assert "Readers of docs/MODEL.md:\n  - A clinician.\n" in shown
    assert f"[1] docs/MODEL.md, rows 1-1, paragraph, {MIN_WORDS} words, for: A clinician" in shown
    assert f"    1 > {PARAGRAPH}" in shown
    assert "jargon" not in shown
    assert "Unintelligible" not in shown


def test_check_refuses_a_set_that_no_run_of_the_current_prompt_has_read(tmp_path: Path) -> None:
    root = _root(tmp_path, {"jargon-2026-11-02-a.md": _entry()})

    assert any("no run of the set used the current prompt" in p for p in check(root, PROMPT, TABLE))


def test_check_passes_once_a_run_of_the_current_prompt_flags_every_entry(tmp_path: Path) -> None:
    root = _root(
        tmp_path,
        {"jargon-2026-11-02-a.md": _entry(), "length-2026-11-02-b.md": _entry(kind="length")},
    )
    _run(root, "one.json", _reply("rewrite", "rewrite"))

    assert check(root, PROMPT, TABLE) == []


def test_a_run_that_kept_an_entry_fails_even_beside_one_that_flagged_it(tmp_path: Path) -> None:
    """A miss stays on record, so running the same prompt again until it passes clears nothing."""
    root = _root(tmp_path, {"jargon-2026-11-02-a.md": _entry()})
    _run(root, "first.json", _reply("keep"))
    _run(root, "second.json", _reply("rewrite"))

    assert check(root, PROMPT, TABLE) == [
        "runs/first.json kept jargon-2026-11-02-a.md: change the prompt so the review flags it, "
        "then run the set again"
    ]


def test_a_changed_prompt_needs_a_new_run_and_the_old_miss_no_longer_counts(tmp_path: Path) -> None:
    root = _root(tmp_path, {"jargon-2026-11-02-a.md": _entry()})
    _run(root, "old.json", _reply("keep"))
    changed = PROMPT + "Flag every number in e-notation.\n"

    assert any(
        "no run of the set used the current prompt" in p for p in check(root, changed, TABLE)
    )
    _run(root, "new.json", _reply("rewrite"), prompt=changed)
    assert check(root, changed, TABLE) == []


def test_a_changed_reader_row_for_a_file_the_run_read_needs_a_new_run(tmp_path: Path) -> None:
    root = _root(tmp_path, {"jargon-2026-11-02-a.md": _entry()})
    _run(root, "one.json", _reply("rewrite"))
    narrowed = reader_table(READERS.replace("E-notation.", "Nothing."))
    other_row = reader_table(READERS.replace("Our history.", "Nothing."))

    assert readers_digest(narrowed, "docs/MODEL.md") != readers_digest(TABLE, "docs/MODEL.md")
    assert any("no run of the set used" in p for p in check(root, PROMPT, narrowed))
    assert check(root, PROMPT, other_row) == []


def test_a_new_entry_after_the_run_needs_no_new_run(tmp_path: Path) -> None:
    """Only a miss is added, so the next change to the prompt is what must flag it."""
    root = _root(tmp_path, {"jargon-2026-11-02-a.md": _entry()})
    _run(root, "one.json", _reply("rewrite"))
    (root / REJECTED_DIR.relative_to(ROOT) / "length-2026-11-03-b.md").write_text(
        _entry(kind="length", rejected="2026-11-03"), encoding="utf-8"
    )

    assert check(root, PROMPT, TABLE) == []


def test_a_kind_above_its_cap_names_the_oldest_entry_to_delete(tmp_path: Path) -> None:
    entries = {
        f"jargon-2026-11-03-{n}.md": _entry(rejected="2026-11-03") for n in range(CAP_PER_KIND)
    }
    entries["jargon-2026-11-02-0.md"] = _entry()
    root = _root(tmp_path, entries)
    _run(root, "one.json", _reply(*["rewrite"] * len(entries)))

    assert check(root, PROMPT, TABLE) == [
        f"kind jargon holds {CAP_PER_KIND + 1} entries, more than {CAP_PER_KIND}: delete the "
        "oldest, jargon-2026-11-02-0.md, which git history keeps"
    ]


def test_check_names_a_malformed_entry_and_a_malformed_run(tmp_path: Path) -> None:
    root = _root(tmp_path, {"jargon-2026-11-02-a.md": _entry(kind="length")})
    folder = root / RUNS_DIR.relative_to(ROOT)
    folder.mkdir(parents=True)
    (folder / "bad.json").write_text("{}", encoding="utf-8")

    assert check(root, PROMPT, TABLE) == [
        "jargon-2026-11-02-a.md: its name must be length-2026-11-02-SLUG.md",
        "runs/bad.json: it must be an object holding exactly recorded, prompt, readers, "
        "entries, reply",
    ]


def test_record_writes_the_reply_and_refuses_one_cut_short(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    rule, prompt = tmp_path / "rule.md", tmp_path / "prompt.md"
    rule.write_text(READERS, encoding="utf-8")
    prompt.write_text(PROMPT, encoding="utf-8")
    monkeypatch.setattr(new_prose, "RULE", rule)
    monkeypatch.setattr(new_prose, "PROMPT", prompt)
    root = _root(
        tmp_path / "tree", {"jargon-2026-11-02-a.md": _entry(), "jargon-2026-11-02-b.md": _entry()}
    )
    reply = tmp_path / "reply.md"

    reply.write_text("[1] rewrite\n", encoding="utf-8")
    assert main(["record", str(reply)], root=root) == 1
    assert "not recorded: [2] has no verdict" in capsys.readouterr().err
    assert not (root / RUNS_DIR.relative_to(ROOT)).exists()

    reply.write_text("[1] rewrite\n[2] keep\n", encoding="utf-8")
    assert main(["record", str(reply)], root=root) == 1
    assert "not recorded: [1] rewrite has no closed fenced block" in capsys.readouterr().err
    assert not (root / RUNS_DIR.relative_to(ROOT)).exists()

    first, second = sorted(["jargon-2026-11-02-a.md", "jargon-2026-11-02-b.md"], key=digest)
    reply.write_text(_reply("rewrite", "keep", words=MIN_WORDS + 1), encoding="utf-8")
    assert main(["record", str(reply)], root=root) == 0
    out = capsys.readouterr().out
    assert first not in out
    assert f"kept {second}: change the prompt" in out
    (written,) = (root / RUNS_DIR.relative_to(ROOT)).glob("*.json")
    assert json.loads(written.read_text(encoding="utf-8"))["entries"] == [first, second]
    assert main(["check"], root=root) == 1

    assert main(["show"], root=root) == 0
    assert capsys.readouterr().out.startswith(READERS.rstrip("\n"))


def test_rewrites_takes_the_first_block_after_each_rewrite_verdict() -> None:
    """A summary line of verdicts, or a block above every verdict, is passed over."""
    reply = (
        "```\nnot a rewrite\n```\n"
        "Summary: [1] rewrite, [2] keep, [3] rewrite\n"
        "## [1]\n**[1] rewrite**\n```markdown\none\n```\n```\nsecond block\n```\n"
        "[2] keep\n[3] rewrite\n```\nthree\nlines\n```\n"
    )

    assert rewrites(reply) == {1: ("one",), 3: ("three", "lines")}


@pytest.mark.parametrize(
    "reply", ["[1] rewrite\n[2] rewrite\n```\ntwo\n```\n", "[1] rewrite\n```\nnever closed\n"]
)
def test_a_rewrite_verdict_with_no_closed_block_is_refused(reply: str) -> None:
    with pytest.raises(ValueError) as raised:
        rewrites(reply)
    assert str(raised.value) == "[1] rewrite has no closed fenced block"


def test_a_rewrite_that_does_not_parse_as_its_file_is_named(tmp_path: Path) -> None:
    docstring = _entry(path="src/pkg/m.py", paragraph=f'"""{PARAGRAPH}"""')
    root = _root(tmp_path, {"jargon-2026-11-02-a.md": docstring})
    _run(root, "one.json", '[1] rewrite\n```\n"""never closed\n```\n')

    (problem,) = check(root, PROMPT, TABLE)
    assert problem.startswith(
        "runs/one.json's rewrite of jargon-2026-11-02-a.md does not parse as src/pkg/m.py"
    )


def test_a_gold_standard_entry_is_named_for_a_kind_that_no_failure_has() -> None:
    """The start of an entry's name is what says, in a run's record, which verdict it needs."""
    assert GOLD_KIND not in FAILURE_KINDS
    assert expected_verdict(f"{GOLD_KIND}-2026-11-05-a.md") == "keep"
    assert all(expected_verdict(f"{kind}-2026-11-02-a.md") == "rewrite" for kind in FAILURE_KINDS)


def test_a_gold_standard_entry_records_its_file_date_and_paragraph() -> None:
    entry = parse_entry("gold-2026-11-05-a.md", _gold(), TABLE, gold=True)

    assert (entry.kind, entry.file, entry.judged.isoformat()) == (
        GOLD_KIND,
        "docs/MODEL.md",
        "2026-11-05",
    )
    assert entry.lines == (KEPT,)


@pytest.mark.parametrize(
    ("name", "text", "reason"),
    [
        ("gold-2026-11-05-a.md", _entry(), "exactly file, named"),
        ("jargon-2026-11-05-a.md", _gold(), "its name must be gold-2026-11-05-SLUG.md"),
        ("gold-2026-11-05-a.md", _gold(named="soon"), "named 'soon' is not a date"),
        (
            "gold-2026-11-05-a.md",
            _gold() + "\n## Accepted rewrite\n\n```text\nA plainer paragraph.\n```\n",
            "and must be Paragraph, The owner's words, Where it came from",
        ),
    ],
)
def test_a_malformed_gold_standard_entry_is_refused_with_its_reason(
    name: str, text: str, reason: str
) -> None:
    with pytest.raises(ValueError) as raised:
        parse_entry(name, text, TABLE, gold=True)
    assert reason in str(raised.value)
    assert not str(raised.value).endswith("optionally Accepted rewrite")


def test_a_rejected_entry_may_not_claim_the_gold_kind() -> None:
    with pytest.raises(ValueError) as raised:
        parse_entry("gold-2026-11-02-a.md", _entry(kind=GOLD_KIND), TABLE)
    assert "kind 'gold' is not one of" in str(raised.value)


def test_show_mixes_the_two_folders_and_leaves_out_an_accepted_rewrite(tmp_path: Path) -> None:
    """Neither a unit's position nor a second version of it tells the reviewer its verdict."""
    rewrite = "A plainer paragraph that the owner accepted."
    sections = (
        "## The owner's words\n\nNo.\n\n## Where it came from\n\nA test.\n\n"
        f"## Accepted rewrite\n\n```text\n{rewrite}\n```\n"
    )
    root = _root(
        tmp_path,
        {f"jargon-2026-11-02-{n}.md": _entry(sections=sections) for n in range(4)},
        {f"gold-2026-11-05-{n}.md": _gold() for n in range(4)},
    )
    entries, _ = read_set(root, TABLE)

    assert [entry.name for entry in entries] == sorted(
        [entry.name for entry in entries], key=digest
    )
    assert [entry.kind for entry in entries] != sorted(entry.kind for entry in entries)
    shown = show(entries, TABLE)
    assert rewrite not in shown
    assert GOLD_KIND not in shown


def test_a_run_that_flagged_a_gold_standard_entry_fails(tmp_path: Path) -> None:
    """A review that flags every paragraph it reads no longer passes the set."""
    root = _root(tmp_path, {"jargon-2026-11-02-a.md": _entry()}, {"gold-2026-11-05-a.md": _gold()})
    _run(root, "everything.json", _reply("rewrite", "rewrite"))

    assert check(root, PROMPT, TABLE) == [
        "runs/everything.json flagged gold-2026-11-05-a.md, which the owner named a gold "
        "standard: change the prompt so the review keeps text that serves its reader, then run "
        "the set again"
    ]


def test_a_run_that_keeps_the_gold_standard_and_flags_the_rejected_passes(tmp_path: Path) -> None:
    root = _root(tmp_path, {"jargon-2026-11-02-a.md": _entry()}, {"gold-2026-11-05-a.md": _gold()})
    order = _in_order(root, {"jargon-2026-11-02-a.md": "rewrite", "gold-2026-11-05-a.md": "keep"})
    _run(root, "one.json", _reply(*order))

    assert check(root, PROMPT, TABLE) == []


def test_a_new_gold_standard_entry_needs_a_run_of_the_current_prompt(tmp_path: Path) -> None:
    """A rejected entry is a known miss, but a gold standard is untested until a run reads it."""
    root = _root(tmp_path, {"jargon-2026-11-02-a.md": _entry()})
    _run(root, "before.json", _reply("rewrite"))
    (root / GOLD_DIR.relative_to(ROOT) / "gold-2026-11-05-a.md").write_text(
        _gold(), encoding="utf-8"
    )

    assert check(root, PROMPT, TABLE) == [
        "no run of the current prompt and readers read gold-2026-11-05-a.md: run the set, "
        "because nobody knows whether the current prompt keeps a gold-standard paragraph "
        "until a run reads it"
    ]
    order = _in_order(root, {"jargon-2026-11-02-a.md": "rewrite", "gold-2026-11-05-a.md": "keep"})
    _run(root, "after.json", _reply(*order))
    assert check(root, PROMPT, TABLE) == []


def test_a_gold_standard_entry_that_repeats_another_entry_is_refused(tmp_path: Path) -> None:
    rewrite = _words(MIN_WORDS + 5)
    sections = (
        "## The owner's words\n\nNo.\n\n## Where it came from\n\nA test.\n\n"
        f"## Accepted rewrite\n\n```text\n{rewrite}\n```\n"
    )
    root = _root(
        tmp_path,
        {"jargon-2026-11-02-a.md": _entry(sections=sections)},
        {
            "gold-2026-11-05-a.md": _gold(paragraph="  " + PARAGRAPH),
            "gold-2026-11-05-b.md": _gold(paragraph=rewrite),
        },
    )

    assert sorted(p for p in check(root, PROMPT, TABLE) if "repeats" in p) == [
        "gold-2026-11-05-a.md repeats the paragraph that jargon-2026-11-02-a.md records as "
        "rejected: record a paragraph in one entry only",
        "gold-2026-11-05-b.md repeats the accepted rewrite in jargon-2026-11-02-a.md: record "
        "a paragraph in one entry only",
    ]


def test_the_gold_standard_entries_share_the_cap_of_a_kind(tmp_path: Path) -> None:
    gold = {f"gold-2026-11-06-{n}.md": _gold(named="2026-11-06") for n in range(CAP_PER_KIND)}
    gold["gold-2026-11-05-0.md"] = _gold()
    root = _root(tmp_path, {}, gold)
    _run(root, "one.json", _reply(*["keep"] * len(gold)))

    assert check(root, PROMPT, TABLE) == [
        f"kind gold holds {CAP_PER_KIND + 1} entries, more than {CAP_PER_KIND}: delete the "
        "oldest, gold-2026-11-05-0.md, which git history keeps"
    ]
