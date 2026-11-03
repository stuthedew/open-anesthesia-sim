"""Show, record and check the prose review's test set: paragraphs the owner rejected.

Close-out step 8 in `.claude/skills/docket/modes/close-out.md` gives a fresh
reviewer the prompt in `docs/prose-review/prompt.md` and each long paragraph a
branch changed in the simulator, and the reviewer judges each one for its named
reader. The owner is the only clinician who reads this project's prose. When the
owner rejects a paragraph that the review passed, the paragraph becomes an entry
in `docs/prose-review/rejected/`. Each change to the prompt is then run on the
set, and it must flag every entry, so the review cannot pass again a kind of text
the owner has already turned down (`PL-FYGJ`, from `PL-H76S`'s design round).

**An entry** is one Markdown file named `KIND-DATE-SLUG.md`. Its front matter
gives `kind`, one of `FAILURE_KINDS`; `file`, the document the paragraph came
from, which decides its readers through the table in
`.claude/rules/plain-writing.md`; and `rejected`, the date of the owner's
rejection. Its body has three sections and may have a fourth, as
`REQUIRED_SECTIONS` and `OPTIONAL_SECTIONS` name them. The paragraph sits in a
fenced block, exactly as it stood in its file. It must read as one unit of
`MIN_WORDS` words or more, as `tools/new_prose.py` reads that file, because the
review never sees a shorter unit. A shorter rejected paragraph is a miss of
that word limit rather than of the prompt, so it belongs in an item.

**How the set stays small.** Only a miss is added: a paragraph that the review
passed and the owner then rejected. A kind holds at most `CAP_PER_KIND` entries.
A new miss of a full kind replaces the oldest entry, and git history keeps the
one replaced. If the review flags all 59 entries of a kind, the chance that it
misses a paragraph of that kind is below 5%, at 95% confidence. The bound after
no misses in n tries is 1 - 0.05^(1/n) (Hanley JA, Lippman-Hand A. If nothing
goes wrong, is everything all right? Interpreting zero numerators. JAMA.
1983;249(13):1743-1745). It treats the entries as independent, so it is a best
case. The owner set the cap (project owner, 2026-11-03).

Three commands:

- `show` prints what the reviewer is given. First comes the prompt, then the
  readers of each entry's file, then each entry's paragraph as a numbered unit
  in `tools/new_prose.py`'s format, with every row marked `>`. It prints the
  paragraph without its kind or the owner's words, so the reviewer judges it as
  it would any branch's prose. Unlike a real review, no lines of the file
  around the paragraph are shown, because the entry does not keep them.
- `record REPLY` reads the reviewer's whole reply from the file REPLY and finds
  its "[N] keep" or "[N] rewrite" verdict for each entry. It writes one record
  to `docs/prose-review/runs/`, holding the reply, the entries in the order
  `show` numbered them, and a SHA-256 hash of the prompt and of each entry
  file's rows in the reader table. It refuses a reply that gives an entry no
  verdict, or two different ones, so a reply cut short is never recorded. This
  tool is the only writer of those records.
- `check` exits 1 when an entry does not parse, names a kind that
  `FAILURE_KINDS` does not hold, or names a file that no row of the reader table
  names; when a kind holds more than `CAP_PER_KIND` entries; and when the
  current prompt and readers have no run, or have a run that kept an entry.
  `make check` and CI run it.

**What a run covers.** The prompt and the readers' rows are what tell the
reviewer what to look for, so a change to either needs a new run. A new entry
needs none, because only a miss is added, and the next change to the prompt
must flag it. A new row for a file that no run read needs none either. Every
run of the current prompt and readers must have flagged every entry it read. So
a miss stays on record, and running the same prompt again until it passes does
not clear it: the prompt has to change.

Standard library only, like every tool under `tools/`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import textwrap
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "subprojects" / "docket" / "src"))

from docket.lines import split_lines  # noqa: E402
from docket.markdown import FENCE, headings  # noqa: E402
from docket.markdown import read as read_markdown  # noqa: E402
from docket.model import parse_front_matter  # noqa: E402
from docket.python import UNTOKENIZABLE, refusal  # noqa: E402

import new_prose  # noqa: E402
from new_prose import MIN_WORDS, Reader, Unit, excerpt, reader_lines, readers_of  # noqa: E402

#: Each kind of failure an entry can record, with what it means. A miss that
#: fits none of them adds a kind here, with its meaning.
FAILURE_KINDS: Mapping[str, str] = {
    "jargon": "a word, symbol or number that the paragraph's reader does not know",
    "length": (
        "more than the reader needs here, such as history that belongs in the item, "
        "or numerical detail that belongs in a note for developers"
    ),
    "unusable-reason": (
        "a reason for a chosen value that the reader cannot act on, because it does not "
        "say what the value does or what changing it would do"
    ),
    "unsourced-reason": (
        "a reason for a chosen value, or a claim that none was recorded, that no record supports"
    ),
}
#: The most entries one kind may hold. The owner set it on 2026-11-03.
CAP_PER_KIND = 59

#: Where the entries and the records of each run live.
REJECTED_DIR = ROOT / "docs" / "prose-review" / "rejected"
RUNS_DIR = ROOT / "docs" / "prose-review" / "runs"

#: The front-matter keys an entry must have, and no others.
ENTRY_KEYS = ("kind", "file", "rejected")
#: The sections an entry's body must have, in this order.
REQUIRED_SECTIONS = ("Paragraph", "The owner's words", "Where it came from")
#: The section an entry may add after them, once the owner accepts a rewrite.
OPTIONAL_SECTIONS = ("Accepted rewrite",)
#: The fields of a run's record.
RUN_KEYS = ("recorded", "prompt", "readers", "entries", "reply")

#: One verdict in the reviewer's reply, as the prompt asks for it. Emphasis and
#: code marks are removed from a line before it is matched.
VERDICT_RE = re.compile(r"\[(\d+)\]\s*(keep|rewrite)\b", re.IGNORECASE)


@dataclass(frozen=True)
class Entry:
    """One paragraph the owner rejected, as its file in `REJECTED_DIR` records it."""

    name: str
    kind: str
    file: str
    rejected: date
    #: The paragraph exactly as it stood in `file`, one string per line.
    lines: tuple[str, ...]
    unit: Unit


@dataclass(frozen=True)
class Run:
    """One run of the review on the set, as `record` wrote it."""

    name: str
    prompt: str
    #: Each file the run's entries came from, with the hash of its readers' rows.
    readers: Mapping[str, str]
    entries: tuple[str, ...]
    reply: str


def digest(text: str) -> str:
    """The SHA-256 hash of `text`, in hexadecimal."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def readers_digest(table: Sequence[Reader], path: str) -> str:
    """The hash of every field of each row of `table` that names the file at `path`."""
    rows = [
        [list(reader.paths), reader.who, reader.knows, reader.does_not_know, reader.will_do]
        for reader in readers_of(table, path)
    ]
    return digest(json.dumps(rows))


