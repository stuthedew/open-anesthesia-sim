"""Run the copy editor on one file that `tools/new_prose.py` wrote, and print its reply.

A session hands the copy editor a file of passages at close-out step 8, in the
pull-request skill, and under reply rule 16 in
`.claude/rules/instruction-writing.md`. The copy editor's instructions are kept
only in the body of `.claude/agents/copy-editor.md`. A Projects thread cannot
start that agent, because a thread does not load `.claude/agents/`. The fallback
is a general-purpose agent given the agent file's text, but that agent loads
every resident instruction that the copy editor is meant to run without
(`PL-TQ4J`).

So this tool runs the copy editor as its own `claude -p` process, the same way
in every kind of session. The process starts in an empty directory that holds
only the request, so it finds no `CLAUDE.md` or rule to load. Inside the
repository, even `claude -p --agent copy-editor` loads the resident
instructions. The process's system prompt is the agent file's body, its one
tool is Read, and it loads no settings file.

When the first read rewrites a passage, a fresh run audits the edit, because
experienced technical editors make at least two passes (project owner,
2026-11-04, ratified, `PL-HGZS`). That run gets the same request, with each
rewritten passage replaced by its edit. A line before the passages marks the
request as a second read (`SECOND_READ`). The audit fixes what the earlier
reads missed or introduced. Audits go on until one changes nothing, up to
`MAX_READS` reads in all (project owner, 2026-11-05, ratified, over exactly
two reads). When the first read rewrites nothing, there is no audit. The
printed reply gives each passage once, in the text of the last read that
rewrote it, else `[N] keep`. Every read's notes follow.

**A separate meaning check then compares each edit with its original**
(`PL-F0Q2`). The copy editor's own audits passed about 120 statements that its
line edit of `docs/MODEL.md` had lost or weakened: a requirement restated as a
description, a limiting word such as "only" cut, a list item or a scope clause
dropped, a stated reason cut. So `CHECK_PANEL` fresh runs of the check each
read every original sentence against the edit. Their instructions are those in
`.claude/agents/meaning-check.md`, followed by the list that the copy editor's
own instructions give under `NEVER_LOSES`. Each statement that any of them
finds lost goes back to the copy editor in a restore read, and the checks run
again, up to `MAX_CHECK_ROUNDS` rounds. A passage that still loses a statement
after the last round is printed as `[N] keep`, with what it lost under "Meaning
check:", so no rewrite in which a check still finds a loss reaches a file.

A passage gets at most `LIMITED_READS` reads and `LIMITED_CHECK_ROUNDS` rounds
of meaning checks where it is written only for a later session or for the
project owner, such as an item brief, a workflow file, a commit message, a pull
request body or a reply (project owner, 2026-11-09). Its header's "For:" line
names its readers, and `LIMITED_READERS` lists the ones that qualify. A passage
with any other reader keeps the full limits.

Before the reply is printed, a code check compares each rewrite with the rows it
replaces (`check_code`). It refuses a rewrite that changes code, a fenced
block, a heading or an HTML comment, that writes an HTML comment or a code
name the passage does not hold, or that cuts a decision's tag without keeping
the item's id. A refused rewrite is printed as `[N] keep`, with the reason
under "Code check:". Under the same heading, the reply also lists each code
name a rewrite dropped and each comment it cut whole (project owner,
2026-11-04, `PL-HGZS`).

**A whole document is reviewed in two parts** (project owner, 2026-11-04,
`PL-HGZS`). With `--structure FILE`, the tool runs the structure read, which
rewrites nothing. A short document gets one read. A long one gets one read per
chapter, then one read of all the chapters' outlines. With `--sections FILE`,
the tool then line-edits each section alone, with the audits and meaning
checks that every run has. All of those requests come from
`tools/new_prose.py`.

The `[models]` table in `docket.toml` chooses the model and effort for the
roles `copy-editor` and `meaning-check`. The runs are billed to the account
that `claude` signs in with, as an Agent call would be.

Prints the reply on standard output and one line of counts on standard
error. Exits 0 when the copy editor replied, and 1 with the reason when
`claude` is missing, fails, times out or returns an error, or when the first
read's reply does not give each passage one verdict.
"""

from __future__ import annotations

import argparse
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import tokenize
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "subprojects" / "docket" / "src"))

from docket.config import load as load_config  # noqa: E402
from docket.lines import split_lines  # noqa: E402
from docket.markdown import FENCE, headings  # noqa: E402
from docket.markdown import read as read_markdown  # noqa: E402
from docket.model import FRONT_MATTER_RE  # noqa: E402
from docket.release import code_spans  # noqa: E402
from docket.store import CITED_ID_RE  # noqa: E402

from new_prose import (  # noqa: E402
    CHECK_PROMPT,
    PROMPT,
    RULE_END,
    Part,
    outline_report,
    part_reports,
    passage_number,
    passage_place,
    read_row,
    read_span,
    respan,
    row_line,
    rule_table,
    structure_reports,
    with_rule,
)
from rejected_prose import rewrites, unmarked, verdicts  # noqa: E402

