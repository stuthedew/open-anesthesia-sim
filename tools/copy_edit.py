"""Run the copy editor on one file that `tools/new_prose.py` wrote, and print its reply.

Close-out step 8, the pull-request skill and reply rule 16 in
`.claude/rules/instruction-writing.md` hand the copy editor a file of passages.
The copy editor's instructions are the body of `.claude/agents/copy-editor.md`,
which is their one home. A Projects thread cannot start that agent, because a
thread does not load `.claude/agents/`. The fallback, a general-purpose agent
given the agent file's text, loads every resident instruction that the copy
editor is meant to run without (`PL-TQ4J`).

So this tool runs the copy editor as its own `claude -p` process, the same
way in every kind of session. The process starts in an empty directory that
holds only the request, so no `CLAUDE.md` or rule is found and loaded. Run
inside the repository, even `claude -p --agent copy-editor` loads the resident
instructions. Its system prompt is the agent file's body, its one tool is Read,
and it loads no settings file.

The copy editor reads each request at least twice, as experienced technical
editors do (project owner, 2026-11-04, ratified, `PL-HGZS`). When the first
read rewrites a passage, a fresh run audits the edit: it gets the same request
with each rewritten passage replaced by its edit, under the line
`SECOND_READ`, and fixes what the earlier reads missed or introduced. Audits
go on until one changes nothing, up to `MAX_READS` reads in all (project
owner, 2026-11-05, ratified, over exactly two reads). The printed reply gives
each passage once, in the text of the last read that rewrote it, else
`[N] keep`. Every read's notes follow. When the first read rewrites nothing,
there is no audit.

Before the reply is printed, `check_code` compares each rewrite with the rows
it replaces. A rewrite that changes code, a fenced block, an HTML comment or a
heading, or writes a code name the passage does not hold, is refused and
printed as `[N] keep`, with the reason under "Code check:". A code name that a
rewrite dropped is listed there too (project owner, 2026-11-04, `PL-HGZS`).

**A whole document is reviewed in two parts** (project owner, 2026-11-04,
`PL-HGZS`). `--structure FILE` runs the structure read, which rewrites
nothing: one read of a short document, or one read per chapter of a long one
and then one read of all the chapters' outlines. `--sections FILE` then
line-edits each section alone, each with its two reads. `tools/new_prose.py`
builds every one of those requests.

The model and effort are the ones `docket.toml`'s `[models]` table chooses
for the role `copy-editor`. The runs are billed to the account that `claude`
signs in with, as an Agent call would be.

Prints the reply on standard output and one line of counts on standard
error. Exits 0 when the copy editor replied, and 1 with the reason when
`claude` is missing, fails, times out or returns an error, or when a read's
reply does not give each passage one verdict.
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

from new_prose import (  # noqa: E402
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
#: A read that takes longer than this is stopped, and each of the two reads
#: has its own limit. The longest copy edit measured so far read 29 passages
#: in about 15 minutes (`PL-22T5`), so 40 minutes leaves room for a larger
#: branch while still ending a run that has stalled.
COPY_EDIT_TIMEOUT_S = 40 * 60
#: Turns off the memory index that a session would otherwise load, so the
#: copy editor's context is its instructions and the request alone.
QUIET_ENV = {"CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1"}
#: The line that opens the prose of a second read's request. The copy editor's
#: instructions say what to do with a request that holds it.
#: The heading under which a second read's request gives each edited passage
#: as it stood before the first read, so that a fact the first read lost or
#: changed can be found. One edit read alone cannot show that (`PL-HGZS`).
BEFORE = "Before the first edit"
SECOND_READ = (
    "Second read. The rows marked > are the text after the earlier copy edits, and "
    "each header's word counts are the counts before them. The text before the "
    f'first edit follows the passages, under "{BEFORE}".'
)


#: The most reads one request gets: the first edit and the audits after it.
#: An audit runs again while the last one changed a passage, because Hart's
#: experienced technical editors make "at least two passes" ("Interview
#: responses: The editing practices of professional technical editors", 2010,
#: https://geoff-hart.com/articles/2010/interview.htm). Runs 16 to 18 of
#: section 1 each left one or two faults after two reads. Four reads bounds
#: the cost of a passage that never settles, at about $1 and 10 minutes for
#: each read of a 1,200-word section; raising it lets such a passage run longer.
MAX_READS = 4
#: The name of each read, by its place, for its files and its notes.
READ_NAMES = ("first", "second", "third", "fourth")


class Refused(Exception):
    """The copy editor could not be run, or did not reply, with the reason."""


def instructions(prompt: str) -> str:
    """The copy editor's instructions: the agent file's text without its front matter."""
    match = FRONT_MATTER_RE.match(prompt)
    if match is None:
        raise Refused(f"{PROMPT} has no front matter, so its instructions cannot be found")
    return match.group(2).lstrip("\n")


def claude_argv(
    claude: str, system_prompt: Path, model: str, effort: str, task: str = TASK
) -> list[str]:
    """The `claude -p` command that does `task` with `REQUEST_NAME`, by default a copy edit."""
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
    """`request` up to and including its `RULE_END` line, and the lines after it.

    Raises `Refused` where the request has no `RULE_END` line.
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
    """The request for the second read: `request` with each passage in `blocks` edited.

    `blocks` maps a passage's number to the rows the first read gave it. The
    passage's rows marked `>` give way to those rows, numbered from the first
    of them. Each row, header and section title after them in the same listing
    is renumbered to follow. `SECOND_READ` opens the prose, and after the last
    passage, under `BEFORE`, each edited passage's rows stand as the first read
    was given them. Raises `Refused` where a passage in `blocks` has no rows
    marked `>`.
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
    return f"{head}\n\n{SECOND_READ}" + "\n".join(fitted_titles(out))


def fitted_titles(lines: Sequence[str]) -> list[str]:
    """`lines`, with each section title's last row set to the last row listed under it.

    A title is a line that ends with a colon and holds a span but is no header.
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

    A verdict mark left in the notes would give its passage a second verdict.
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
    """What a rewrite did to code: each change that refuses it, and each code name it dropped.

    The copy editor may change prose and nothing else. Its instructions say so,
    and this check enforces it on what it returns, so that no session applies a
    rewrite that changed code (project owner, 2026-11-04, `PL-HGZS`).
    """

    refused: tuple[str, ...] = ()
    dropped: tuple[str, ...] = ()