def _sections(body: list[str]) -> dict[str, tuple[int, int]]:
    """Each second-level heading's title in `body`, with the lines its section spans.

    Raises `ValueError` for a heading of another level, a title written twice,
    and a line other than a blank one above the first heading.
    """
    found: dict[str, tuple[int, int]] = {}
    marks = headings(body)
    if any(line.strip() for line in body[: marks[0].line if marks else len(body)]):
        raise ValueError("text stands above the first section")
    for index, heading in enumerate(marks):
        if heading.level != 2:
            raise ValueError(f"heading {heading.title!r} is not a second-level heading")
        if heading.title in found:
            raise ValueError(f"section {heading.title!r} is written twice")
        end = marks[index + 1].line if index + 1 < len(marks) else len(body)
        found[heading.title] = (heading.end, end)
    return found


def _paragraph(body: list[str], span: tuple[int, int]) -> tuple[str, ...]:
    """The lines of the one closed fenced block that the section at `span` holds."""
    blocks = [block for block in read_markdown(body).blocks if span[0] <= block.start < span[1]]
    if len(blocks) != 1 or blocks[0].kind != FENCE or not blocks[0].closing:
        raise ValueError("the Paragraph section must hold one closed fenced block and nothing else")
    return tuple(body[blocks[0].start + 1 : blocks[0].end - 1])


def _unit(path: str, lines: Sequence[str]) -> Unit:
    """The paragraph `lines` as `tools/new_prose.py` reads a unit of the file at `path`.

    A Python paragraph is read with its common indent removed, since a function's
    docstring stands indented in its file.
    """
    source = "\n".join(lines) + "\n"
    if path not in new_prose.DOCUMENTS:
        source = textwrap.dedent(source)
    try:
        units = new_prose.units_of(path, source)
    except UNTOKENIZABLE as error:
        raise ValueError(
            f"the paragraph does not parse as {path} would: {refusal(error)}"
        ) from None
    if len(units) != 1:
        raise ValueError(f"the paragraph reads as {len(units)} units of {path}, not one")
    if units[0].words < MIN_WORDS:
        raise ValueError(
            f"the paragraph has {units[0].words} words, and the review reads only units of "
            f"{MIN_WORDS} or more"
        )
    return Unit(path, units[0].kind, 1, len(lines), units[0].text)