#: The role `docket.toml`'s `[models]` table is asked about.
ROLE = "copy-editor"
#: The name the request takes inside the copy editor's empty directory.
REQUEST_NAME = "request.txt"
#: What the copy editor is asked to do with the request.
TASK = f"Copy-edit the passages in {REQUEST_NAME}."
#: A read that takes longer than this is stopped. Each of the two reads has
#: its own limit. The longest copy edit measured so far read 29 passages in
#: about 15 minutes (`PL-22T5`), so 40 minutes leaves room for a larger branch
#: while still ending a run that has stalled.
COPY_EDIT_TIMEOUT_S = 40 * 60
#: Turns off the memory index that a session would otherwise load, so the
#: copy editor's context is its instructions and the request alone.
QUIET_ENV = {"CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1"}
#: The heading under which a second read's request gives each edited passage
#: as it stood before the first read, so that the audit can find a fact the
#: first read lost or changed. The edit alone cannot show such a fact
#: (`PL-HGZS`). The next constant (`SECOND_READ`) is the line that opens the
#: prose of a second read's request. The copy editor's instructions say what
#: to do with a request that holds that line.
BEFORE = "Before the first edit"
SECOND_READ = (
    "Second read. The rows marked > are the text after the earlier copy edits, and "
    "each header's word counts are the counts before them. The text before the "
    f'first edit follows the passages, under "{BEFORE}".'
)


#: The most reads one request gets, counting the first edit and the audits
#: after it. A first read that rewrites a passage gets an audit because
#: experienced technical editors make "at least two passes" (Hart, "Interview
#: responses: The editing practices of professional technical editors", 2010,
#: https://geoff-hart.com/articles/2010/interview.htm). Audits go on until one
#: changes nothing, because runs 16 to 18 of section 1 each left one or two
#: faults after two reads. A limit of four bounds the cost of a passage that
#: never settles, at about $1 and 10 minutes for each read of a 1,200-word
#: section. Raising the limit lets such a passage run longer.
MAX_READS = 4
#: The readers of the texts whose passages get fewer reads: the item briefs,
#: workflow files, commit messages and pull request bodies that a later
#: session reads, and the replies sent to the project owner. Each name is a
#: reader of a row in the plain-writing rule's table, as the passage header's
#: "For:" gives it. A passage gets `LIMITED_READS` reads and
#: `LIMITED_CHECK_ROUNDS` rounds of meaning checks only where every reader its
#: header names is one of these, so a simulator document never gets fewer.
LIMITED_READERS = (
    "A later session, or the owner reading the history",
    "The project owner, an anesthesiologist and intensive-care physician",
)
#: The most copy-editor reads a passage for `LIMITED_READERS` gets: the edit
#: and one audit (project owner, 2026-11-09: "Copy edit non-core human
#: documents like PL items etc at most twice"). A later read's rewrite of such
#: a passage is not taken. Raising the limit spends up to `MAX_READS` reads on
#: text that no clinician reads.
LIMITED_READS = 2
#: The name of each read in order, used in its files and its notes.
READ_NAMES = ("first", "second", "third", "fourth")

#: The meaning check's role in the `[models]` table of `docket.toml`.
CHECK_ROLE = "meaning-check"
#: The heading of the section in the copy editor's instructions that lists what
#: an edit never loses. The meaning check is given the same section, so the
#: copy editor and the check hold an edit to one list.
NEVER_LOSES = "## What an edit never loses"
#: The line that opens the prose of a meaning check's request.
MEANING_CHECK = (
    "Meaning check. The rows marked > are the text after the copy edit. The text before "
    f'the first edit follows the passages, under "{BEFORE}".'
)
#: The heading under which a restore read's request lists what the check found lost.
LOST = "Lost in the edit"
#: The line that opens the prose of a restore read's request.
RESTORE_READ = (
    "Restore read. The rows marked > are the text after the copy edit. The text before "
    f'the first edit follows the passages, under "{BEFORE}", and what a separate check '
    f'found the edit lost follows that, under "{LOST}".'
)
#: How many separate meaning checks read each version of the edit. Runs of
#: one check on one edit find different statements lost: on
#: `docs/MODEL.md` § "Supported run length", four runs on the same edit found
#: one or two each of the four statements that it had lost, and no run found
#: all four (`PL-F0Q2`). So each version goes to two checks, a statement that
#: either finds lost goes back to the copy editor, and an edit passes only
#: when both find nothing. A third check would cost one more read each round.
CHECK_PANEL = 2
#: The most rounds of meaning checks one request gets: one round after the
#: copy editor's reads, and one after each restore read. The rounds stop early
#: when no check finds anything lost. A later round can find a statement that
#: an earlier round missed, or one that a restore read lost. Five rounds allow
#: four restore reads, which is how many the edit above needed with one check
#: a round. A round of two checks and a restore read together cost about as
#: much as the copy editor's first read on the same section. A lower limit
#: keeps more passages unedited, and a higher one spends more reads on a
#: passage whose restores keep failing.
MAX_CHECK_ROUNDS = 5
#: The most rounds of meaning checks a passage for `LIMITED_READERS` gets,
#: which allows it at most one restore read (project owner, 2026-11-09, with
#: `LIMITED_READS`). A loss that the last of these rounds still finds keeps the
#: passage as it was.
LIMITED_CHECK_ROUNDS = 2
# regex: the readers a passage header names, after its "For:"
FOR_RE = re.compile(r"\bFor: (.+)$")
# regex: a meaning check's verdict line, such as "[3] lost"
CHECK_VERDICT_RE = re.compile(r"^[\s*_`]*\[(\d+)\][*_`]*\s*(same|lost)\b", re.IGNORECASE)


class Refused(Exception):
    """The copy editor could not be run, or did not reply, with the reason."""


def instructions(prompt: str) -> str:
    """The copy editor's instructions: the agent file's text without its front matter."""
    match = FRONT_MATTER_RE.match(prompt)
    if match is None:
        raise Refused(f"{PROMPT} has no front matter, so its instructions cannot be found")
    return match.group(2).lstrip("\n")


