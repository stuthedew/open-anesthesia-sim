"""Refuse a `.claude/rules/` path glob that is not anchored to the repository root.

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

**Deliberately not decided here: whether a glob describes the *right* set of
files.** That differs per rule, it is judgment rather than fact, and a tool
guessing at it would be the "worse than no tool" case `CLAUDE.md` names - its
output would look authoritative and would not be. This asks only whether an
entry is anchored, which the text answers by itself.

Standard library only, like every tool here, so it runs in a bare checkout.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

RULES_DIR = Path(".claude") / "rules"

#: The spelling that matches nothing, called out separately in the failure
#: because "add a leading slash" reads as cosmetic against it.
DEAD_PREFIX = "./"


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


def problems(root: Path) -> list[str]:
    """Every unanchored entry, and every rule whose scope cannot be read."""
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
            f"{RULES_DIR.as_posix()}, all anchored to the repository root"
        )
        return 0

    print(
        f"rules-paths: {len(found)} unanchored `paths:` entr"
        f"{'y' if len(found) == 1 else 'ies'} in {RULES_DIR.as_posix()}.\n"
        + "".join(f"  {problem}\n" for problem in found)
        + "  A leading `/` anchors an entry to the repository root. Without one it "
        "matches the same name at any depth, so a rule written about one file governs "
        "every file that happens to share its name - measured, not assumed "
        "(`PL-ZQ35`, `PL-LLWN`).",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