def parse_entry(name: str, text: str, table: Sequence[Reader]) -> Entry:
    """The entry that the file called `name` records in `text`.

    Raises `ValueError` saying what is wrong with it.
    """
    fields, body_text, declined = parse_front_matter(text)
    if declined:
        raise ValueError(f"its front matter has {declined}")
    if tuple(sorted(fields)) != tuple(sorted(ENTRY_KEYS)):
        raise ValueError(f"its front matter must have exactly {', '.join(ENTRY_KEYS)}")
    kind, path = fields["kind"], fields["file"]
    if kind not in FAILURE_KINDS:
        raise ValueError(f"kind {kind!r} is not one of {', '.join(FAILURE_KINDS)}")
    try:
        rejected = date.fromisoformat(fields["rejected"])
    except ValueError:
        raise ValueError(
            f"rejected {fields['rejected']!r} is not a date written YYYY-MM-DD"
        ) from None
    if not name.startswith(f"{kind}-{rejected.isoformat()}-") or not name.endswith(".md"):
        raise ValueError(f"its name must be {kind}-{rejected.isoformat()}-SLUG.md")
    if not readers_of(table, path):
        raise ValueError(f"no row of the reader table names {path}")
    body = split_lines(body_text)
    sections = _sections(body)
    titles = tuple(sections)
    if titles not in (REQUIRED_SECTIONS, REQUIRED_SECTIONS + OPTIONAL_SECTIONS):
        raise ValueError(
            f"its sections are {', '.join(titles) or 'none'}, and must be "
            f"{', '.join(REQUIRED_SECTIONS)}, then optionally {', '.join(OPTIONAL_SECTIONS)}"
        )
    for title, (start, end) in sections.items():
        if not any(line.strip() for line in body[start:end]):
            raise ValueError(f"section {title!r} is empty")
    lines = _paragraph(body, sections["Paragraph"])
    return Entry(name, kind, path, rejected, lines, _unit(path, lines))


def read_entries(directory: Path, table: Sequence[Reader]) -> tuple[list[Entry], list[str]]:
    """Every entry in `directory`, sorted by name, and a line for each file that is not one."""
    entries: list[Entry] = []
    problems: list[str] = []
    for path in sorted(directory.glob("*.md")):
        try:
            entries.append(parse_entry(path.name, path.read_text(encoding="utf-8"), table))
        except ValueError as error:
            problems.append(f"{path.name}: {error}")
    return entries, problems


def show(prompt: str, entries: Sequence[Entry], table: Sequence[Reader]) -> str:
    """What the reviewer is given: the prompt, the readers, then each entry as a numbered unit."""
    out = [
        prompt.rstrip("\n"),
        "",
        f"{len(entries)} document paragraphs of {MIN_WORDS} words or more. Rows marked > are "
        "the unit. Judge each unit for the readers its header names, as the list below "
        "describes them.",
    ]
    out += reader_lines(table, (entry.file for entry in entries))
    for number, entry in enumerate(entries, start=1):
        out += new_prose.unit_lines(number, entry.unit, excerpt(entry.lines, entry.unit), table)
    return "\n".join(out)


def verdicts(reply: str, count: int) -> list[str]:
    """The verdict `reply` gives each of `count` units, "keep" or "rewrite", in order.

    Raises `ValueError` where a unit has no verdict or two different ones, or a
    verdict numbers a unit that was not shown.
    """
    found: dict[int, set[str]] = {}
    for line in split_lines(reply):
        for match in VERDICT_RE.finditer(re.sub(r"[*_`]", "", line)):
            found.setdefault(int(match.group(1)), set()).add(match.group(2).lower())
    problems = [f"[{number}] was not shown" for number in sorted(found) if not 1 <= number <= count]
    for number in range(1, count + 1):
        given = found.get(number, set())
        if len(given) != 1:
            problems.append(f"[{number}] has {' and '.join(sorted(given)) or 'no verdict'}")
    if problems:
        raise ValueError("; ".join(problems))
    return [found[number].pop() for number in range(1, count + 1)]


def record(
    prompt: str, entries: Sequence[Entry], table: Sequence[Reader], reply: str, now: datetime
) -> dict[str, object]:
    """The record of one run, after checking that `reply` gives every entry a verdict."""
    verdicts(reply, len(entries))
    return {
        "recorded": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "prompt": digest(prompt),
        "readers": {
            path: readers_digest(table, path) for path in sorted({e.file for e in entries})
        },
        "entries": [entry.name for entry in entries],
        "reply": reply,
    }