def never_loses(prompt: str) -> str:
    """The section of the copy editor's instructions `prompt` headed `NEVER_LOSES`.

    Raises `Refused` where the instructions hold no such section, because the
    meaning check cannot then be told what to check.
    """
    lines = split_lines(prompt)
    if NEVER_LOSES not in lines:
        raise Refused(f"{PROMPT} has no section {NEVER_LOSES!r} for the meaning check")
    start = lines.index(NEVER_LOSES)
    end = next(
        (row for row in range(start + 1, len(lines)) if lines[row].startswith("## ")), len(lines)
    )
    return "\n".join(lines[start:end]).strip("\n")


def claude_argv(
    claude: str, system_prompt: Path, model: str, effort: str, task: str = TASK
) -> list[str]:
    """The `claude -p` command that does `task`, by default a copy edit, on `REQUEST_NAME`."""
    return [
        claude,
        "-p",
        task,
        "--model",
        model,
        "--effort",
        effort,
        "--tools",
        "Read",
        "--system-prompt-file",
        str(system_prompt),
        "--setting-sources",
        "",
        "--output-format",
        "json",
    ]


def reply_of(output: str) -> tuple[str, str]:
    """The reply in `claude -p`'s JSON `output`, and one line of what the run read and cost."""
    try:
        data = json.loads(output[output.index("{") :])
    except ValueError as error:
        raise Refused(f"claude printed no JSON result: {error}") from error
    if data.get("is_error") or not isinstance(data.get("result"), str):
        raise Refused(f"claude returned an error: {data.get('result')!r}")
    usage = data.get("usage", {})
    read = sum(
        usage.get(key, 0)
        for key in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")
    )
    counts = (
        f"copy_edit: read {read} tokens, wrote {usage.get('output_tokens', 0)}, "
        f"{data.get('num_turns', '?')} turns, ${data.get('total_cost_usd', 0):.2f}"
    )
    return data["result"], counts


def prose_of(request: str) -> tuple[str, list[str]]:
    """`request` up to and including the line that ends the writing rule, and the lines after it.

    Raises `Refused` where the request has no such line (`RULE_END`).
    """
    head, marker, body = request.partition(RULE_END)
    if not marker:
        raise Refused(f"the request has no line {RULE_END!r}, so its passages cannot be found")
    return head + marker, split_lines(body)


def passage_count(request: str) -> int:
    """How many passages `request` numbers. Raises `Refused` unless they run 1, 2, 3 in order."""
    numbers = [n for line in prose_of(request)[1] if (n := passage_number(line)) is not None]
    if numbers != list(range(1, len(numbers) + 1)):
        raise Refused(f"the request numbers its passages {numbers}, not from 1 in order")
    return len(numbers)


def limited_passages(request: str) -> frozenset[int]:
    """The passages of `request` whose header names only `LIMITED_READERS` as their readers.

    A passage whose header names no reader, or any other reader, keeps the full
    limits, so no passage is ever given fewer reads by mistake.
    """
    found = set()
    for line in prose_of(request)[1]:
        number = passage_number(line)
        match = FOR_RE.search(line) if number is not None else None
        if number is None or match is None:
            continue
        named = [who.strip() for who in match[1].split(";")]
        if named and all(who in LIMITED_READERS for who in named):
            found.add(number)
    return frozenset(found)


def marked_rows(lines: Sequence[str]) -> dict[int, list[str]]:
    """The text of each passage's rows marked `>`, by the passage's number.

    A passage's rows are the first unbroken run of rows marked `>` after its
    header. Rows marked `|` and other lines before the run are passed over.
    """
    found: dict[int, list[str]] = {}
    current: int | None = None
    for line in lines:
        number = passage_number(line)
        if number is not None:
            current = number
            continue
        if current is None:
            continue
        row = read_row(line)
        if row is not None and row[1] == ">":
            found.setdefault(current, []).append(row[2])
        elif current in found:
            current = None
    return found


def second_request(request: str, blocks: Mapping[int, Sequence[str]]) -> str:
    """`request` with each passage in `blocks` edited, for the second read (`edited_request`)."""
    return edited_request(request, blocks, SECOND_READ)


def edited_request(
    request: str, blocks: Mapping[int, Sequence[str]], opening: str, after: Sequence[str] = ()
) -> str:
    """`request` with each passage in `blocks` edited, its prose opening with `opening`.

    `blocks` maps a passage's number to the rows an earlier read gave it. Those
    rows replace the passage's rows marked `>`, and are numbered from where the
    old rows began. Each row, header and section title after them in the same
    listing is renumbered to follow. After the last passage, under the heading
    `BEFORE`, each edited passage's rows appear as the first read was given
    them, and the lines `after` follow those. Raises `Refused` where a passage
    in `blocks` has no rows marked `>`.
    """
    head, lines = prose_of(request)
    marked = marked_rows(lines)
    out: list[str] = []
    before: dict[int, list[str]] = {}
    shift = 0
    waiting: int | None = None
    index = 0
    while index < len(lines):
        line = lines[index]
        number = passage_number(line)
        row = read_row(line)
        if number is not None:
            span = read_span(line)
            assert span is not None, "passage_number reads a header only where it has a span"
            first, last = span[0] + shift, span[1] + shift
            if number in blocks:
                last = first + len(blocks[number]) - 1
                waiting = number
            out.append(respan(line, first, last))
        elif row is None:
            shift = 0
            out.append(line)
        elif row[1] == ">" and waiting is not None:
            was = marked[waiting]
            block = blocks[waiting]
            before[waiting] = was
            out += [row_line(row[0] + shift + k, ">", text) for k, text in enumerate(block)]
            shift += len(block) - len(was)
            waiting = None
            index += len(was)
            continue
        else:
            out.append(row_line(row[0] + shift, *row[1:]) if shift else line)
        index += 1
    missing = sorted(set(blocks) - set(before))
    if missing:
        raise Refused(f"passages {missing} have no rows marked > to replace")
    out += ["", f"{BEFORE}:"]
    for number in sorted(before):
        out += ["", f"Passage {number}, the rows marked > as the first read was given them:"]
        out += fenced(before[number])
    out += list(after)
    return f"{head}\n\n{opening}" + "\n".join(fitted_titles(out))


