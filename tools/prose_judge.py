"""Judge the copy editor's edits blind against their originals, with a separate `claude -p` run.

usage: python3 tools/prose_judge.py OUTDIR REQUEST REPLY [REQUEST REPLY ...] [--seed N]

Each REQUEST is a file that `tools/new_prose.py` wrote, and each REPLY is what
`tools/copy_edit.py` printed for it. Every passage that a reply rewrote becomes
one pair: the rows marked `>` in the request, and the reply's text for them.
The pairs go to the judge in one file, each with its file and its readers.
Within each pair the edit is version A or version B at random, from a seeded
generator, so the judge is never told which version is the original. The
judge's instructions are the body of `.claude/agents/prose-judge.md`, and it
runs the way `tools/copy_edit.py` runs the copy editor: alone, in an empty
directory, with Read as its one tool (`PL-HGZS`).

`docs/prose-review/README.md` § "Judging edits blind" says when to run it and
how to read its result. Writes `request.txt`, `key.json`, `reply.txt` and
`result.json` into OUTDIR. Prints one line for each pair, saying whether the
edit, the original or neither won, and the words in each, then one line of
counts. Exits 0 when every pair has a verdict, and 1 with the reason when the
judge could not be run or left a pair without one.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import re
import shutil
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "subprojects" / "docket" / "src"))

from docket.config import load as load_config  # noqa: E402

import copy_edit  # noqa: E402
from new_prose import passage_number, read_row  # noqa: E402
from rejected_prose import rewrites  # noqa: E402

#: The role `docket.toml`'s `[models]` table is asked about.
ROLE = "prose-judge"
#: The judge's agent definition, whose body is its prompt.
PROMPT = ROOT / ".claude" / "agents" / "prose-judge.md"
#: What the judge is asked to do with the request.
TASK = f"Judge the pairs in {copy_edit.REQUEST_NAME}."
#: The seed for the order of A and B, so that a run can be repeated exactly.
SEED = 20261104
#: The line that opens the readers of one file in a request.
READERS_OF = "Readers of "
#: Deletes the emphasis and code marks a verdict line may carry.
EMPHASIS = str.maketrans("", "", "*_`")
# regex: a verdict line in the judge's free prose, which its instructions ask
# for as "[N] verdict: A", B or same, found anywhere in a line.
VERDICT_RE = re.compile(r"\[(\d+)\]\s*verdict:\s*(A|B|same)\b", re.IGNORECASE)


@dataclass(frozen=True)
class Pair:
    """One passage before and after a copy edit, with where it stands and who reads it."""

    name: str
    where: str
    readers: str
    original: str
    edited: str


def readers_blocks(lines: Sequence[str]) -> dict[str, str]:
    """Each "Readers of X:" block in a request's prose, by X, up to the first passage header."""
    blocks: dict[str, list[str]] = {}
    current: list[str] | None = None
    for line in lines:
        if passage_number(line) is not None:
            break
        if line.startswith(READERS_OF) and line.endswith(":"):
            current = blocks.setdefault(line.removeprefix(READERS_OF).removesuffix(":"), [line])
        elif current is not None and line.strip():
            current.append(line)
        else:
            current = None
    return {name: "\n".join(rows) for name, rows in blocks.items()}


def originals_of(lines: Sequence[str]) -> tuple[dict[int, list[str]], dict[int, str]]:
    """Each passage's first run of rows marked `>`, and the file and section its header names."""
    originals: dict[int, list[str]] = {}
    places: dict[int, str] = {}
    current: int | None = None
    for line in lines:
        number = passage_number(line)
        if number is not None:
            current = number
            places[number] = line.partition("] ")[2].partition(", rows ")[0]
            continue
        row = read_row(line)
        if row is None:
            current = None
        elif current is not None and row[1] == ">":
            originals.setdefault(current, []).append(row[2])
        elif current in originals:
            current = None
    return originals, places


def pairs_of(name: str, request: str, reply: str) -> list[Pair]:
    """The pairs that `reply` makes of the passages in `request`, one for each it rewrote."""
    _, lines = copy_edit.prose_of(request)
    readers = readers_blocks(lines)
    originals, places = originals_of(lines)
    try:
        edits = rewrites(reply)
    except ValueError as error:
        raise copy_edit.Refused(f"{name}: the reply cannot be read: {error}") from error
    out: list[Pair] = []
    for number in sorted(edits):
        where = places[number]
        own = [text for path, text in readers.items() if where.startswith(path)]
        out.append(
            Pair(
                name=f"{name} [{number}]",
                where=where,
                readers="\n".join(own or readers.values()),
                original="\n".join(originals[number]),
                edited="\n".join(edits[number]),
            )
        )
    return out