def parse_run(name: str, text: str) -> Run:
    """The run that the record called `name` holds in `text`.

    Raises `ValueError` saying what is wrong with it.
    """
    try:
        data = json.loads(text)
    except json.JSONDecodeError as error:
        raise ValueError(f"it is not JSON: {error}") from None
    if not isinstance(data, dict) or tuple(sorted(data)) != tuple(sorted(RUN_KEYS)):
        raise ValueError(f"it must be an object holding exactly {', '.join(RUN_KEYS)}")
    readers, entries = data["readers"], data["entries"]
    if not isinstance(data["prompt"], str) or not isinstance(data["reply"], str):
        raise ValueError("its prompt and reply must be strings")
    if not isinstance(readers, dict) or not all(isinstance(v, str) for v in readers.values()):
        raise ValueError("its readers must map each file to a string")
    if not isinstance(entries, list) or not all(isinstance(e, str) for e in entries):
        raise ValueError("its entries must be a list of file names")
    return Run(name, data["prompt"], readers, tuple(entries), data["reply"])


def check(root: Path, prompt: str, table: Sequence[Reader]) -> list[str]:
    """Each reason the set or its runs fail, or none."""
    entries, problems = read_entries(root / REJECTED_DIR.relative_to(ROOT), table)
    held = Counter(entry.kind for entry in entries)
    for kind, count in sorted(held.items()):
        if count > CAP_PER_KIND:
            oldest = min((e for e in entries if e.kind == kind), key=lambda e: (e.rejected, e.name))
            problems.append(
                f"kind {kind} holds {count} entries, more than {CAP_PER_KIND}: delete the "
                f"oldest, {oldest.name}, which git history keeps"
            )
    runs: list[Run] = []
    runs_dir = root / RUNS_DIR.relative_to(ROOT)
    for path in sorted(runs_dir.glob("*.json")) if runs_dir.is_dir() else []:
        try:
            runs.append(parse_run(path.name, path.read_text(encoding="utf-8")))
        except ValueError as error:
            problems.append(f"runs/{path.name}: {error}")
    current = [
        run
        for run in runs
        if run.prompt == digest(prompt)
        and all(readers_digest(table, path) == value for path, value in run.readers.items())
    ]
    if entries and not current:
        problems.append(
            "no run of the set used the current prompt and readers: run `show`, give its whole "
            "output to one fresh general-purpose reviewer, save the reply, and run `record` on it"
        )
    for run in current:
        try:
            given = verdicts(run.reply, len(run.entries))
        except ValueError as error:
            problems.append(f"runs/{run.name}: {error}")
            continue
        for name, verdict in zip(run.entries, given, strict=True):
            if verdict != "rewrite":
                problems.append(
                    f"runs/{run.name} kept {name}: change the prompt so the review flags it, "
                    "then run the set again"
                )
    return problems


def main(argv: Sequence[str] | None = None, *, root: Path = ROOT) -> int:
    parser = argparse.ArgumentParser(description=__doc__.partition("\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("show", help="print what the reviewer is given")
    recording = commands.add_parser("record", help="record the reviewer's reply as a run")
    recording.add_argument("reply", type=Path, help="file holding the reviewer's whole reply")
    commands.add_parser(
        "check", help="fail on a bad entry, a full kind, or a missing or failed run"
    )
    args = parser.parse_args(argv)
    table = new_prose.reader_table(new_prose.RULE.read_text(encoding="utf-8"))
    prompt = new_prose.PROMPT.read_text(encoding="utf-8")
    if args.command == "check":
        problems = check(root, prompt, table)
        for problem in problems:
            print(f"rejected_prose: {problem}", file=sys.stderr)
        if not problems:
            print("rejected_prose: every run of the current prompt flagged every entry it read")
        return 1 if problems else 0
    entries, problems = read_entries(root / REJECTED_DIR.relative_to(ROOT), table)
    for problem in problems:
        print(f"rejected_prose: {problem}", file=sys.stderr)
    if problems:
        return 1
    if args.command == "show":
        print(show(prompt, entries, table))
        return 0
    reply = args.reply.read_text(encoding="utf-8")
    try:
        given = verdicts(reply, len(entries))
    except ValueError as error:
        print(f"rejected_prose: not recorded: {error}", file=sys.stderr)
        return 1
    now = datetime.now(UTC)
    runs_dir = root / RUNS_DIR.relative_to(ROOT)
    runs_dir.mkdir(parents=True, exist_ok=True)
    path = runs_dir / f"{now.strftime('%Y-%m-%dT%H%M%SZ')}.json"
    run = record(prompt, entries, table, reply, now)
    path.write_text(json.dumps(run, indent=2) + "\n", encoding="utf-8")
    print(f"rejected_prose: recorded {path.relative_to(root)}")
    for entry, verdict in zip(entries, given, strict=True):
        if verdict == "keep":
            print(
                f"rejected_prose: the review kept {entry.name}: change the prompt, then run again"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