def restore_request(
    request: str, blocks: Mapping[int, Sequence[str]], lost: Mapping[int, str]
) -> str:
    """`request` with the edits in `blocks`, and under `LOST` what the meaning check found lost.

    `lost` maps a passage's number to the meaning check's findings for it.
    """
    after = ["", f"{LOST}:"]
    for number in sorted(lost):
        after += ["", f"Passage {number}:", "", unmarked(lost[number])]
    return edited_request(request, blocks, RESTORE_READ, after)


def meaning_findings(reply: str, count: int) -> dict[int, str]:
    """What the meaning check's `reply` found lost, by passage number, for `count` passages.

    A passage marked "[N] same" lost nothing and is left out. The findings of a
    passage marked "[N] lost" are the lines after its verdict, up to the next
    verdict. Raises `ValueError` where a passage has no verdict or two, or a
    verdict numbers a passage that was not shown.
    """
    lines = split_lines(reply)
    marks = [
        (row, int(match.group(1)), match.group(2).lower())
        for row, line in enumerate(lines)
        if (match := CHECK_VERDICT_RE.match(line))
    ]
    numbers = [number for _, number, _ in marks]
    problems = [f"[{n}] was not shown" for n in sorted(set(numbers)) if not 1 <= n <= count]
    problems += [
        f"[{n}] has {numbers.count(n) or 'no'} verdicts"
        for n in range(1, count + 1)
        if numbers.count(n) != 1
    ]
    if problems:
        raise ValueError("; ".join(problems))
    found: dict[int, str] = {}
    for position, (row, number, verdict) in enumerate(marks):
        end = marks[position + 1][0] if position + 1 < len(marks) else len(lines)
        if verdict == "lost":
            found[number] = "\n".join(lines[row + 1 : end]).strip("\n") or "(no finding given)"
    return found


def fitted_titles(lines: Sequence[str]) -> list[str]:
    """`lines`, with each section title's last row set to the last row listed under it.

    A title is a line that gives a span of rows and ends with a colon, such as
    "tools/copy_edit.py, rows 1-57:", but is not a passage header.
    """
    out = list(lines)
    for index, line in enumerate(out):
        span = read_span(line)
        if span is None or passage_number(line) is not None or not line.endswith(":"):
            continue
        last = None
        for later in out[index + 1 :]:
            if (row := read_row(later)) is not None:
                last = row[0]
            elif passage_number(later) is None:
                break
        if last is not None:
            out[index] = respan(line, span[0], last)
    return out


def notes(reply: str) -> str:
    """The `reply` without its fenced blocks, each "[N]" written "Passage N".

    An "[N]" left in the notes would give passage N a second verdict.
    Runs of blank lines that the dropped blocks leave become one.
    """
    lines = split_lines(reply)
    dropped = {
        row
        for block in read_markdown(lines).blocks
        if block.kind == FENCE
        for row in range(block.start, block.end)
    }
    kept: list[str] = []
    for row, line in enumerate(lines):
        if row in dropped or (not line.strip() and kept and not kept[-1].strip()):
            continue
        kept.append(unmarked(line))
    return "\n".join(kept).strip("\n")


def fenced(rows: Sequence[str]) -> list[str]:
    """`rows` in a fenced block whose fence is longer than any fence of backticks inside."""
    starts = (row.lstrip(" ") for row in rows)
    inner = [len(start) - len(start.lstrip("`")) for start in starts if start.startswith("```")]
    fence = "`" * max([3, *(length + 1 for length in inner)])
    return [fence, *rows, fence]


@dataclass(frozen=True)
class CodeCheck:
    """The reasons a rewrite is refused, and each code name and comment it cut.

    The copy editor may change prose and nothing else. Its instructions say so.
    This check enforces the rule on each rewrite the copy editor returns, so that
    no session applies a rewrite that changed code (project owner, 2026-11-04,
    `PL-HGZS`).
    """

    refused: tuple[str, ...] = ()
    dropped: tuple[str, ...] = ()
    cut_comments: tuple[str, ...] = ()


#: Python tokens that are prose or layout, which a copy edit may change. Every
#: other token is code and must come back as it was. A string literal counts as
#: prose because the copy editor edits docstrings and the string literals a
#: learner reads.
PROSE_TOKENS = frozenset(
    {
        tokenize.COMMENT,
        tokenize.STRING,
        tokenize.FSTRING_MIDDLE,
        tokenize.NL,
        tokenize.NEWLINE,
        tokenize.INDENT,
        tokenize.DEDENT,
        tokenize.ENDMARKER,
    }
)
# regex: a decision's tag, such as "(project owner, 2026-10-18, ratified, over X, `PL-W5WX`)"
DECISION_TAG_RE = re.compile(r"\(project owner,[^()]*\)")
# regex: an HTML comment, which a Markdown file uses for its provenance markers
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.S)


def python_code(rows: Sequence[str]) -> list[tuple[int, str]] | list[str]:
    """The tokens of Python `rows` other than prose, or failing that, their code lines.

    An excerpt can start inside an indented block, so it may not tokenize. When
    it does not, the code is each line that holds no quote and no `#`, since such
    a line can hold only code.
    """
    try:
        return [
            (token.type, token.string)
            for token in tokenize.generate_tokens(io.StringIO("\n".join(rows) + "\n").readline)
            if token.type not in PROSE_TOKENS
        ]
    except (tokenize.TokenError, SyntaxError):
        return sorted(line.strip() for line in rows if line.strip() and not set("\"'#") & set(line))