#: Python tokens that are prose or layout, which a copy edit may change. Every
#: other token is code and must come back as it was. A string literal is prose
#: here because the units the copy editor edits include docstrings and the
#: string literals a learner reads.
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
# regex: an HTML comment, which a Markdown file uses for its provenance markers
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.S)


def python_code(rows: Sequence[str]) -> list[tuple[int, str]] | list[str]:
    """The code in Python `rows`: its tokens other than prose, or failing that, its code lines.

    An excerpt can start inside an indented block, so it may not tokenize. Then
    the code is each line that holds no quote and no `#`, which is code alone.
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

    `seen` is every row of the passage, the read-only rows included, so a code
    name the copy editor took from any of them is not a new name. A rewrite is
    refused where it changes Python code, a fenced block, an HTML comment or a
    heading, or writes a code name that the passage does not hold.
    """
    refused: list[str] = []
    if path.endswith(".py") and python_code(before) != python_code(after):
        refused.append("it changed code outside the docstrings, comments and strings")
    old_fences, old_comments, old_titles, old_spans = markdown_code(before)
    new_fences, new_comments, new_titles, new_spans = markdown_code(after)
    if not path.endswith(".py"):
        if old_fences != new_fences:
            refused.append("it changed, added or removed a fenced block")
        if old_comments != new_comments:
            refused.append("it changed, added or removed an HTML comment")
        if old_titles != new_titles:
            refused.append("it changed, added or removed a heading")
    # A code name the passage already holds anywhere, inside a longer code
    # span, a source comment or the prose, is one the copy editor took from
    # the text, not one it made up.
    known = " ".join(" ".join(seen).split())
    added = sorted({span for span in new_spans if " ".join(span.split()) not in known})
    if added:
        refused.append(
            "it wrote code names the passage does not hold: "
            + ", ".join(f"`{span}`" for span in added)
        )
    dropped = tuple(sorted({span for span in old_spans if span not in new_spans}))
    return CodeCheck(tuple(refused), dropped)


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
    """A check of one passage's rewrite against the code in `request`'s text of that passage."""
    texts = passage_texts(request)

    def check(number: int, rows: Sequence[str]) -> CodeCheck:
        path, before, seen = texts[number]
        return check_code(path, before, seen, rows)

    return check


