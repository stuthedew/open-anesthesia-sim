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

sys.path.insert(0, str(ROOT / "subprojects" / "docket" / "src"))

from docket.frontmatter import Unread, closing, closing_quote, keys, uncommented  # noqa: E402
from docket.lines import split_lines  # noqa: E402

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
    Where it closes is `docket.frontmatter.closing`'s to say (`PL-R417`).
    """
    lines = split_lines(text)
    end = closing(lines)
    return None if end is None else lines[1:end]


class Unreadable(Exception):
    """A `paths:` value continued in a form `entries` does not read, named in the message."""


def entries(block: list[str]) -> list[str]:
    """Every `paths:` glob in one frontmatter block, in source order.

    Both shapes the harness accepts: a single glob inline after the key, and a
    YAML list beneath it. Where the value ends is `docket.frontmatter.keys`'s to
    say, the one reading of a front matter's keys (`PL-R417`), so a later key is
    never read as an item, a comment between two items does not end the list,
    and a line opening `paths:` inside another key's quoted value is no key
    (`PL-BM8T`). A block that reader cannot split raises `Unreadable` naming
    the line, since it may hold a `paths:` key nobody can find.

    A value YAML carries past its line in any other way raises `Unreadable`
    naming it, rather than being read from its first line (`PL-R417`): a flow
    collection, a block scalar, a quoted glob its own line does not close, a
    glob on the line after the key, or a line carrying a glob on, each of which
    YAML joins into the value or reads as something else. None is written here,
    and a glob read from a fragment would be checked as the rule's scope when it
    is not. So does `paths:` written twice, which YAML refuses (§ 3.2.1.3) and a
    lenient parser settles by keeping one of the two.

    So does a `- ` line at another indentation than the list's first item
    (`PL-PPNV`), which YAML reads as no item of the list: deeper, it is a line
    of the glob above it (YAML 1.2.2 § 7.3.3), so `- /src/**` over an indented
    `- /tests/**` is the one glob `/src/** - /tests/**`; shallower, or after a
    tab, YAML refuses it.
    """
    try:
        declared = [key for key in keys(block) if key.name == "paths"]
    except Unread as unread:
        raise Unreadable(str(unread)) from None
    if not declared:
        return []
    if len(declared) > 1:
        raise Unreadable(
            "`paths:` is written twice, which YAML refuses; write every glob under one key"
        )
    key = declared[0]
    below = block[key.line + 1 : key.end]
    if uncommented(key.inline).strip():
        glob = _glob(key.inline, "`paths:`")
        if any(line.strip() and not line.lstrip().startswith("#") for line in below):
            raise Unreadable(
                "`paths:` carries its glob onto the line after it, which YAML "
                "joins into the glob; write it on the key's line"
            )
        return [glob]
    found: list[str] = []
    # The indentation of the list's first `- `, where every item of it sits.
    column: int | None = None
    for line in below:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if not stripped.startswith("- "):
            raise Unreadable(
                f"`{stripped}` under `paths:` is no `- ` item, so YAML joins it into the "
                "value above it; write each glob on one line, as a `- ` item"
            )
        indent = len(line) - len(line.lstrip(" "))
        column = indent if column is None else column
        if line[indent] != "-" or indent < column:
            raise Unreadable(
                f"`{stripped}` under `paths:` is not at the list's indentation, or a tab "
                "indents it, which YAML refuses; write each glob as a `- ` item at the "
                "list's indentation"
            )
        if indent > column:
            raise Unreadable(
                f"`{stripped}` under `paths:` is indented past the list's first `- `, so "
                "YAML joins it into the glob above it, or refuses the file, rather than "
                "reading a glob of its own; write each glob as a `- ` item at the list's "
                "indentation"
            )
        found.append(_glob(stripped[2:], f"`{stripped}` under `paths:`"))
    return found


def _glob(node: str, where: str) -> str:
    """The glob one line's node holds, without its comment or its quotes (YAML 1.2.2 § 6.6).

    A plain scalar, or a quoted one its own line closes. Any other node raises
    `Unreadable` with `where` naming it: a flow collection or a block scalar,
    which this reader does not take, a quoted glob its line leaves open, which
    YAML carries onto the lines below even where they open with `#`, and an item
    holding nothing (`PL-BM8T`).
    """
    value = uncommented(node).strip()
    if value[:1] in ("[", "{"):
        raise Unreadable(
            f"{where} is a flow collection, which this reader does not take; "
            "write each glob as a `- ` item beneath the key"
        )
    if value[:1] in ("|", ">"):
        raise Unreadable(
            f"{where} is a block scalar, which this reader does not take; "
            "write each glob on one line, as a `- ` item"
        )
    if value[:1] in ("'", '"') and closing_quote(value) < 0:
        raise Unreadable(
            f"{where} opens a quoted glob its line does not close, so YAML carries "
            "it onto the lines below; close the quote on the glob's line"
        )
    if not value:
        raise Unreadable(f"{where} holds no glob; write one after the `- `, or drop the item")
    return _unquote(value)


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
        try:
            declared = entries(block)
        except Unreadable as unread:
            found.append(f"{name}: {unread}, so the scope it declares was not read")
            continue
        for entry in declared:
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