def markdown_code(rows: Sequence[str]) -> tuple[Counter[str], Counter[str], list[str], list[str]]:
    """The fenced blocks, HTML comments, headings and code-span contents of Markdown `rows`."""
    blocks = [block for block in read_markdown(rows).blocks if block.kind == FENCE]
    inside = {row for block in blocks for row in range(block.start, block.end)}
    fences = Counter("\n".join(rows[block.start : block.end]) for block in blocks)
    prose = "\n".join(line for row, line in enumerate(rows) if row not in inside)
    comments = Counter(HTML_COMMENT_RE.findall(prose))
    titles = [f"{'#' * mark.level} {mark.title}" for mark in headings(rows)]
    spans = [found["content"].strip() for found in code_spans(prose)]
    return fences, comments, titles, spans


def check_code(
    path: str, before: Sequence[str], seen: Sequence[str], after: Sequence[str]
) -> CodeCheck:
    """What the rewrite `after` of the rows `before` did to code, in the file at `path`.

    A rewrite is refused where it changes Python code, a fenced block, a heading
    or an HTML comment, where it writes an HTML comment or a code name that the
    passage does not hold, or where it cuts the item id beside a decision.
    `seen` is every row of the passage, the read-only
    rows included, so a code name the copy editor took from any of them is not
    new. A comment the rewrite cut whole is listed and not refused, because the
    copy editor's instructions say to cut a source comment with the number it
    backs. The documentation check still refuses a stored value that a paragraph
    states with no source comment, but not a figure derived from that value, so
    the session judging the edit checks such figures.
    """
    refused: list[str] = []
    if path.endswith(".py") and python_code(before) != python_code(after):
        refused.append("it changed code outside the docstrings, comments and strings")
    old_fences, old_comments, old_titles, old_spans = markdown_code(before)
    new_fences, new_comments, new_titles, new_spans = markdown_code(after)
    if not path.endswith(".py"):
        if old_fences != new_fences:
            refused.append("it changed, added or removed a fenced block")
        # A rewrite may repeat a comment the passage holds, to go with a number stated twice.
        if set(new_comments) - set(old_comments):
            refused.append("it changed an HTML comment or wrote a new one")
        if old_titles != new_titles:
            refused.append("it changed, added or removed a heading")
    # A code name counts as taken from the text when the passage already holds
    # it anywhere, even inside a longer code span, a source comment or the prose.
    known = " ".join(" ".join(seen).split())
    added = sorted({span for span in new_spans if " ".join(span.split()) not in known})
    if added:
        refused.append(
            "it wrote code names the passage does not hold: "
            + ", ".join(f"`{span}`" for span in added)
        )
    refused += [
        f"it cut the decision that `{item}` records without naming the item"
        for item in lost_decisions(before, after)
    ]
    dropped = tuple(sorted({span for span in old_spans if span not in new_spans}))
    cut = tuple(sorted((old_comments - new_comments).elements()))
    return CodeCheck(tuple(refused), dropped, cut)


def lost_decisions(before: Sequence[str], after: Sequence[str]) -> tuple[str, ...]:
    """Each item that a decision's tag in `before` names and `after` no longer names.

    The copy editor may cut a decision's tag whole only where the item it names
    records the decision. The item's id must then stay beside the decision.
    Without the id, nothing in the text leads to the record of who decided and
    what was chosen over what. A blind judge preferred the original of one
    section only because its edit had lost such an id (`PL-HGZS`). The rewrite
    is refused rather than listed, because the copy editor cut such an id in 4
    of the 72 rewrites of the first branch it edited after the fix, and a
    refusal keeps the passage without relying on the session to restore it.
    """
    old = " ".join(" ".join(before).split())
    new = " ".join(after)
    named = {item for tag in DECISION_TAG_RE.findall(old) for item in CITED_ID_RE.findall(tag)}
    return tuple(sorted(item for item in named if item not in new))


def passage_texts(request: str) -> dict[int, tuple[str, list[str], list[str]]]:
    """Each passage's file, its rows marked `>`, and all its rows, by the passage's number."""
    found: dict[int, tuple[str, list[str], list[str]]] = {}
    current: int | None = None
    for line in prose_of(request)[1]:
        number = passage_number(line)
        if number is not None:
            place = passage_place(line) or ""
            path = place.partition(" § ")[0].rstrip(", ").strip()
            found[number] = (path, [], [])
            current = number
            continue
        row = read_row(line)
        if current is None or row is None:
            continue
        found[current][2].append(row[2])
        if row[1] == ">":
            found[current][1].append(row[2])
    return found


def code_report(request: str) -> Callable[[int, Sequence[str]], CodeCheck]:
    """A check of a passage's rewrite against the code that `request` gives for that passage."""
    texts = passage_texts(request)

    def check(number: int, rows: Sequence[str]) -> CodeCheck:
        path, before, seen = texts[number]
        return check_code(path, before, seen, rows)

    return check