def merge(
    replies: Sequence[str],
    count: int,
    check: Callable[[int, Sequence[str]], CodeCheck] | None = None,
) -> str:
    """One reply from every read's reply in `replies`, in order, for `count` passages.

    Each passage gets one verdict: the text of the last read that rewrote it,
    else `[N] keep`. `check`, where given, refuses a rewrite that changed code,
    which then becomes `[N] keep` with the reason under "Code check:", and
    lists each code name a rewrite dropped. The notes of every read follow, so
    that every cut, move and query any read made is kept. Raises `Refused`
    where a reply does not give each passage one verdict, or a rewrite has no
    text.
    """
    found: list[dict[int, tuple[str, ...]]] = []
    for name, reply in zip(READ_NAMES, replies, strict=False):
        try:
            verdicts(reply, count)
            found.append(rewrites(reply))
        except ValueError as error:
            raise Refused(f"the {name} read's reply cannot be read: {error}") from error
    out: list[str] = []
    checked: list[str] = []
    for number in range(1, count + 1):
        rows = next((made[number] for made in reversed(found) if number in made), None)
        result = CodeCheck() if rows is None or check is None else check(number, rows)
        for reason in result.refused:
            checked.append(f"- Passage {number}: the rewrite was refused, because {reason}.")
        for span in result.dropped:
            checked.append(
                f"- Passage {number}: the rewrite no longer names `{span}`. "
                "Check that its reader does not need it."
            )
        if rows is None or result.refused:
            out += [f"[{number}] keep", ""]
        else:
            out += [f"[{number}] rewrite", "", *fenced(rows), ""]
    if checked:
        out += ["Code check:", "", *checked, ""]
    for name, reply in zip(READ_NAMES, replies, strict=False):
        out += [f"Notes from the {name} read:", "", notes(reply), ""]
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
    """One run of `claude -p` on the request `text`: its reply and its counts.

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
    """How to run the copy editor: the `claude` program, its prompt, model and effort."""

    claude: str
    prompt: str
    model: str
    effort: str
    env: Mapping[str, str]

    def read(self, asked: str, name: str, reads: Path | None) -> tuple[str, str]:
        """One read of the request `asked`, kept under `name` in `reads` where it is given."""
        reply, counts = read_once(
            asked, self.claude, self.prompt, self.model, self.effort, self.env
        )
        if reads is not None:
            reads.mkdir(parents=True, exist_ok=True)
            (reads / f"{name}-request.txt").write_text(asked, encoding="utf-8")
            (reads / f"{name}-reply.txt").write_text(reply, encoding="utf-8")
        return reply, counts


def editor(root: Path = ROOT, env: Mapping[str, str] | None = None) -> Editor:
    """The copy editor that `docket.toml` and its agent file set up.

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


def edit(text: str, editor: Editor, reads: Path | None = None) -> tuple[str, str]:
    """Run the copy editor on the request `text` until an audit changes nothing.

    Returns its merged reply and the counts. The first read edits; each later
    read audits the text as the reads before it left it, and runs only while
    the last read changed a passage, up to `MAX_READS`. Where `reads` names a
    directory, each read's request and reply are also written there, so that
    what each audit changed can be judged alone.
    """
    first, first_counts = editor.read(text, READ_NAMES[0], reads)
    try:
        current = dict(rewrites(first))
    except ValueError as error:
        raise Refused(f"the first read's reply cannot be read: {error}") from error
    if not current:
        return first, first_counts
    count = passage_count(text)
    replies = [first]
    counts = [first_counts]
    for name in READ_NAMES[1:MAX_READS]:
        reply, reply_counts = editor.read(second_request(text, current), name, reads)
        replies.append(reply)
        counts.append(f"{name} read: {reply_counts.removeprefix('copy_edit: ')}")
        try:
            made = rewrites(reply)
        except ValueError as error:
            raise Refused(f"the {name} read's reply cannot be read: {error}") from error
        changed = {number: rows for number, rows in made.items() if current.get(number) != rows}
        if not changed:
            break
        current.update(changed)
    return merge(replies, count, code_report(text)), "; ".join(counts)


def run(
    request: Path,
    root: Path = ROOT,
    env: Mapping[str, str] | None = None,
    reads: Path | None = None,
) -> tuple[str, str]:
    """Run the copy editor on the file at `request`, and return its reply and the counts."""
    return edit(request.read_text(encoding="utf-8"), editor(root, env), reads)


def where(path: str, part: Part) -> str:
    """The file, section and rows of `part`, as a heading line of the printed reply."""
    section = f' § "{part.title}"' if part.title else ""
    return f"{path}{section}, rows {part.first}-{part.last}"


def structure(
    path: str, root: Path = ROOT, env: Mapping[str, str] | None = None, reads: Path | None = None
) -> tuple[str, str]:
    """The first part of a document's review: its structure read, and the counts.

    A document `new_prose.chapters` keeps whole is read once. A longer one is
    read a chapter at a time, and each chapter's reverse outline then goes to
    one read of the whole document's outline, which finds what crosses
    chapters. Raises `Refused` where a read rewrites a row, or a chapter read
    gives no outline.
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
    """The second part of a document's review: each section line-edited alone, and the counts.

    Each section is its own request, read as `edit` reads one, with its reply under a line
    that names the section and its rows.
    """
    try:
        parts = part_reports(root, path, rule_table())
    except ValueError as error:
        raise Refused(str(error)) from error
    reader = editor(root, env)
    out: list[str] = []
    counts: list[str] = []
    for index, (part, request) in enumerate(parts, start=1):
        kept = None if reads is None else reads / f"section-{index:03}"
        reply, count = edit(with_rule(request), reader, kept)
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
