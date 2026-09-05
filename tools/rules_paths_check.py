"""Refuse a `.claude/rules/` path glob that is not anchored, or that points at nothing.

A `paths:` entry decides which files load a rule. Measured against this harness
on 2026-09-05, with throwaway rules and target files at the root and under
`subprojects/docket/`:

    "README.md"    fires at the root AND at any depth
    "/README.md"   fires at the root only
    "./README.md"  fires nowhere at all
    "src/**"       fires at the root AND at any depth
    "/src/**"      fires at the root only

Every entry in this repository was written as if it were relative to the root,
and until `PL-ZQ35` none of them was. Both failure directions are silent, which
is what makes a check worth more here than prose:

- **Too wide.** The README freeze loaded on `subprojects/docket/README.md`, the
  queue tool's manual, alongside `apparatus-standard.md` - whose own text says
  every sentence of it is wrong when applied to a `README.md`. Two rules with
  opposite instructions, on a file neither was written about (`PL-ZQ35`).
- **Nowhere.** The `./` spelling above matches nothing, so a rule written that
  way is never delivered and leaves no trace saying so. Nobody has written one
  yet; it is one plausible keystroke away, and it would look correct in review.

This is a growth problem rather than a fixed one. `subprojects/` exists so that
a second tree can live here, so every unanchored glob is a collision waiting
for a directory nobody has created yet - `subprojects/docket/src/` and
`tests/` are the two that already arrived.

A second rule, added by `PL-DNYL`, closes the same failure from the other side:
**an anchored entry whose literal prefix resolves to nothing.**
`/scr/anesthesia_sim/core/**` is anchored, passes the first rule, and delivers
its rule to no session ever. That is worse than `./` on the test the paragraph
above uses - `./` is at least visibly unusual, while a transposed directory
name reads as correct at every glance - and the tree answers it outright.

A rule may not declare scope ahead of the code it governs (project owner,
2026-09-05): the rule is written when the path exists, so this is an error
rather than an advisory. There is no reading of the tree under which a dead
path is the intended state.

**Deliberately not decided here: whether a glob describes the *right* set of
files.** That differs per rule, it is judgment rather than fact, and a tool
guessing at it would be the "worse than no tool" case `CLAUDE.md` names - its
output would look authoritative and would not be. Both rules here ask only
whether an entry is anchored and whether it points at anything, which the text
and the tree answer by themselves.

Standard library only, like every tool here, so it runs in a bare checkout.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent.parent

RULES_DIR = Path(".claude") / "rules"

#: The spelling that matches nothing, called out separately in the failure
#: because "add a leading slash" reads as cosmetic against it.
DEAD_PREFIX = "./"

#: Where a glob stops being a real path. Everything before the first of these
#: is literal, and so is answerable against the tree.
GLOB_CHARS = "*?["


def _unquote(value: str) -> str:
    """One frontmatter scalar, with the quotes these files write it in."""
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def frontmatter(text: str) -> list[str] | None:
    """The lines between the opening and closing `---`, or None where there is no block.

    A file with no leading `---` carries no frontmatter and so no `paths:`: it
    is resident, which is a legitimate shape here and not this tool's business.
    An *unterminated* block is a third case and is returned as None too, which
    the caller reports rather than skips - the file declares scope that cannot
    be read, and passing it silently is the failure this check exists to stop.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return lines[1:index]
    return None


def entries(block: list[str]) -> list[str]:
    """Every `paths:` glob in one frontmatter block, in source order.

    Both shapes the harness accepts: a single glob inline after the key, and a
    YAML list beneath it. The list ends at the first line that is neither an
    item nor blank, so a later key cannot be read as one.
    """
    found: list[str] = []
    in_paths = False
    for line in block:
        stripped = line.strip()
        if not line.startswith((" ", "\t")) and stripped.startswith("paths:"):
            inline = stripped[len("paths:") :].strip()
            if inline:
                found.append(_unquote(inline))
                in_paths = False
            else:
                in_paths = True
            continue
        if not in_paths:
            continue
        if not stripped:
            continue
        if stripped.startswith("- "):
            found.append(_unquote(stripped[2:]))
            continue
        in_paths = False
    return found