def merge(
    replies: Sequence[str],
    count: int,
    check: Callable[[int, Sequence[str]], CodeCheck] | None = None,
    names: Sequence[str] | None = None,
    lost: Mapping[int, str] | None = None,
    checks: Sequence[tuple[str, str]] = (),
    skipped: Sequence[frozenset[int]] = (),
) -> str:
    """One reply from every read's reply in `replies`, in order, for `count` passages.

    `names` has one name for each read in `replies`, in the same order, and
    defaults to the first names in `READ_NAMES`. Each passage gets one verdict:
    the text of the last read that rewrote it, else `[N] keep`. `skipped`
    gives, for each reply in order, the passages whose rewrite in that reply
    is not taken, because the passage had already had all the reads it is
    allowed (`LIMITED_READS`). Where `check` is given, it refuses a rewrite
    that changed code, and the passage then becomes `[N] keep` with the reason
    under "Code check:". The check also lists each code name a rewrite
    dropped. A passage in `lost` becomes `[N] keep` too, with what the meaning
    check found it lost under "Meaning check:". The notes of every read
    follow, then those of each meaning check in `checks`, under its label, so
    that every cut, move, query and finding is kept. Raises `Refused` where a
    reply does not give each passage one verdict, or a rewrite has no text.
    """
    lost = {} if lost is None else lost
    names = READ_NAMES[: len(replies)] if names is None else names
    if len(names) != len(replies):
        raise Refused(f"{len(replies)} replies were given {len(names)} names")
    found: list[dict[int, tuple[str, ...]]] = []
    for index, (name, reply) in enumerate(zip(names, replies, strict=True)):
        late = skipped[index] if index < len(skipped) else frozenset()
        try:
            verdicts(reply, count)
            found.append({n: rows for n, rows in rewrites(reply).items() if n not in late})
        except ValueError as error:
            raise Refused(f"the {name} read's reply cannot be read: {error}") from error
    out: list[str] = []
    checked: list[str] = []
    meant: list[str] = []
    for number in range(1, count + 1):
        rows = next((made[number] for made in reversed(found) if number in made), None)
        if rows is not None and number in lost:
            meant += [
                f"- Passage {number}: the rewrite was refused, because it still loses what the "
                "original says:",
                "",
                unmarked(lost[number]),
                "",
            ]
            out += [f"[{number}] keep", ""]
            continue
        result = CodeCheck() if rows is None or check is None else check(number, rows)
        for reason in result.refused:
            checked.append(f"- Passage {number}: the rewrite was refused, because {reason}.")
        for span in result.dropped:
            checked.append(
                f"- Passage {number}: the rewrite no longer names `{span}`. "
                "Check that its reader does not need it."
            )
        for comment in result.cut_comments:
            checked.append(
                f"- Passage {number}: the rewrite cut the comment {comment}. "
                "Check that it also cut the number the comment backs."
            )
        if rows is None or result.refused:
            out += [f"[{number}] keep", ""]
        else:
            out += [f"[{number}] rewrite", "", *fenced(rows), ""]
    if checked:
        out += ["Code check:", "", *checked, ""]
    if meant:
        out += ["Meaning check:", "", *meant]
    for name, reply in zip(names, replies, strict=True):
        out += [f"Notes from the {name} read:", "", notes(reply), ""]
    for label, reply in checks:
        out += [f"Notes from {label}:", "", notes(reply), ""]
    merged = "\n".join(out).rstrip("\n")
    try:
        verdicts(merged, count)
    except ValueError as error:
        raise Refused(f"the reads' notes left a verdict mark: {error}") from error
    return merged


def read_once(
    text: str,
    claude: str,
    prompt: str,
    model: str,
    effort: str,
    env: Mapping[str, str],
    task: str = TASK,
) -> tuple[str, str]:
    """The reply and counts of one run of `claude -p` on the request `text`.

    `prompt` is the system prompt and `task` what it is asked to do. The run
    starts in an empty directory that holds only the request.
    """
    with tempfile.TemporaryDirectory() as held, tempfile.TemporaryDirectory() as work:
        system_prompt = Path(held) / "copy-editor.md"
        system_prompt.write_text(prompt, encoding="utf-8")
        (Path(work) / REQUEST_NAME).write_text(text, encoding="utf-8")
        try:
            done = subprocess.run(
                claude_argv(claude, system_prompt, model, effort, task),
                cwd=work,
                env={**env, **QUIET_ENV},
                stdin=subprocess.DEVNULL,
                capture_output=True,
                timeout=COPY_EDIT_TIMEOUT_S,
            )
        except subprocess.TimeoutExpired as error:
            raise Refused(f"claude did not finish within {COPY_EDIT_TIMEOUT_S} s") from error
    if done.returncode:
        reason = done.stderr.decode("utf-8", errors="replace").strip()[-500:]
        raise Refused(f"claude exited {done.returncode}: {reason}")
    return reply_of(done.stdout.decode("utf-8"))


@dataclass(frozen=True)
class Editor:
    """The `claude` program, prompt, model, effort and environment for running the copy editor."""

    claude: str
    prompt: str
    model: str
    effort: str
    env: Mapping[str, str]

    def read(self, asked: str, name: str, reads: Path | None) -> tuple[str, str]:
        """One read of the request `asked`, kept under `name` in `reads`, if given."""
        reply, counts = read_once(
            asked, self.claude, self.prompt, self.model, self.effort, self.env
        )
        if reads is not None:
            reads.mkdir(parents=True, exist_ok=True)
            (reads / f"{name}-request.txt").write_text(asked, encoding="utf-8")
            (reads / f"{name}-reply.txt").write_text(reply, encoding="utf-8")
        return reply, counts


def editor(root: Path = ROOT, env: Mapping[str, str] | None = None) -> Editor:
    """The copy editor that `docket.toml` and the agent file set up.

    Raises `Refused` where `claude` is missing or no model is chosen.
    """
    claude = shutil.which("claude")
    if claude is None:
        raise Refused("no `claude` on PATH")
    table = load_config(root).models
    if table is None:
        raise Refused(f"{root / 'docket.toml'} has no [models] table, so no model is chosen")
    choice = table.choose({"role": ROLE})
    prompt = instructions(PROMPT.read_text(encoding="utf-8"))
    return Editor(claude, prompt, choice.model, choice.effort, os.environ if env is None else env)


