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

**Every rule file, at any depth.** Claude Code discovers the `.md` files under
`.claude/rules/` recursively, so a rule in `.claude/rules/sub/` loads like any
other ([memory](https://code.claude.com/docs/en/memory), read 2026-10-12).
`rule_files` is the one reader of which files those are, and
`tools/doc_check.py` measures the resident set through it, so a nested rule is
never measured as resident here and left unread there (`PL-9NZ3`).

**The apparatus set is written, not copied** (`PL-C3K1`). It is the set of
paths `.claude/rules/apparatus-standard.md` governs, and that rule's `paths:`
is the only place the harness reads it from. Its one source is `docket.toml`'s
`workflow_paths`, the lane each path's items take, less the entries under
`tests/` and the entries `LANE_ONLY` lists. `make check` runs this tool with
`--write`, which rewrites the rule's `paths:` from that source, so a path added
to `workflow_paths` needs no second edit. CI runs it without `--write` and
refuses a `paths:` that differs from what the source gives. Until `PL-C3K1`
the set was held in two or three hand-written copies, and all six of this
check's refusals that `PL-LY24` counted asked for a new path to be added to
each copy by hand.

Whether a `workflow_paths` entry belongs in the apparatus set is the judgment.
An entry is in the set unless `LANE_ONLY` names it, and `--write` names each
path it adds, so the session that added it sees the decision in its own run.
Entries under `tests/` are left out: a test's imports decide its bar, by the
rule `.claude/rules/where-new-code-goes.md` points to.

Standard library only, like every tool here, so it runs in a bare checkout.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(ROOT / "subprojects" / "docket" / "src"))

from docket.frontmatter import (  # noqa: E402
    Misindented,
    Unread,
    closing,
    closing_quote,
    is_item,
    keys,
    uncommented,
    unquote,
)
from docket.lines import split_lines  # noqa: E402

from workflow_paths_check import declared_workflow_paths, tracked_under  # noqa: E402

#: Where Claude Code reads project rules, relative to the repository root.
RULES_DIR = ".claude/rules"

#: The spelling that matches nothing, called out separately in the failure
#: because "add a leading slash" reads as cosmetic against it.
DEAD_PREFIX = "./"

#: The rule whose `paths:` is the apparatus set's loading copy.
APPARATUS_RULE = ".claude/rules/apparatus-standard.md"

#: The `workflow_paths` entries outside the apparatus set, so that a session
#: opening one does not load the apparatus standard. Each is a record or a
#: configuration file rather than apparatus prose or code, or it is written for
#: contributors to both halves. `PL-1KTV` placed most of them, and `PL-21RC`
#: placed the rest on the same test. `docs/prose-review` holds a reverse
#: outline of `docs/MODEL.md`, a draft written from it and the texts of one
#: writing test. That is prose and records with no code, and
#: `.claude/rules/plain-writing.md`, which is resident, already governs the
#: prose (`PL-FYGJ`, `PL-GL45`).
LANE_ONLY = (
    # Records of what was decided or measured, not instructions.
    "docs/items",
    "docs/WORKING_NOTES.md",
    "docs/dead-ends.md",
    "docs/pr-bodies",
    "docs/stress-2026-09-25",
    "docs/session-ledger.tsv",
    "docs/ci-runs.tsv",
    "docs/blind-review-findings.tsv",
    "docs/blind-review-findings.md",
    "docs/model-review.md",
    "model-evidence.toml",
    "docs/hook-blocks",
    # The feature registry: one description per feature name, like the item
    # store it describes (`PL-Q3BN`).
    "docs/features.toml",
    # Prose-review records: prose, no code.
    "docs/prose-review",
    # Configuration, which carries no prose a standard could apply to.
    ".gitattributes",
    ".gitignore",
    ".vscode",
    "Makefile",
    "conftest.py",
    "docket.toml",
    ".claude-plugin",
    # Written for contributors to both halves.
    "AGENTS.md",
    "CONTRIBUTING.md",
    "docs/mutation-testing.md",
)

#: Where a glob stops being a real path. Everything before the first of these
#: is literal, and so is answerable against the tree.
GLOB_CHARS = "*?["


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


#: Why a `- ` line under `paths:` at another indentation than the list's is no glob.
_OFF_THE_LIST = (
    "`{}` under `paths:` is not at the list's indentation, or a tab indents it, which YAML "
    "refuses; write each glob as a `- ` item at the list's indentation"
)


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
    except Misindented as misplaced:
        stripped = block[misplaced.line].strip()
        if misplaced.key == "paths" and is_item(stripped):
            raise Unreadable(_OFF_THE_LIST.format(stripped)) from None
        raise Unreadable(str(misplaced)) from None
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
        if not is_item(stripped):
            raise Unreadable(
                f"`{stripped}` under `paths:` is no `- ` item, so YAML joins it into the "
                "value above it; write each glob on one line, as a `- ` item"
            )
        indent = len(line) - len(line.lstrip(" "))
        column = indent if column is None else column
        if line[indent] != "-" or indent < column:
            raise Unreadable(_OFF_THE_LIST.format(stripped))
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

    A plain scalar, or a quoted one its own line closes, read as
    `docket.frontmatter.unquote` reads it: `'it''s'` is `it's` and `"a\\"b"` is
    `a"b`, where this reader kept both quotes of the first and the backslash of
    the second (`PL-8MHZ`). Any other node raises `Unreadable` with `where`
    naming it: a flow collection or a block scalar, which this reader does not
    take, a quoted glob its line leaves open, which YAML carries onto the lines
    below even where they open with `#`, one followed by more than a comment or
    holding an escape YAML refuses, and an item holding nothing (`PL-BM8T`).
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
    if not value:
        raise Unreadable(f"{where} holds no glob; write one after the `- `, or drop the item")
    if value[:1] not in ("'", '"'):
        return value
    end = closing_quote(value)
    if end < 0:
        raise Unreadable(
            f"{where} opens a quoted glob its line does not close, so YAML carries "
            "it onto the lines below; close the quote on the glob's line"
        )
    if end < len(value) - 1:
        raise Unreadable(
            f"{where} holds `{value[end + 1 :].strip()}` after its quoted glob, which YAML "
            "refuses; end the item at the closing quote"
        )
    try:
        return unquote(value)
    except Unread as refused:
        raise Unreadable(f"{where} holds a quoted glob YAML refuses: {refused}") from None


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


def rule_files(root: Path) -> list[Path]:
    """Every rule file the repository holds, at any depth under `RULES_DIR`, in path order."""
    return tracked_under(root, RULES_DIR, ".md")


def problems(root: Path) -> list[str]:
    """Every entry that is unanchored or dead, and every rule whose scope cannot be read."""
    found: list[str] = []
    for path in rule_files(root):
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


def apparatus_paths(root: Path) -> list[str]:
    """The paths the apparatus standard governs, read from `docket.toml`'s `workflow_paths`.

    Every entry except those under `tests/` and those `LANE_ONLY` names, in
    path order.
    """
    return sorted(
        entry
        for entry in declared_workflow_paths(root)
        if not entry.startswith("tests/") and entry not in LANE_ONLY
    )


def apparatus_globs(root: Path) -> list[str]:
    """`apparatus_paths` as `paths:` globs: `/<directory>/**` or `/<file>`.

    A path the tree does not hold is written as a file. `problems` then
    refuses it as pointing at nothing, which is the right report for a
    `workflow_paths` entry with nothing behind it.
    """
    return [
        f"/{path}/**" if (root / path).is_dir() else f"/{path}" for path in apparatus_paths(root)
    ]


def _paths_key(root: Path) -> tuple[list[str], int, int]:
    """The apparatus rule's lines, and the first and end line of its `paths:` key.

    Raises `Unreadable` where the rule has no closed frontmatter or no
    `paths:` key, since there is then no list to compare or rewrite.
    """
    lines = split_lines((root / APPARATUS_RULE).read_text(encoding="utf-8"))
    close = closing(lines)
    if close is None:
        raise Unreadable("its frontmatter is missing or never closed")
    try:
        declared = [key for key in keys(lines[1:close]) if key.name == "paths"]
    except Unread as unread:
        raise Unreadable(str(unread)) from None
    if len(declared) != 1:
        raise Unreadable("it does not hold exactly one `paths:` key")
    return lines, declared[0].line + 1, declared[0].end + 1


def write_apparatus_paths(root: Path) -> tuple[list[str], list[str]]:
    """Rewrite the apparatus rule's `paths:` from `apparatus_globs`.

    Returns the globs added and the globs removed, both empty where the file
    already agreed and was left untouched. Raises `Unreadable` or `OSError`
    where the rule cannot be read.
    """
    lines, first, end = _paths_key(root)
    old = entries(lines[1 : closing(lines)])
    new = apparatus_globs(root)
    if old == new:
        return [], []
    block = ["paths:", *(f'  - "{glob}"' for glob in new)]
    text = "\n".join([*lines[:first], *block, *lines[end:]]) + "\n"
    (root / APPARATUS_RULE).write_text(text, encoding="utf-8")
    return sorted(set(new) - set(old)), sorted(set(old) - set(new))


def apparatus_set_problems(root: Path) -> list[str]:
    """Where the apparatus rule's `paths:` differs from `workflow_paths`, and stale `LANE_ONLY`."""
    found: list[str] = []
    try:
        lines, _, _ = _paths_key(root)
        declared = entries(lines[1 : closing(lines)])
    except (OSError, Unreadable) as error:
        found.append(f"apparatus set: {APPARATUS_RULE}'s `paths:` was not read ({error})")
    else:
        expected = apparatus_globs(root)
        if declared != expected:
            missing = sorted(set(expected) - set(declared))
            extra = sorted(set(declared) - set(expected))
            detail = "; ".join(
                part
                for part in (
                    f"it lacks {', '.join(missing)}" if missing else "",
                    f"it also names {', '.join(extra)}" if extra else "",
                    "" if missing or extra else "its globs are out of order",
                )
                if part
            )
            found.append(
                f"apparatus set: {APPARATUS_RULE}'s `paths:` is not the one docket.toml's "
                f"workflow_paths gives ({detail}). Run `python3 tools/rules_paths_check.py "
                "--write`, which `make check` runs, and commit the result"
            )
    workflow = declared_workflow_paths(root)
    for entry in LANE_ONLY:
        if entry not in workflow:
            found.append(
                f"apparatus set: LANE_ONLY's {entry} is no longer in workflow_paths; drop it"
            )
    return found


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="repository to check")
    parser.add_argument(
        "--write",
        action="store_true",
        help=f"first rewrite {APPARATUS_RULE}'s `paths:` from docket.toml's workflow_paths",
    )
    args = parser.parse_args(argv)

    if args.write:
        try:
            added, removed = write_apparatus_paths(args.root)
        except (OSError, Unreadable) as error:
            print(f"rules-paths: {APPARATUS_RULE}'s `paths:` was not rewritten ({error})")
        else:
            for glob in added:
                print(
                    f'rules-paths: {APPARATUS_RULE} now loads on "{glob}". If that path is a '
                    "record or a configuration file rather than apparatus, add it to LANE_ONLY "
                    "in tools/rules_paths_check.py with its reason"
                )
            for glob in removed:
                print(f'rules-paths: {APPARATUS_RULE} no longer loads on "{glob}"')

    found = problems(args.root) + apparatus_set_problems(args.root)
    if not found:
        declared = [
            entry
            for path in rule_files(args.root)
            for entry in entries(frontmatter(path.read_text(encoding="utf-8")) or [])
        ]
        print(
            f"rules-paths: {len(declared)} declared path glob(s) across "
            f"{RULES_DIR}, all anchored to the repository root and resolving; "
            f"{APPARATUS_RULE}'s `paths:` is the one workflow_paths gives"
        )
        return 0

    print(
        f"rules-paths: {len(found)} problem(s) in {RULES_DIR}.\n"
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
