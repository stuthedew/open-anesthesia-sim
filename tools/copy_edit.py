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

The copy editor reads each request twice, as experienced technical editors
do (project owner, 2026-11-04, ratified, `PL-HGZS`). When the first read
rewrites a passage, a second run gets the same request with each rewritten
passage replaced by its edit, under the line `SECOND_READ`, and fixes what the
first read missed or introduced. The printed reply gives each passage once:
the second read's text where it rewrote the passage, else the first read's,
else `[N] keep`. Both reads' notes follow. When the first read rewrites
nothing, there is no second read.

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
import json
import os
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Mapping, Sequence
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "subprojects" / "docket" / "src"))

from docket.config import load as load_config  # noqa: E402
from docket.lines import split_lines  # noqa: E402
from docket.markdown import FENCE  # noqa: E402
from docket.markdown import read as read_markdown  # noqa: E402
from docket.model import FRONT_MATTER_RE  # noqa: E402

from new_prose import (  # noqa: E402
    PROMPT,
    RULE_END,
    passage_number,
    read_row,
    read_span,
    respan,
    row_line,
)
from rejected_prose import rewrites, unmarked, verdicts  # noqa: E402

#: The role `docket.toml`'s `[models]` table is asked about.
ROLE = "copy-editor"
#: The name the request takes inside the copy editor's empty directory.
REQUEST_NAME = "request.txt"
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
SECOND_READ = (
    "Second read. The rows marked > are the text after one copy edit. The text "
    "before that edit is not shown, and each header's word counts are the "
    "counts before it."
)


class Refused(Exception):
    """The copy editor could not be run, or did not reply, with the reason."""


def instructions(prompt: str) -> str:
    """The copy editor's instructions: the agent file's text without its front matter."""
    match = FRONT_MATTER_RE.match(prompt)
    if match is None:
        raise Refused(f"{PROMPT} has no front matter, so its instructions cannot be found")
    return match.group(2).lstrip("\n")


def claude_argv(claude: str, system_prompt: Path, model: str, effort: str) -> list[str]:
    """The `claude -p` command that runs the copy editor on `REQUEST_NAME`."""
    return [
        claude,
        "-p",
        f"Copy-edit the passages in {REQUEST_NAME}.",
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


def second_request(request: str, blocks: Mapping[int, Sequence[str]]) -> str:
    """The request for the second read: `request` with each passage in `blocks` edited.

    `blocks` maps a passage's number to the rows the first read gave it. The
    passage's rows marked `>` give way to those rows, numbered from the first
    of them. Each row, header and section title after them in the same listing
    is renumbered to follow. `SECOND_READ` opens the prose. Raises `Refused`
    where a passage in `blocks` has no rows marked `>`.
    """
    head, lines = prose_of(request)
    out: list[str] = []
    shift = 0
    waiting: int | None = None
    placed: set[int] = set()
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
            end = index
            while end < len(lines) and (later := read_row(lines[end])) and later[1] == ">":
                end += 1
            block = blocks[waiting]
            out += [row_line(row[0] + shift + k, ">", text) for k, text in enumerate(block)]
            shift += len(block) - (end - index)
            placed.add(waiting)
            waiting = None
            index = end
            continue
        else:
            out.append(row_line(row[0] + shift, *row[1:]) if shift else line)
        index += 1
    missing = sorted(set(blocks) - placed)
    if missing:
        raise Refused(f"passages {missing} have no rows marked > to replace")
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


def merge(first: str, second: str, count: int) -> str:
    """One reply from the two reads' replies, `first` and `second`, for `count` passages.

    Each passage gets one verdict: the second read's text where it rewrote the
    passage, else the first read's text, else `[N] keep`. The notes of both
    reads follow, so that every cut, move and query either read made is kept.
    Raises `Refused` where either reply does not give each passage one verdict,
    or a rewrite has no text.
    """
    found: list[dict[int, tuple[str, ...]]] = []
    for name, reply in (("first", first), ("second", second)):
        try:
            verdicts(reply, count)
            found.append(rewrites(reply))
        except ValueError as error:
            raise Refused(f"the {name} read's reply cannot be read: {error}") from error
    once, twice = found
    out: list[str] = []
    for number in range(1, count + 1):
        rows = twice.get(number, once.get(number))
        if rows is None:
            out += [f"[{number}] keep", ""]
        else:
            out += [f"[{number}] rewrite", "", *fenced(rows), ""]
    out += ["Notes from the first read:", "", notes(first), ""]
    out += ["Notes from the second read:", "", notes(second)]
    reply = "\n".join(out)
    try:
        verdicts(reply, count)
    except ValueError as error:
        raise Refused(f"the two reads' notes left a verdict mark: {error}") from error
    return reply


def read_once(
    text: str, claude: str, prompt: str, model: str, effort: str, env: Mapping[str, str]
) -> tuple[str, str]:
    """One run of the copy editor on the request `text`: its reply and its counts."""
    with tempfile.TemporaryDirectory() as held, tempfile.TemporaryDirectory() as work:
        system_prompt = Path(held) / "copy-editor.md"
        system_prompt.write_text(prompt, encoding="utf-8")
        (Path(work) / REQUEST_NAME).write_text(text, encoding="utf-8")
        try:
            done = subprocess.run(
                claude_argv(claude, system_prompt, model, effort),
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


def run(
    request: Path,
    root: Path = ROOT,
    env: Mapping[str, str] | None = None,
    reads: Path | None = None,
) -> tuple[str, str]:
    """Run the copy editor twice on the file at `request`, and return its reply and the counts.

    Where `reads` names a directory, each read's request and reply are also
    written there, so that what the second read changed can be judged alone.
    """
    claude = shutil.which("claude")
    if claude is None:
        raise Refused("no `claude` on PATH")
    table = load_config(root).models
    if table is None:
        raise Refused(f"{root / 'docket.toml'} has no [models] table, so no model is chosen")
    choice = table.choose({"role": ROLE})
    prompt = instructions(PROMPT.read_text(encoding="utf-8"))
    environment = os.environ if env is None else env
    text = request.read_text(encoding="utf-8")

    def once(name: str, asked: str) -> tuple[str, str]:
        reply, counts = read_once(asked, claude, prompt, choice.model, choice.effort, environment)
        if reads is not None:
            reads.mkdir(parents=True, exist_ok=True)
            (reads / f"{name}-request.txt").write_text(asked, encoding="utf-8")
            (reads / f"{name}-reply.txt").write_text(reply, encoding="utf-8")
        return reply, counts

    first, first_counts = once("first", text)
    try:
        blocks = rewrites(first)
    except ValueError as error:
        raise Refused(f"the first read's reply cannot be read: {error}") from error
    if not blocks:
        return first, first_counts
    count = passage_count(text)
    second, second_counts = once("second", second_request(text, blocks))
    both = f"{first_counts}; second read: {second_counts.removeprefix('copy_edit: ')}"
    return merge(first, second, count), both


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.partition("\n")[0])
    parser.add_argument("request", type=Path, help="the file tools/new_prose.py wrote")
    parser.add_argument(
        "--reads", type=Path, help="a directory to write each read's request and reply into"
    )
    args = parser.parse_args(argv)
    try:
        reply, counts = run(args.request, reads=args.reads)
    except (Refused, OSError) as error:
        print(f"copy_edit: no reply: {error}", file=sys.stderr)
        return 1
    print(reply)
    print(counts, file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