def checker(root: Path = ROOT, env: Mapping[str, str] | None = None) -> Editor:
    """The meaning check that `docket.toml` and the two agent files set up.

    Its instructions are `CHECK_PROMPT`'s body followed by the copy editor's
    section `NEVER_LOSES`, so the check and the copy editor hold an edit to one
    list. Raises `Refused` where `claude` is missing, no model is chosen, or
    the copy editor's instructions hold no such section.
    """
    claude = shutil.which("claude")
    if claude is None:
        raise Refused("no `claude` on PATH")
    table = load_config(root).models
    if table is None:
        raise Refused(f"{root / 'docket.toml'} has no [models] table, so no model is chosen")
    choice = table.choose({"role": CHECK_ROLE})
    own = instructions(CHECK_PROMPT.read_text(encoding="utf-8"))
    listed = never_loses(instructions(PROMPT.read_text(encoding="utf-8")))
    prompt = f"{own.rstrip()}\n\n{listed}\n"
    return Editor(claude, prompt, choice.model, choice.effort, os.environ if env is None else env)


def edit(text: str, editor: Editor, checker: Editor, reads: Path | None = None) -> tuple[str, str]:
    """Run the copy editor on the request `text` until an audit changes nothing, then check it.

    Returns its merged reply and the counts. The first read edits. Each later
    read audits the text as the earlier reads left it, and runs only while the
    last read changed a passage, up to `MAX_READS` reads. A passage written
    only for `LIMITED_READERS` takes no rewrite after its `LIMITED_READS` reads,
    and the audits stop once only such passages are still changing. An audit whose reply
    cannot be read ends the audits, and the counts say so: the reads before it
    are kept, because each of them gave every passage a verdict. Then
    `checker`, the meaning check, compares each edit with its original
    (`meaning_check`). Where `reads` names a directory, each read's request and
    reply are also written there, so that what each read changed can be judged
    alone.
    """
    first, first_counts = editor.read(text, READ_NAMES[0], reads)
    try:
        current = dict(rewrites(first))
    except ValueError as error:
        raise Refused(f"the first read's reply cannot be read: {error}") from error
    if not current:
        return first, first_counts
    count = passage_count(text)
    limited = limited_passages(text)
    replies = [first]
    names = [READ_NAMES[0]]
    counts = [first_counts]
    skipped: list[frozenset[int]] = [frozenset()]
    changing = set(current)
    for index, name in enumerate(READ_NAMES[1:MAX_READS], start=1):
        late = limited if index >= LIMITED_READS else frozenset()
        if changing <= late:
            break
        reply, reply_counts = editor.read(second_request(text, current), name, reads)
        counts.append(f"{name} read: {reply_counts.removeprefix('copy_edit: ')}")
        try:
            verdicts(reply, count)
            made = rewrites(reply)
        except ValueError as error:
            # An audit that returns no readable reply changes nothing, so the
            # reads before it still give every passage its verdict.
            counts.append(f"{name} read: reply unreadable, so it was left out ({error})")
            break
        replies.append(reply)
        names.append(name)
        skipped.append(late)
        changed = {
            number: rows
            for number, rows in made.items()
            if number not in late and current.get(number) != rows
        }
        if not changed:
            break
        changing = set(changed)
        current.update(changed)
    lost, checks = meaning_check(
        text, current, editor, checker, reads, replies, names, counts, limited, skipped
    )
    merged = merge(replies, count, code_report(text), names, lost, checks, skipped)
    return merged, "; ".join(counts)


def meaning_check(
    text: str,
    current: dict[int, tuple[str, ...]],
    editor: Editor,
    checker: Editor,
    reads: Path | None,
    replies: list[str],
    names: list[str],
    counts: list[str],
    limited: frozenset[int] = frozenset(),
    skipped: list[frozenset[int]] | None = None,
) -> tuple[dict[int, str], list[tuple[str, str]]]:
    """Check each edit in `current` against its original, and have the copy editor restore losses.

    In each round, `CHECK_PANEL` separate runs of `checker` read the request
    `text` with the edits in `current`, and each lists what each edit lost.
    Where any of them lists anything, `editor` gets a restore read
    (`restore_request`) with every finding, and its rewrites update `current`
    and join `replies` under a name in `names`. The checks then run again, up
    to `MAX_CHECK_ROUNDS` rounds. A passage in `limited` gets at most
    `LIMITED_CHECK_ROUNDS` rounds: what the last of them finds lost stays
    lost, and later rounds and restore reads leave it alone. For each restore
    read, the passages that it may not rewrite join `skipped`. Each run's
    counts join `counts`. Returns what the last round found still lost, by
    passage, and every check's label and reply. A check whose reply cannot be
    read counts as finding every edited passage lost, because nothing then
    shows that the edit kept the original's meaning. A restore read whose
    reply cannot be read changes nothing.
    """
    count = passage_count(text)
    checks: list[tuple[str, str]] = []
    lost: dict[int, str] = {}
    settled: dict[int, str] = {}
    done = limited if MAX_CHECK_ROUNDS > LIMITED_CHECK_ROUNDS else frozenset()
    for index in range(1, MAX_CHECK_ROUNDS + 1):
        closed = limited if index > LIMITED_CHECK_ROUNDS else frozenset()
        asked = edited_request(text, current, MEANING_CHECK)
        found: dict[int, list[str]] = {}
        for reader in range(1, CHECK_PANEL + 1):
            label = f"meaning check {index}" + (f", reader {reader}" if reader > 1 else "")
            name = f"meaning-{index}" + (f"-{reader}" if reader > 1 else "")
            reply, reply_counts = checker.read(asked, name, reads)
            counts.append(f"{label}: {reply_counts.removeprefix('copy_edit: ')}")
            try:
                findings = meaning_findings(reply, count)
            except ValueError as error:
                counts.append(f"{label}: reply unreadable ({error})")
                reason = f"The reply of {label} could not be read ({error})."
                return {number: reason for number in current}, checks
            checks.append((label, reply))
            for number in sorted(findings):
                if number in current and number not in closed:
                    found.setdefault(number, []).append(findings[number])
        lost = {number: "\n\n".join(found[number]) for number in sorted(found)}
        if index == LIMITED_CHECK_ROUNDS:
            settled = {number: why for number, why in lost.items() if number in done}
            lost = {number: why for number, why in lost.items() if number not in done}
        if not lost or index == MAX_CHECK_ROUNDS:
            break
        name = f"restore {index}"
        restore, restore_counts = editor.read(
            restore_request(text, current, lost), f"restore-{index}", reads
        )
        counts.append(f"{name} read: {restore_counts.removeprefix('copy_edit: ')}")
        try:
            verdicts(restore, count)
            made = rewrites(restore)
        except ValueError as error:
            counts.append(f"{name} read: reply unreadable, so it was left out ({error})")
            break
        late = limited if index >= LIMITED_CHECK_ROUNDS else frozenset()
        replies.append(restore)
        names.append(name)
        if skipped is not None:
            skipped.append(late)
        current.update({number: rows for number, rows in made.items() if number not in late})
    return dict(sorted({**lost, **settled}.items())), checks