def blind(pairs: Sequence[Pair], seed: int = SEED) -> tuple[str, list[dict[str, object]]]:
    """The judge's request for `pairs`, and the key that says which version is the edit."""
    order = random.Random(seed)
    blocks: list[str] = []
    key: list[dict[str, object]] = []
    for number, pair in enumerate(pairs, start=1):
        edit_is_a = order.random() < 0.5
        a, b = (pair.edited, pair.original) if edit_is_a else (pair.original, pair.edited)
        fence = copy_edit.fenced((a + "\n" + b).split("\n"))[0]
        blocks += [f"## Pair {number}", "", f"From {pair.where}.", "", pair.readers, ""]
        blocks += ["### Version A", "", fence, a, fence, ""]
        blocks += ["### Version B", "", fence, b, fence, ""]
        key.append(
            {
                "pair": number,
                "name": pair.name,
                "edit": "A" if edit_is_a else "B",
                "words": [len(pair.original.split()), len(pair.edited.split())],
            }
        )
    return "\n".join(blocks), key


def verdicts(reply: str) -> dict[int, str]:
    """The first verdict the judge's `reply` gives each pair, "A", "B" or "same", by number."""
    found: dict[int, str] = {}
    for line in reply.split("\n"):
        for match in VERDICT_RE.finditer(line.translate(EMPHASIS)):
            verdict = match.group(2)
            found.setdefault(int(match.group(1)), "same" if verdict.lower() == "same" else verdict)
    return found


def won(edit: str, verdict: str | None) -> str:
    """What won a pair whose edit is version `edit`: "edit", "original", "same", or "?"."""
    if verdict is None:
        return "?"
    if verdict == "same":
        return "same"
    return "edit" if verdict.upper() == edit else "original"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.partition("\n")[0])
    parser.add_argument("outdir", type=Path)
    parser.add_argument("files", nargs="+", type=Path, help="REQUEST REPLY pairs")
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args(argv)
    if len(args.files) % 2:
        parser.error("give each REQUEST with its REPLY")
    try:
        pairs = [
            pair
            for request, reply in zip(args.files[::2], args.files[1::2], strict=True)
            for pair in pairs_of(
                request.parent.name or request.name,
                request.read_text(encoding="utf-8"),
                reply.read_text(encoding="utf-8"),
            )
        ]
        if not pairs:
            raise copy_edit.Refused("no reply rewrote a passage, so there is nothing to judge")
        text, key = blind(pairs, args.seed)
        claude = shutil.which("claude")
        if claude is None:
            raise copy_edit.Refused("no `claude` on PATH")
        table = load_config(ROOT).models
        if table is None:
            raise copy_edit.Refused(f"{ROOT / 'docket.toml'} has no [models] table")
        choice = table.choose({"role": ROLE})
        prompt = copy_edit.instructions(PROMPT.read_text(encoding="utf-8"))
        reply, counts = copy_edit.read_once(
            text, claude, prompt, choice.model, choice.effort, os.environ, TASK
        )
    except (copy_edit.Refused, OSError) as error:
        print(f"prose_judge: no verdict: {error}", file=sys.stderr)
        return 1
    found = verdicts(reply)
    result = [
        {**entry, "won": won(str(entry["edit"]), found.get(int(str(entry["pair"]))))}
        for entry in key
    ]
    args.outdir.mkdir(parents=True, exist_ok=True)
    (args.outdir / "request.txt").write_text(text, encoding="utf-8")
    (args.outdir / "key.json").write_text(json.dumps(key, indent=1), encoding="utf-8")
    (args.outdir / "reply.txt").write_text(reply, encoding="utf-8")
    (args.outdir / "result.json").write_text(json.dumps(result, indent=1), encoding="utf-8")
    for entry in result:
        print(f"{entry['name']}: {entry['won']} ({entry['words']} words before and after)")
    print(counts.replace("copy_edit:", "prose_judge:"), file=sys.stderr)
    missing = [str(entry["pair"]) for entry in result if entry["won"] == "?"]
    if missing:
        print(f"prose_judge: pairs {', '.join(missing)} have no verdict", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