def anchored(entry: str) -> str:
    """What the entry should have said."""
    if entry.startswith(DEAD_PREFIX):
        entry = entry[len(DEAD_PREFIX) :]
    return "/" + entry.lstrip("/")


def literal_prefix(entry: str) -> str:
    """The part of an anchored entry that is a real path rather than a pattern.

    A pattern beginning mid-segment leaves only the completed segments real:
    `/src/foo*.md` says nothing about `foo`, but it does say `src/` exists.
    Returned relative to the root, so the repository root itself comes back as
    the empty string - which every tree has, and which therefore never fails.
    """
    cut = len(entry)
    for index, char in enumerate(entry):
        if char in GLOB_CHARS:
            cut = index
            break
    head = entry[:cut]
    if cut < len(entry):
        head = head[: head.rfind("/") + 1]
    return head.strip("/")


def nearest_existing(root: Path, prefix: str) -> str:
    """The deepest ancestor of `prefix` that is really there, for the message.

    Naming it turns "this path is wrong" into "it stopped being real here",
    which is the difference between a reader re-reading the entry and a reader
    seeing the typo.
    """
    parts = PurePosixPath(prefix).parts
    for stop in range(len(parts) - 1, 0, -1):
        candidate = PurePosixPath(*parts[:stop])
        if (root / candidate).exists():
            return candidate.as_posix()
    return "the repository root"


def problems(root: Path) -> list[str]:
    """Every entry that is unanchored or dead, and every rule whose scope cannot be read."""
    found: list[str] = []
    for path in sorted((root / RULES_DIR).glob("*.md")):
        name = path.relative_to(root).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as error:
            found.append(f"{name}: cannot be read ({error})")
            continue
        block = frontmatter(text)
        if block is None:
            if text.lstrip().startswith("---"):
                found.append(
                    f"{name}: opens a frontmatter block that is never closed, so whatever "
                    f"scope it declares cannot be read"
                )
            continue
        for entry in entries(block):
            if entry.startswith("/"):
                prefix = literal_prefix(entry)
                target = root / prefix
                if prefix and not target.exists():
                    found.append(
                        f'{name}: "{entry}" points at nothing - "{prefix}" does not '
                        f"exist, so this rule is never delivered. Nearest existing "
                        f'path: "{nearest_existing(root, prefix)}"'
                    )
                elif prefix and entry != f"/{prefix}" and not target.is_dir():
                    found.append(
                        f'{name}: "{entry}" matches below "{prefix}", which is a file '
                        f"rather than a directory, so nothing can match it"
                    )
                continue
            if entry.startswith(DEAD_PREFIX):
                found.append(
                    f'{name}: "{entry}" matches nothing at all, so this rule is never '
                    f'delivered. Write "{anchored(entry)}"'
                )
            else:
                found.append(
                    f'{name}: "{entry}" also matches that name at any depth. '
                    f'Write "{anchored(entry)}"'
                )
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="repository to check")
    args = parser.parse_args()

    found = problems(args.root)
    if not found:
        declared = [
            entry
            for path in sorted((args.root / RULES_DIR).glob("*.md"))
            for entry in entries(frontmatter(path.read_text(encoding="utf-8")) or [])
        ]
        print(
            f"rules-paths: {len(declared)} declared path glob(s) across "
            f"{RULES_DIR.as_posix()}, all anchored to the repository root and resolving"
        )
        return 0

    print(
        f"rules-paths: {len(found)} problem(s) in {RULES_DIR.as_posix()}.\n"
        + "".join(f"  {problem}\n" for problem in found)
        + "  A `paths:` entry decides which files load a rule, and it fails silently "
        "in both directions: without a leading `/` it also matches the same name at "
        "any depth, and pointing at a path that is not there it is never delivered at "
        "all. Measured, not assumed (`PL-ZQ35`, `PL-LLWN`, `PL-DNYL`).",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