def run(
    request: Path,
    root: Path = ROOT,
    env: Mapping[str, str] | None = None,
    reads: Path | None = None,
) -> tuple[str, str]:
    """Run the copy editor on the file at `request`, and return its reply and the counts."""
    return edit(request.read_text(encoding="utf-8"), editor(root, env), checker(root, env), reads)


def where(path: str, part: Part) -> str:
    """The file, section and rows of `part`, as a heading line of the printed reply."""
    section = f' § "{part.title}"' if part.title else ""
    return f"{path}{section}, rows {part.first}-{part.last}"


def structure(
    path: str, root: Path = ROOT, env: Mapping[str, str] | None = None, reads: Path | None = None
) -> tuple[str, str]:
    """A document's structure read, the first part of its review, with the counts.

    A short document is read once, whole. A longer one is split into chapters
    (`new_prose.chapters`) and read a chapter at a time. A last read then takes
    every chapter's reverse outline and finds what crosses chapters. Raises
    `Refused` where a read rewrites a row, or a chapter read gives no outline.
    """
    try:
        pieces = structure_reports(root, path, rule_table())
    except ValueError as error:
        raise Refused(str(error)) from error
    reader = editor(root, env)
    replies: list[tuple[Part, str]] = []
    counts: list[str] = []
    for index, (part, request) in enumerate(pieces, start=1):
        reply, count = reader.read(with_rule(request), f"chapter-{index:02}", reads)
        if rewrites(reply):
            raise Refused(f"the structure read of {where(path, part)} rewrote rows")
        replies.append((part, reply))
        counts.append(count.removeprefix("copy_edit: "))
    if len(pieces) == 1:
        return replies[0][1], f"copy_edit: {counts[0]}"
    outlines = []
    for part, reply in replies:
        outline = reply.partition("\nOutline:")[2]
        if not outline.strip():
            raise Refused(f"the structure read of {where(path, part)} gave no outline")
        outlines.append((part, unmarked(outline)))
    whole, count = reader.read(
        with_rule(outline_report(path, rule_table(), outlines)), "outline", reads
    )
    counts.append(count.removeprefix("copy_edit: "))
    out = [f"Structure read of {path} in {len(pieces)} chapters.", ""]
    for index, (part, reply) in enumerate(replies, start=1):
        out += [f"Chapter {index} of {len(pieces)}: {where(path, part)}", "", unmarked(reply), ""]
    out += ["The whole document:", "", unmarked(whole)]
    return "\n".join(out), "copy_edit: " + "; ".join(counts)


def sections(
    path: str, root: Path = ROOT, env: Mapping[str, str] | None = None, reads: Path | None = None
) -> tuple[str, str]:
    """The second part of a document's review, each section line-edited alone, with the counts.

    Each section is its own request, edited and audited like any other (`edit`).
    Its reply follows a line that names the section and its rows.
    """
    try:
        parts = part_reports(root, path, rule_table())
    except ValueError as error:
        raise Refused(str(error)) from error
    reader = editor(root, env)
    check = checker(root, env)
    out: list[str] = []
    counts: list[str] = []
    for index, (part, request) in enumerate(parts, start=1):
        kept = None if reads is None else reads / f"section-{index:03}"
        reply, count = edit(with_rule(request), reader, check, kept)
        out += [f"Section {index} of {len(parts)}: {where(path, part)}", "", reply, ""]
        counts.append(count.removeprefix("copy_edit: "))
    return "\n".join(out).rstrip("\n"), "copy_edit: " + "; ".join(counts)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.partition("\n")[0])
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("request", type=Path, nargs="?", help="the file tools/new_prose.py wrote")
    modes.add_argument(
        "--structure",
        metavar="FILE",
        help="the first part of a document's review: read the Markdown file FILE for its "
        "structure, and rewrite nothing",
    )
    modes.add_argument(
        "--sections",
        metavar="FILE",
        help="the second part: line-edit each section of the Markdown file FILE alone",
    )
    parser.add_argument(
        "--reads", type=Path, help="a directory to write each read's request and reply into"
    )
    args = parser.parse_args(argv)
    try:
        if args.structure is not None:
            reply, counts = structure(args.structure, reads=args.reads)
        elif args.sections is not None:
            reply, counts = sections(args.sections, reads=args.reads)
        else:
            reply, counts = run(args.request, reads=args.reads)
    except (Refused, OSError) as error:
        print(f"copy_edit: no reply: {error}", file=sys.stderr)
        return 1
    print(reply)
    print(counts, file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
