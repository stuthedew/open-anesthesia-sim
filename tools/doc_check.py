"""Deterministic checks for the documentation this repository must keep true.

`CLAUDE.md` requires a session to sweep the documentation before calling an
item done, because a reader who trusts a wrong statement about which module
runs, what a constant is, or where a file lives can reach a wrong clinical
conclusion from a correct number. That sweep is a grep over five documents
and a judgment on every hit, run at the end of a session, by hand. It leaks:
`weight_kg` sat out of the provenance table until someone noticed it.

The failure modes the sweep looks for that need no judgment at all are
checked here, and never left to a session to remember:

- **Package map.** Every module under `src/anesthesia_sim/` (and `tools/`)
  appears in the matching tree in `docs/ARCHITECTURE.md`, and every path
  those trees name still exists.
- **Provenance table.** Every scientific constant in a `data/**/*.json` file
  has exactly one row in `docs/MODEL.md`'s provenance table, and every row
  names a key that file actually holds, carrying the value the table states.
- **Citations.** Every repository path and every section heading cited from
  a documentation file resolves to something that exists.
- **Release train.** Every row of `ROADMAP.md`'s timeline matches the step
  grammar, and the milestones, gates and step numbers run in order. The table
  is the project's only statement of which milestone is current and which is
  next, so it has to stay readable by a tool and not only by a person.
- **Frozen-list counts.** Every count a release's frozen list states about
  itself - in a group heading over the entries it counts, or in the version
  or timeline row naming that release - matches the entries below. The same
  number reached six places in `ROADMAP.md` once, and admitting four entries
  meant correcting nine numbers by hand. Prose counts are deliberately not
  read; see `check_gate_counts` for why.
- **Current baseline.** `ROADMAP.md`'s version table names each released
  version once, marks exactly one of them the current baseline, and its
  "Current baseline:" heading names that same version - which is the version
  `pyproject.toml` holds. Cutting a release bumps the version file and leaves
  this file naming the previous one until somebody notices, which has now
  happened twice.

One more thing is *reported* rather than checked:

- **Resident instructions.** How many lines every session loads before it has
  read anything - `CLAUDE.md` plus the rules carrying no `paths:` frontmatter
  - and whether that total has grown against the default branch. Nothing here
  passes or fails; see `check_resident_instructions` for why it must not.

What is left to judgment - whether a statement is still *true*, whether a
`must` in `docs/MODEL.md` still matches the code, whether a milestone's
out-of-scope list has become a lie - this tool does not attempt. It narrows
the sweep to the hits a human still has to read, which is what `candidates`
mode prints.

Two modes:

- `check`       full report. Errors exit non-zero and gate `make check`;
                advisories are informational and never fail a build.
- `candidates`  diff-scoped. Prints the documentation lines that mention
                anything the working tree changed, so close-out reads a
                short list instead of grepping five documents by hand.

Standard library only, and no import of the application package, so this
runs in a bare checkout exactly as it runs in CI. The one exception is
`docket.roadmap`, which owns the release-train grammar this tool checks - also
standard library only, and imported by path rather than by installation for
the same reason.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

# `ROADMAP.md`'s release-train grammar lives in `docket`, which reasons about
# project state for a living and reads the same table to report which beat of
# the planning cadence is due. A second copy here would drift from it silently,
# and the drift would be in the one document that says which milestone is
# current. Both are standard-library only and both must run in a bare checkout,
# so the import costs nothing but the path.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "subprojects" / "docket" / "src"))

try:
    # This import and the one below follow the path insertion above.
    from docket.roadmap import (
        BASELINE_MARK,
        HEADING_RE,
        TIMELINE_HEADING,
        VERSION_TABLE_HEADING,
        MilestoneSection,
        baseline_heading,
        parse_milestones,
        parse_timeline,
        parse_version_table,
        table_rows,
    )

    # Reading `git tag` is a second borrowing, for the same reason as the first.
    # `vcs` collapses every way git can fail to answer - not installed, not a
    # repository, timed out - into an empty answer, and a check that asked the
    # question itself would either duplicate that or, by omitting it, fail on a
    # checkout with no git at all. The emptiness is read here as "this checkout
    # cannot say", never as "there are no tags".
    from docket.vcs import DEFAULT_BRANCHES, is_shallow, tags
except ImportError as error:  # pragma: no cover - a checkout missing the subproject
    raise SystemExit(
        "doc_check needs subprojects/docket/src/docket/roadmap.py for the release-train "
        "grammar and docket/vcs.py for the tag read and the default-branch list, "
        f"and could not import them: {error}"
    ) from error

# Documentation whose claims this tool holds to the tree. `CLAUDE.md` and the
# docket skill are included because they cite paths as heavily as the docs
# proper do, and a rule that names a file that no longer exists is a rule
# nobody can follow.
DOC_GLOBS = (
    "README.md",
    "ROADMAP.md",
    "CLAUDE.md",
    "AGENTS.md",
    "docs/*.md",
    ".claude/rules/**/*.md",
    ".claude/skills/*/SKILL.md",
    "subprojects/*/README.md",
)

# What every session loads before it has read anything. `CLAUDE.md` may live at
# either of two paths, and a `.claude/rules/*.md` joins them unless it carries
# `paths:` frontmatter, which defers it to the sessions that open a matching
# file.
RESIDENT_ROOTS = ("CLAUDE.md", ".claude/CLAUDE.md")
RULES_DIR = ".claude/rules"

# A top-level `paths` key inside the YAML frontmatter block. Read this way
# rather than with a YAML parser because this tool is standard library only,
# and because the question is only ever "is the key there".
PATHS_KEY_RE = re.compile(r"paths\s*:")

# Every way git can fail to answer, named rather than written as a tuple in the
# `except` clause itself. This file must run under whatever bare `python3` is on
# PATH, but the repository's formatter targets a newer one, and it rewrites a
# parenthesized multi-type `except` into PEP 758's unparenthesized form, which
# older interpreters cannot parse. `subprojects/docket/` was broken exactly this
# way once and now guards it with a portability test; this file has the same
# exposure and no such guard. A name is not rewritten.
GIT_UNAVAILABLE = (OSError, subprocess.SubprocessError)

# Named for the same reason: a file that cannot be read is not a finding, and
# the two ways it can fail must not be written as a tuple in the `except`
# clause itself.
UNREADABLE = (OSError, UnicodeDecodeError)

# Where the package map lives, and where the provenance table lives.
ARCHITECTURE = Path("docs/ARCHITECTURE.md")
MODEL = Path("docs/MODEL.md")

# Where the release train lives. `ROADMAP.md` calls itself the authoritative
# version and milestone map, and it is the only statement of which milestone
# is current and which is next. That makes its rows something a tool has to be
# able to read, not only a person: `docket wave` reports the project's position
# on this table, and a parser guessing at free prose would be guessing at the
# plan.
ROADMAP = Path("ROADMAP.md")

PACKAGE_ROOT = PurePosixPath("src/anesthesia_sim")

# Directories that hold no reviewable source, so nothing in them belongs in a
# package map and nothing in them answers a path citation.
IGNORED_DIRS = frozenset(
    {
        ".git",
        ".venv",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        "__pycache__",
        "node_modules",
        "build",
        "dist",
    }
)

# What a package map is expected to account for. `__init__.py` is excluded
# because it carries no behavior here and listing five of them would bury the
# modules that do.
MAPPED_SUFFIXES = frozenset({".py", ".json"})
UNMAPPED_NAMES = frozenset({"__init__.py"})

# Suffixes that make a code span a claim about a file in this repository.
# A span without one of these is prose or an identifier (`Entry.model_guidance`,
# `flet_charts.*`, `v0.2.0`), not a path, and is not resolved.
PATH_SUFFIXES = frozenset(
    {".py", ".json", ".md", ".yml", ".yaml", ".toml", ".sh", ".cfg", ".ini", ".lock", ".txt"}
)

# Prefixes a path citation may be written against. The documentation writes
# `core/parameters.py` and `data/agents/sevoflurane.json` package-relative,
# and `tools/doc_check.py` repository-relative; both are correct, so both
# roots are tried.
PATH_ROOTS = ("", str(PACKAGE_ROOT))

# Top-level keys in a data file that are not scientific parameters and so are
# not expected in the provenance table. `sources` is the citation array the
# table points *at*; `schema_version` is a file-format number.
NON_PARAMETER_KEYS = frozenset({"schema_version", "sources"})

FENCE_RE = re.compile(r"^```")
TREE_ROOT_RE = re.compile(r"^(?P<path>[\w./-]+/)$")
TREE_ENTRY_RE = re.compile(r"^(?P<indent>(?:(?:│   )|(?:    ))*)(?:├──|└──) (?P<name>\S+)")
CODE_SPAN_RE = re.compile(r"`([^`\n]+)`")
LINK_RE = re.compile(r"\[[^\]\n]*\]\((?P<target>[^)\s]+)\)")
NUMBER_RE = re.compile(r"[-+]?\d+(?:\.\d+)?")

BRACE_RE = re.compile(r"\{([^{}]*)\}")

# A quoted phrase is read as a section citation only in the two forms this
# repository actually writes: after `see`/`under`, or immediately before
# `above`/`below`. Bare `in "..."` is ordinary English and is left alone.
CITATION_RE = re.compile(
    r'(?:\b(?:see|under)\s+"(?P<named>[^"\n]+)")'
    r'|(?:"(?P<directed>[^"\n]+)"[ ]+(?:above|below)\b)',
    re.IGNORECASE,
)
DIRECTION_RE = re.compile(r"^[ ]*(?:above|below)\b", re.IGNORECASE)

# The `**Tags.**` statement. What it claims is deliberately not a list: the
# version table above it already says which releases exist, so restating them
# would be a second copy to keep true, and it was wrong twice before this check
# was written. The claim is the invariant instead - every completed release
# carries a tag - which is read against the table and `git tag` directly.
#
# What stays prose is the exception. A version that genuinely shipped untagged
# is named in a bold sentence, and the decidable half of that is its count
# against the names it gives; whether the omission is settled or an open
# decision is not, and is left alone.
TAGS_MARK_RE = re.compile(r"^\*\*Tags\.\*\*")
UNTAGGED_CLAIM_RE = re.compile(
    r"\*\*(?P<count>[A-Za-z]+|\d+)\s+versions?\s+(?:are|is)\s+untagged\*\*", re.I
)
# `: v0.1.0, v0.2.0 and v0.3.0` - read one version at a time so the list ends
# where the prose resumes, rather than sweeping up every version in the region.
LIST_SEPARATOR_RE = re.compile(r"[\s,:]*(?:and\s+)?")
LIST_VERSION_RE = re.compile(r"v(?P<version>\d+\.\d+\.\d+)")
# A tag naming a release, as against `v1.2.3-rc1` or a name of another shape.
RELEASE_TAG_RE = re.compile(r"^v?(?P<version>\d+\.\d+\.\d+)$")
# The status cell that says a version has gone out.
COMPLETED_MARK = "completed"
# This document writes its counts as words, so both forms are read. Anything
# outside the table is reported rather than guessed at: a count nobody can read
# is a count nobody is checking.
NUMBER_WORDS = {
    "no": 0,
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
}

# A Makefile target is a line-initial name followed by a colon. `:=` is an
# assignment, and `.PHONY` and its kin start with a dot, so neither matches.
MAKE_TARGET_RE = re.compile(r"^(?P<name>[A-Za-z][\w.-]*)\s*:(?!=)")
# `.PHONY` names targets without defining them. A name listed here and given no
# recipe is the silent failure this check exists for: `make` accepts it and
# exits 0. A name in neither place fails loudly, which needs no tool.
PHONY_RE = re.compile(r"^\.PHONY\s*:(?P<names>.*)$")
# `make docket`, as the documentation writes it. Read only inside code spans
# and fenced blocks: prose says "make sure" and means nothing of the kind.
MAKE_MENTION_RE = re.compile(r"\bmake\s+(?P<name>[a-z][\w.-]*)")

# Where CI's commands live. A workflow step names repository scripts by path
# exactly as the documentation does, and nothing was holding it to them.
# GitHub renders inline math from `$`...`$` (or `$...$`) and block math from a
# `$$` fence. It does not recognise LaTeX's `\(...\)` or `\[...\]`: `(` and
# `)` are ASCII punctuation, so CommonMark consumes the backslash as a
# character escape before any math parser runs, and `\(t\)` reaches the page
# as the literal text `(t)`. `docs/MODEL.md` carried 97 of them, its entire
# symbol table among them, and seven queue items had copied the form out of it
# (`PL-TH9V`).
TEX_DELIMITER_RE = re.compile(r"\\[()\[\]]")

# A well-formed inline expression, `$`...`$`, allowing the longer backtick runs
# CommonMark permits.
MATH_SPAN_RE = re.compile(r"\$(`+)(?:(?!\1).)*\1\$")

# The two halves of one that is not well-formed. Inline math is parsed within a
# line, so an expression split by a line break renders as literal text on both
# sides. Four in this repository were split that way, one of them already on
# the correct delimiters and broken only by a paragraph reflow - which is why
# the rule is worth keeping after the conversion rather than only during it.
MATH_EDGE_RE = re.compile(r"\$`|`\$")

# A backtick run that is code rather than math. Blanked before either rule
# runs: `\(` inside a code span is a quotation of the broken syntax rather than
# a use of it, and a shell snippet like `"$upstream..HEAD"` is not an unclosed
# expression.
BACKTICK_RUN_RE = re.compile(r"(`+)(?:(?!\1).)*\1")

# Any fence, including an indented one. `FENCE_RE` is anchored at column zero
# and matches only backticks, which is right for the package-map reader but
# would leave an indented or tilde-fenced sample exposed to the rules below.
ANY_FENCE_RE = re.compile(r"^\s*(?:```|~~~)")

WORKFLOW_GLOBS = (".github/workflows/*.yml", ".github/workflows/*.yaml")

# `run:` opens a step's shell, either inline or as a block scalar whose body
# is every following line indented past the key. Reading it this way rather
# than parsing YAML keeps this tool standard-library only, which is what lets
# a hook or a bare checkout run it.
RUN_STEP_RE = re.compile(r"^(?P<indent>\s*)-?\s*run:\s*(?P<inline>.*)$")
BLOCK_SCALARS = frozenset({"|", ">", "|-", ">-", "|+", ">+"})

# Shell syntax that separates one token from the next.
COMMAND_SPLIT_RE = re.compile(r"[\s;|&()<>]+")

# A token this check cannot resolve by reading the tree: a shell or GitHub
# expansion, a glob whose intended match is not stated, a URL, or an action
# reference. Skipped rather than guessed at - a checker that guesses at the
# judgment half is worse than no checker.
UNRESOLVABLE = ("$", "*", "?", "://", "@")


@dataclass
class Report:
    """Findings, split by whether a machine or a human has to resolve them."""

    errors: list[str] = field(default_factory=list)
    advisories: list[str] = field(default_factory=list)
    # Checks this checkout could not run, each naming why. Kept apart from
    # advisories because they are the opposite claim: an advisory says
    # something was read and wants judgment, a decline says nothing was read
    # at all, and collapsing the two lets a check that never ran be reported
    # as one that passed (`PL-XCYB`, and `PL-J295` for the tag reader).
    declined: list[str] = field(default_factory=list)
    # What every session loads before it has read anything. Not a finding:
    # `format_check` prints it whether or not anything else fired, because the
    # number is the point rather than any verdict on it. `None` only when the
    # checkout holds no resident instruction file at all.
    resident: ResidentInstructions | None = None


@dataclass(frozen=True)
class ResidentInstructions:
    """The instruction files loaded at launch, measured, and against the base.

    `baseline_ref` is the default branch this was compared against, and is
    `None` when no checkout could be read - a bare tree, no git, no default
    branch. The comparison is the part that goes missing then; the current
    total is still known, so it is still reported.
    """

    files: tuple[tuple[str, int], ...]
    baseline_ref: str | None = None
    baseline_files: tuple[tuple[str, int], ...] | None = None

    @property
    def total(self) -> int:
        return sum(count for _, count in self.files)

    @property
    def baseline_total(self) -> int | None:
        if self.baseline_files is None:
            return None
        return sum(count for _, count in self.baseline_files)

    @property
    def growth(self) -> int | None:
        baseline = self.baseline_total
        return None if baseline is None else self.total - baseline

    def deltas(self) -> list[tuple[str, int]]:
        """Per-file change against the baseline, largest growth first."""
        if self.baseline_files is None:
            return []
        before = dict(self.baseline_files)
        names = sorted({*before, *dict(self.files)})
        changed = [(name, dict(self.files).get(name, 0) - before.get(name, 0)) for name in names]
        return sorted((row for row in changed if row[1]), key=lambda row: -row[1])


@dataclass(frozen=True)
class TreeMap:
    """One package-map tree, as drawn in `docs/ARCHITECTURE.md`."""

    root: PurePosixPath
    line: int
    files: frozenset[PurePosixPath]
    # Directories drawn without any children beneath them. Such an entry
    # stands for its whole subtree — a unit documented by its own README
    # rather than module by module — so files under it are covered without
    # being listed. No tree draws one today; the mechanism is kept because a
    # subtree with its own documentation is the case it exists for.
    covered_dirs: frozenset[PurePosixPath]

    @property
    def entries(self) -> frozenset[PurePosixPath]:
        return self.files | self.covered_dirs


def _line_of(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def _expand_braces(token: str) -> list[str]:
    """Expand `a/{x,y}.json` the way the trees and citations write it."""
    match = BRACE_RE.search(token)
    if match is None:
        return [token]
    expanded: list[str] = []
    for option in match.group(1).split(","):
        expanded.extend(_expand_braces(token[: match.start()] + option + token[match.end() :]))
    return expanded


def _walk(directory: Path) -> Iterator[Path]:
    """Yield every file under `directory`, skipping caches and virtualenvs."""
    for child in sorted(directory.iterdir()):
        if child.name in IGNORED_DIRS:
            continue
        if child.is_dir():
            yield from _walk(child)
        elif child.is_file():
            yield child


def read_docs(root: Path) -> dict[Path, str]:
    """Read every documentation file this tool holds to the tree."""
    documents: dict[Path, str] = {}
    for pattern in DOC_GLOBS:
        for path in sorted(root.glob(pattern)):
            if path.is_file():
                documents[path.relative_to(root)] = path.read_text(encoding="utf-8")
    return documents


def _fenced_blocks(text: str) -> Iterator[tuple[int, list[str]]]:
    """Yield each fenced block as its opening line number and its contents."""
    lines = text.splitlines()
    index = 0
    while index < len(lines):
        if not FENCE_RE.match(lines[index]):
            index += 1
            continue
        start = index + 1
        body: list[str] = []
        index += 1
        while index < len(lines) and not FENCE_RE.match(lines[index]):
            body.append(lines[index])
            index += 1
        index += 1
        yield start, body


def parse_tree(root: Path, start_line: int, block: list[str]) -> TreeMap | None:
    """Read one fenced block as a package-map tree, or decline it.

    A block is a tree when its first line is a lone directory path that
    exists. That is what separates the package maps from the layering and
    data-flow diagrams drawn in the same file with the same fence.
    """
    body = [line for line in block if line.strip()]
    if not body:
        return None
    match = TREE_ROOT_RE.match(body[0].strip())
    if match is None:
        return None
    tree_root = PurePosixPath(match.group("path").rstrip("/"))
    if not (root / tree_root).is_dir():
        return None

    files: set[PurePosixPath] = set()
    directories: set[PurePosixPath] = set()
    parents: set[PurePosixPath] = set()
    stack: list[str] = []

    for line in body[1:]:
        entry = TREE_ENTRY_RE.match(line)
        if entry is None:
            continue
        depth = len(entry.group("indent")) // 4
        name = entry.group("name")
        del stack[depth:]
        stack.append(name.rstrip("/"))
        for expanded in _expand_braces("/".join(stack)):
            path = tree_root / expanded
            if name.endswith("/"):
                directories.add(path)
            else:
                files.add(path)
            if depth:
                parents.add(path.parent)

    return TreeMap(
        root=tree_root,
        line=start_line,
        files=frozenset(files),
        covered_dirs=frozenset(directories - parents),
    )


def _mapped_candidates(root: Path, tree_root: PurePosixPath) -> list[PurePosixPath]:
    """Files under a mapped root that a package map is expected to account for."""
    base = root / tree_root
    return [
        tree_root / PurePosixPath(path.relative_to(base).as_posix())
        for path in _walk(base)
        if path.suffix in MAPPED_SUFFIXES and path.name not in UNMAPPED_NAMES
    ]


def check_package_maps(root: Path, report: Report) -> None:
    """Hold `docs/ARCHITECTURE.md`'s trees to the tree on disk, both ways."""
    path = root / ARCHITECTURE
    if not path.is_file():
        report.errors.append(f"{ARCHITECTURE}: missing; the package map cannot be checked")
        return

    text = path.read_text(encoding="utf-8")
    trees = [
        tree
        for start, block in _fenced_blocks(text)
        if (tree := parse_tree(root, start, block)) is not None
    ]
    if not trees:
        report.errors.append(
            f"{ARCHITECTURE}: no package-map tree found; either the file lost its map or the "
            "tree format changed and this check has gone blind"
        )
        return

    for tree in trees:
        where = f"{ARCHITECTURE} (package map at line {tree.line})"

        for entry in sorted(tree.entries):
            if not (root / entry).exists():
                report.errors.append(f"{where}: lists {entry}, which does not exist")

        for candidate in _mapped_candidates(root, tree.root):
            if candidate in tree.files:
                continue
            if any(parent in tree.covered_dirs for parent in candidate.parents):
                continue
            report.errors.append(f"{where}: does not list {candidate}")


def _leaf_numbers(node: object, prefix: str = "") -> Iterator[tuple[str, float]]:
    """Yield every numeric leaf of a data file as `dotted.key`, value."""
    if isinstance(node, dict):
        for key, value in node.items():
            if not prefix and key in NON_PARAMETER_KEYS:
                continue
            yield from _leaf_numbers(value, f"{prefix}.{key}" if prefix else key)
    elif isinstance(node, bool):
        return
    elif isinstance(node, (int, float)):
        yield prefix, float(node)


def _lookup(document: object, key_path: str) -> float | None:
    node: object = document
    for key in key_path.split("."):
        if not isinstance(node, dict) or key not in node:
            return None
        node = node[key]
    if isinstance(node, bool) or not isinstance(node, (int, float)):
        return None
    return float(node)


def check_provenance(root: Path, report: Report) -> None:
    """Hold `docs/MODEL.md`'s provenance table to the data files, both ways.

    Each row names the data file and the key path it documents, so a row is
    checked against the value that key actually holds rather than against
    whichever number in the file happens to match. A derived row states the
    stored value alongside the derived one (`1.6923 (= 1.1 / 0.65)`), so the
    stored value is required to appear in the cell, not to be the whole of it.
    """
    path = root / MODEL
    if not path.is_file():
        report.errors.append(f"{MODEL}: missing; the provenance table cannot be checked")
        return

    documented: dict[tuple[str, str], int] = {}
    rows = list(table_rows(path.read_text(encoding="utf-8"), "Parameter provenance"))
    if not rows:
        report.errors.append(
            f"{MODEL}: no provenance table found under 'Parameter provenance'; either the "
            "table moved or its format changed and this check has gone blind"
        )
        return

    for line, cells in rows:
        where = f"{MODEL} (line {line})"
        if len(cells) < 4:
            report.errors.append(f"{where}: provenance row has {len(cells)} cells, expected 4")
            continue

        parameter, value_cell, _unit, source_cell = cells[0], cells[1], cells[2], cells[3]
        spans = CODE_SPAN_RE.findall(source_cell)
        if len(spans) != 2:
            report.errors.append(
                f"{where}: {parameter!r} names {len(spans)} code spans in its source cell; "
                "expected the data file and the JSON key path it documents"
            )
            continue

        relative, key_path = spans
        data_path = root / PACKAGE_ROOT / relative
        if not data_path.is_file():
            report.errors.append(f"{where}: {parameter!r} cites {relative}, which does not exist")
            continue

        document = json.loads(data_path.read_text(encoding="utf-8"))
        stored = _lookup(document, key_path)
        if stored is None:
            report.errors.append(
                f"{where}: {parameter!r} names key {key_path!r}, which {relative} does not "
                "hold as a number"
            )
            continue

        key = (relative, key_path)
        if key in documented:
            report.errors.append(
                f"{where}: {relative} {key_path} already has a row at line {documented[key]}; "
                "each constant is documented once"
            )
            continue
        documented[key] = line

        stated = [float(number) for number in NUMBER_RE.findall(value_cell)]
        if stored not in stated:
            report.errors.append(
                f"{where}: {parameter!r} states {value_cell!r} but {relative} holds "
                f"{key_path} = {stored:g}"
            )

    data_root = root / PACKAGE_ROOT / "data"
    if not data_root.is_dir():
        return
    for data_path in _walk(data_root):
        if data_path.suffix != ".json":
            continue
        relative = PurePosixPath(data_path.relative_to(root / PACKAGE_ROOT).as_posix())
        document = json.loads(data_path.read_text(encoding="utf-8"))
        for key_path, value in _leaf_numbers(document):
            if (str(relative), key_path) not in documented:
                report.errors.append(
                    f"{MODEL}: no provenance row for {relative} {key_path} = {value:g}; "
                    "every constant a clinician could read belongs in the table"
                )


def check_timeline(root: Path, report: Report) -> None:
    """Hold `ROADMAP.md`'s release train to a shape a tool can read."""
    roadmap = root / ROADMAP
    if not roadmap.is_file():
        return
    text = roadmap.read_text(encoding="utf-8")

    steps, problems = parse_timeline(text)
    report.errors.extend(f"{ROADMAP}: {problem}" for problem in problems)
    if not steps and not problems:
        # The table is the mechanism, not decoration: losing it to a rename or
        # a reformat would leave every reader of the plan with nothing, and
        # would do it silently.
        report.errors.append(f'{ROADMAP}: no timeline table found under "{TIMELINE_HEADING}"')
        return
    if steps and not any(step.kind == "milestone" for step in steps):
        report.errors.append(f"{ROADMAP}: the timeline names no milestone version")


def check_baseline(root: Path, report: Report) -> None:
    """Hold the three statements of the current version to each other.

    `ROADMAP.md` calls itself the authoritative version and milestone map, and
    every release note, gate record and milestone claim is anchored to it. It
    says which version is current in two places - one row of the version table
    and the heading below it - and `pyproject.toml` says it in a third. A
    release bumps the third and leaves the other two behind, which has now
    happened twice, the second time one release after the first was repaired.

    This refuses rather than writes. The milestone column is editorial prose,
    and a generated row would either be thin or would overwrite something
    considered; refusing costs the owner one hand-written row per release and
    cannot corrupt the file. Whether those versions carry tags is `check_tags`
    below, which reads git and therefore has to stay silent when git cannot
    answer; this one compares three statements already in the tree and can run
    anywhere.
    """
    roadmap = root / ROADMAP
    version_file = root / "pyproject.toml"
    if not roadmap.is_file() or not version_file.is_file():
        return
    text = roadmap.read_text(encoding="utf-8")

    rows = parse_version_table(text)
    if not rows:
        report.errors.append(f'{ROADMAP}: no version table found under "{VERSION_TABLE_HEADING}"')
        return

    seen: dict[str, int] = {}
    for row in rows:
        if row.version in seen:
            report.errors.append(
                f"{ROADMAP}:{row.line}: v{row.version} already has a row at line "
                f"{seen[row.version]}; one row per released version"
            )
        seen.setdefault(row.version, row.line)

    marked = [row for row in rows if row.is_baseline]
    if len(marked) != 1:
        where = ", ".join(f"line {row.line}" for row in marked) or "no row"
        report.errors.append(
            f'{ROADMAP}: {len(marked)} rows are marked "{BASELINE_MARK}" ({where}); '
            "exactly one release is current"
        )
        return

    declared = _project_version(version_file)
    if declared and marked[0].version != declared:
        report.errors.append(
            f"{ROADMAP}:{marked[0].line}: the current baseline row is v{marked[0].version}, "
            f"but pyproject.toml holds {declared}"
        )

    heading = baseline_heading(text)
    if heading is None:
        report.errors.append(f'{ROADMAP}: no "Current baseline: vX.Y.Z" heading')
    elif heading[1] != marked[0].version:
        report.errors.append(
            f"{ROADMAP}:{heading[0]}: the baseline heading names v{heading[1]}, but the "
            f"table marks v{marked[0].version} current"
        )


# --- the counts a frozen list states about itself ---------------------------

#: How `ROADMAP.md` writes a small number. Digits are read too, because the
#: file uses both and which one a writer reached for says nothing about what
#: the number means.
_UNITS = (
    "zero",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
    "ten",
    "eleven",
    "twelve",
    "thirteen",
    "fourteen",
    "fifteen",
    "sixteen",
    "seventeen",
    "eighteen",
    "nineteen",
)
_TENS = ("twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety")

# A stated count of entries: `thirty-seven entries`, `20 entries`. The word
# before `entries` is read as a number and the phrase is passed over when it is
# not one, so "no entries" and "the remaining entries" state no count and are
# left alone rather than reported.
ENTRY_COUNT_RE = re.compile(r"(?P<count>[\w-]+)\s+entries\b")

# A group heading inside a frozen list: an emphasized line whose label is
# followed by a dash and then the count of what comes after it, as in
# `*Stops new debt being introduced - fifteen entries:*`. The count has to sit
# on the far side of the dash, where a heading puts it, which is what keeps a
# paragraph *about* some entries - "Four entries added 2026-08-30 from an
# outside review of the repository" - from being read as a heading over them.
GATE_GROUP_RE = re.compile(
    r"^\*{1,2}.*?(?:\u2014|\s-\s)\s*(?P<entries>[\w-]+)\s+entries\b"
    r"(?:,\s*(?P<ids>[\w-]+)\s+item ids)?"
)


def _count_word(word: str) -> int | None:
    """The number a count word states, or `None` where it states none."""
    token = word.strip().casefold()
    if token.isdigit():
        return int(token)
    if token in _UNITS:
        return _UNITS.index(token)
    tens, _, unit = token.partition("-")
    if tens in _TENS:
        base = (_TENS.index(tens) + 2) * 10
        if not unit:
            return base
        if unit in _UNITS[1:10]:
            return base + _UNITS.index(unit)
    return None


def _subsection_end(lines: Sequence[str], start: int) -> int:
    """Where a gate subsection stops, read the way `_gate_entries` reads it."""
    for index in range(start, len(lines)):
        heading = HEADING_RE.match(lines[index])
        if heading is not None and len(heading.group("hashes")) <= 3:
            return index
    return len(lines)


def _gate_groups(
    lines: Sequence[str], section: MilestoneSection
) -> Iterator[tuple[int, int, int | None, int, int]]:
    """Each count-carrying group heading of a frozen list, and what follows it.

    Yields the heading's line, the counts it states, and the counts of the
    entries between it and the next such heading. A heading stating no
    readable count is not one of these and is passed over: it groups the list
    without claiming a size, which is a shape the file already uses.
    """
    end = _subsection_end(lines, section.gate_line)
    headings: list[tuple[int, int, int | None]] = []
    for index in range(section.gate_line, end):
        match = GATE_GROUP_RE.match(lines[index])
        if match is None:
            continue
        stated = _count_word(match.group("entries"))
        if stated is None:
            continue
        ids = match.group("ids")
        headings.append((index + 1, stated, _count_word(ids) if ids else None))

    for position, (line, stated, stated_ids) in enumerate(headings):
        following = headings[position + 1][0] if position + 1 < len(headings) else end + 1
        covered = [entry for entry in section.gate_entries if line < entry.line < following]
        yield line, stated, stated_ids, len(covered), sum(len(entry.ids) for entry in covered)


def _table_counts(text: str, section: MilestoneSection) -> Iterator[tuple[int, str, int]]:
    """Every entry count the two tables state about one release's frozen list.

    Only a row whose *own* naming cell is this release is read, so the v0.3.0
    row saying what Gate 0 holds - a list recorded under v0.4.0 - is not read
    as a claim about v0.3.0, which records no list at all.
    """
    rendered = "v{}.{}.{}".format(*section.version)
    for where, heading, level, naming in (
        ("version table", VERSION_TABLE_HEADING, 2, 0),
        ("timeline", TIMELINE_HEADING, 3, 1),
    ):
        for line, cells in table_rows(text, heading, level=level):
            if len(cells) <= naming or rendered not in cells[naming]:
                continue
            for cell in cells[naming + 1 :]:
                for match in ENTRY_COUNT_RE.finditer(cell):
                    stated = _count_word(match.group("count"))
                    if stated is not None:
                        yield line, where, stated


def check_gate_counts(root: Path, report: Report) -> None:
    """Hold every count a frozen list states about itself to the list.

    `ROADMAP.md` states the size of a release's frozen list in its own group
    headings and in the two tables that name the release, and the same number
    reached six places once. On 2026-08-31 three of them said "nineteen" while
    one said "twenty-two"; on 2026-09-01 the timeline said eighteen, four
    paragraphs said thirty-one and the list's own intro said thirty-two, and
    admitting four entries that day meant correcting nine numbers by hand -
    then eight of them again an hour later, for a fifth entry.

    The file already states the principle: "a count written into a document
    goes stale the next time an item closes". It applies it to the *closed*
    count, which is deliberately not recorded and read from `bin/docket wave`
    instead. This applies the same rule to the total.

    Only counts whose meaning is fixed by where they sit are read - a group
    heading over the entries it counts, and a cell of the version or timeline
    table naming that release. Prose is deliberately left alone: a checker
    cannot tell "the thirty-seven entries below are its whole content", a
    claim about today's list, from "frozen ... at seventeen entries", a dated
    fact that must never change. Judging that is a reader's job, so the prose
    restates no count instead of being guessed at.
    """
    roadmap = root / ROADMAP
    if not roadmap.is_file():
        return
    text = roadmap.read_text(encoding="utf-8")
    lines = text.splitlines()

    for section in parse_milestones(text):
        if not section.records_a_gate:
            continue
        rendered = "v{}.{}.{}".format(*section.version)
        total = len(section.gate_entries)
        groups = list(_gate_groups(lines, section))

        for line, stated, stated_ids, entries, ids in groups:
            if stated != entries:
                report.errors.append(
                    f"{ROADMAP}:{line}: this group heading of {rendered}'s frozen list "
                    f"says {stated} entries, but {entries} follow it"
                )
            if stated_ids is not None and stated_ids != ids:
                report.errors.append(
                    f"{ROADMAP}:{line}: this group heading of {rendered}'s frozen list "
                    f"says {stated_ids} item ids, but the entries under it hold {ids}"
                )

        summed = sum(stated for _, stated, _, _, _ in groups)
        if groups and summed != total:
            report.errors.append(
                f"{ROADMAP}:{section.gate_line}: the group headings of {rendered}'s frozen "
                f"list count {summed} entries between them, but the list holds {total}"
            )

        for line, where, stated in _table_counts(text, section):
            if stated != total:
                report.errors.append(
                    f"{ROADMAP}:{line}: the {where} row for {rendered} says {stated} "
                    f"entries, but its frozen list holds {total}"
                )


def _tags_region(text: str) -> tuple[int, str] | None:
    """The `**Tags.**` statement, and everything up to the next section heading.

    The exception sentence has historically sat in a paragraph below the claim
    rather than inside it, so the region runs to the heading rather than to the
    blank line.
    """
    lines = text.splitlines()
    start = next((index for index, line in enumerate(lines) if TAGS_MARK_RE.match(line)), None)
    if start is None:
        return None
    end = next(
        (index for index in range(start + 1, len(lines)) if HEADING_RE.match(lines[index])),
        len(lines),
    )
    return start + 1, "\n".join(lines[start:end])


def _version_list(text: str, start: int) -> list[str]:
    """Versions written as a run of `v0.1.0`, separated by commas and `and`."""
    found: list[str] = []
    position = start
    while True:
        gap = LIST_SEPARATOR_RE.match(text, position)
        candidate = LIST_VERSION_RE.match(text, gap.end() if gap else position)
        if candidate is None:
            return found
        found.append(candidate.group("version"))
        position = candidate.end()


def _untagged_claim(body: str, first_line: int) -> tuple[frozenset[str], list[str], int]:
    """The versions the roadmap says went out untagged, and whether it counts them right.

    Two sentences that each agree with `git tag` can still disagree with each
    other, which is why the count is read at all: it is the one part of the
    claim that no comparison with the repository would catch.
    """
    match = UNTAGGED_CLAIM_RE.search(body)
    if match is None:
        return frozenset(), [], 0
    line = first_line + body[: match.start()].count("\n")
    named = _version_list(body, match.end())

    stated = match.group("count")
    count = int(stated) if stated.isdigit() else NUMBER_WORDS.get(stated.casefold())
    if count is None:
        return frozenset(named), [f'{ROADMAP}:{line}: cannot read "{stated}" as a count'], line
    if count != len(named):
        return (
            frozenset(named),
            [
                f"{ROADMAP}:{line}: the sentence says {stated} untagged, but names "
                f"{len(named)}; the two halves cannot both be right"
            ],
            line,
        )
    return frozenset(named), [], line


def _is_tagged(version: str, existing: frozenset[str]) -> bool:
    """Whether a tag names this release, written with or without its leading `v`."""
    return f"v{version}" in existing or version in existing


def check_tags(root: Path, report: Report) -> None:
    """Hold the roadmap's tag statements to `git tag`, and to each other.

    The statements exist because four versions once went out untagged and the
    gap could not be repaired afterwards with any confidence: `git describe
    --contains` resolves nothing across an untagged release's span, so "which
    release did this change go out in" stops having an answer. A claim about
    which releases are traceable that is not itself traceable is the wrong way
    round, and it went stale exactly as one would expect - by releases landing,
    with nothing reading the sentence.

    Three silences are deliberate. A checkout git cannot answer for - no
    repository, no git, no tags fetched - is told nothing at all, because a
    check that fails on how somebody fetched the repository is a check that
    gets switched off.

    A **truncated** checkout is the second, and it was missed for exactly as
    long as this docstring claimed the first one covered it (`PL-J295`). A
    shallow clone does not collapse to an empty tag set: it holds the tags
    pointing into its fetched depth and omits the rest, so every release older
    than that depth reads as never tagged. That fired on `main` in every web
    session container, eight false errors at a time.

    The guard is deliberately narrower than "this clone is shallow". Both the
    session containers and `actions/checkout` clone shallow, so declining on
    that alone would retire the check everywhere it runs - including in a
    checkout that has since fetched its tags and can answer exactly. So the
    findings are computed first, and only withheld when there is something to
    withhold *and* truncation could account for it. A tag being **present** is
    never in doubt, so those inferences are untouched.

    And the release being cut right now is
    an advisory rather than an error: its tag goes on the merge commit, so
    there is a window in which the newest version is completed and untagged,
    and failing it would turn `make check` red on every release branch - which
    is the failure `make release` was just repaired to stop causing.
    """
    roadmap = root / ROADMAP
    if not roadmap.is_file():
        return
    text = roadmap.read_text(encoding="utf-8")

    rows = parse_version_table(text)
    completed = {row.version: row for row in rows if COMPLETED_MARK in row.status.casefold()}
    if not completed:
        return

    region = _tags_region(text)
    if region is None:
        report.errors.append(
            f'{ROADMAP}: no "**Tags.**" statement; it is where this file says every '
            "released version is traceable to a tag, and deleting it removes the claim "
            "rather than making it true"
        )
        return
    first_line, body = region

    untagged, problems, claim_line = _untagged_claim(body, first_line)
    report.errors.extend(problems)
    for version in sorted(untagged):
        if version not in completed:
            report.errors.append(
                f"{ROADMAP}:{claim_line}: v{version} is named as untagged, but no row of the "
                "version table marks it completed"
            )

    existing = tags(root)
    if not existing:
        return

    marked = [row for row in rows if row.is_baseline]
    baseline = marked[0].version if len(marked) == 1 else ""

    absent: list[str] = []
    for version, row in sorted(completed.items()):
        if version in untagged or _is_tagged(version, existing):
            continue
        if version == baseline:
            report.advisories.append(
                f"{ROADMAP}:{row.line}: v{version} is the current baseline and carries no "
                f"tag yet; tag the merge once it lands:\n"
                f'    git tag -a v{version} <merge commit> -m "v{version}"\n'
                f"    git push origin v{version}"
            )
            continue
        absent.append(
            f"{ROADMAP}:{row.line}: v{version} is marked completed but git holds no tag "
            "for it, so no commit in its span maps to the release it went out in"
        )

    # Only a finding that a truncated checkout could have invented is withheld,
    # and only when there is one. Declining on `is_shallow` alone would silence
    # this check in every environment that matters - a web session's container
    # and `actions/checkout` both clone shallow - including the ones that have
    # since run `git fetch --tags` and can answer perfectly well.
    truncated = is_shallow(root)
    if absent and truncated is not False:
        report.declined.append(
            "release tags: "
            + (
                "the checkout is a shallow clone"
                if truncated
                else "git cannot say whether this checkout is complete"
            )
            + f", so the {_plural(len(absent), 'release', 'releases')} with no tag here "
            "cannot be told from a release whose tag was never fetched; "
            "`git fetch --tags` makes the question answerable"
        )
    else:
        report.errors.extend(absent)

    for version in sorted(untagged):
        if _is_tagged(version, existing):
            report.errors.append(
                f"{ROADMAP}:{claim_line}: v{version} is named as untagged, but git holds a "
                "tag for it"
            )

    for name in sorted(existing):
        match = RELEASE_TAG_RE.match(name)
        if match is None:
            continue
        version = match.group("version")
        if version not in completed:
            report.errors.append(
                f"{ROADMAP}: git holds {name}, but no row of the version table marks v{version} "
                "completed; a release that shipped is one this table has to name"
            )


def _project_version(pyproject: Path) -> str:
    match = re.search(r'^version\s*=\s*"([^"]+)"', pyproject.read_text(encoding="utf-8"), re.M)
    return match.group(1) if match else ""


def _is_path_citation(token: str) -> bool:
    if not token or not re.fullmatch(r"[\w./*{},-]+", token):
        return False
    if token.endswith("/"):
        return True
    return PurePosixPath(token).suffix in PATH_SUFFIXES


def _resolves(root: Path, basenames: frozenset[str], token: str) -> bool:
    patterned = "*" in token or "{" in token
    for prefix in PATH_ROOTS:
        base = root / prefix if prefix else root
        for candidate in _expand_braces(token):
            if patterned:
                if next(base.glob(candidate), None) is not None:
                    return True
            elif (base / candidate).exists():
                return True
    # A bare filename (`parameters.py`, `WORKING_NOTES.md`) is written without
    # a directory throughout the documentation; resolve it by name.
    return "/" not in token and token in basenames


def _headings(text: str) -> list[str]:
    return [
        match.group("title")
        for line in text.splitlines()
        if (match := HEADING_RE.match(line)) is not None
    ]


def _cites_heading(term: str, headings: Iterable[str]) -> bool:
    """Whether `term` names one of `headings`.

    Two tolerances, both for writing that is correct as written. A prefix
    ending on a word boundary counts, because prose shortens a long heading
    (`"Completed: v0.2.0"` for `Completed: v0.2.0 - isoflurane and
    desflurane`). And sentence punctuation closed inside the quotation marks
    is ignored, because `See "Known limitations."` is ordinary US style, not
    a citation of a heading that ends in a period. A rename still breaks the
    match, which is the drift being checked.
    """
    candidates = {term, term.rstrip(" .,;:")}
    return any(
        heading == candidate
        or (heading.startswith(candidate) and heading[len(candidate)] in " -:,;")
        for heading in headings
        for candidate in candidates
        if candidate
    )


def check_citations(root: Path, documents: dict[Path, str], report: Report) -> None:
    """Resolve every path and section a documentation file cites."""
    basenames = frozenset(path.name for path in _walk(root))
    headings = {path: _headings(text) for path, text in documents.items()}
    every_heading = [heading for titles in headings.values() for heading in titles]

    for path, text in documents.items():
        for match in CODE_SPAN_RE.finditer(text):
            token = match.group(1)
            if _is_path_citation(token) and not _resolves(root, basenames, token):
                report.errors.append(
                    f"{path}:{_line_of(text, match.start())}: cites `{token}`, which does not exist"
                )

        for match in LINK_RE.finditer(text):
            target = match.group("target")
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            relative, _, anchor = target.partition("#")
            line = _line_of(text, match.start())
            resolved = (root / path).parent / relative if relative else root / path
            if not resolved.exists():
                report.errors.append(f"{path}:{line}: links to {target}, which does not exist")
                continue
            if anchor:
                linked = resolved.relative_to(root)
                titles = headings.get(linked) or _headings(resolved.read_text(encoding="utf-8"))
                slugs = {re.sub(r"[^a-z0-9-]", "", h.lower().replace(" ", "-")) for h in titles}
                if anchor.lower() not in slugs:
                    report.errors.append(
                        f"{path}:{line}: links to {target}, but {linked} has no such heading"
                    )

        for match in CITATION_RE.finditer(text):
            term = match.group("named") or match.group("directed")
            line = _line_of(text, match.start())
            same_file = match.group("directed") is not None or DIRECTION_RE.match(
                text[match.end() : match.end() + 24]
            )
            if same_file:
                if not _cites_heading(term, headings[path]):
                    report.errors.append(
                        f'{path}:{line}: cites section "{term}" in this file, which has no '
                        "such heading"
                    )
            elif not _cites_heading(term, every_heading):
                report.errors.append(
                    f'{path}:{line}: cites section "{term}", which no documentation file has'
                )


def make_targets(text: str) -> tuple[frozenset[str], frozenset[str]]:
    """Every target a Makefile names, and the subset that carries a recipe.

    The two differ exactly where this check earns its place. A name listed in
    `.PHONY` but never given a recipe is still a target as far as `make` is
    concerned: it accepts the argument, prints "Nothing to be done", and exits
    0. Documentation that tells a session to run it is therefore naming a
    check that reports success without running, which is worse than one that
    errors - an erroring command gets investigated, a passing one gets
    believed.
    """
    declared: set[str] = set()
    with_recipe: set[str] = set()
    current: str | None = None
    for line in text.splitlines():
        if line.startswith("\t"):
            if current is not None:
                with_recipe.add(current)
            continue
        phony = PHONY_RE.match(line)
        if phony is not None:
            declared.update(phony.group("names").split())
            current = None
            continue
        match = MAKE_TARGET_RE.match(line)
        if match is not None:
            current = match.group("name")
            declared.add(current)
        elif line.strip():
            current = None
    return frozenset(declared), frozenset(with_recipe)


def _make_mentions(text: str) -> Iterator[tuple[str, int]]:
    """Every `make <target>` written as code, with the line it sits on."""
    for match in CODE_SPAN_RE.finditer(text):
        for mention in MAKE_MENTION_RE.finditer(match.group(1)):
            yield mention.group("name"), _line_of(text, match.start())
    for start, body in _fenced_blocks(text):
        for offset, line in enumerate(body):
            for mention in MAKE_MENTION_RE.finditer(line):
                yield mention.group("name"), start + offset + 1


def check_make_targets(root: Path, documents: dict[Path, str], report: Report) -> None:
    """Hold every documented `make` command to a target that actually runs.

    `make docket` was named by three documents for two releases while the
    recipe sat under the pre-rename target name, so the store validation those
    documents promised had not run once. The failure is silent by
    construction, which is what makes it worth a check rather than a reader's
    attention.
    """
    makefile = root / "Makefile"
    if not makefile.is_file():
        return
    declared, with_recipe = make_targets(makefile.read_text(encoding="utf-8"))
    for path, text in sorted(documents.items()):
        reported: set[tuple[str, int]] = set()
        for name, line in _make_mentions(text):
            if name in with_recipe or (name, line) in reported:
                continue
            reported.add((name, line))
            if name in declared:
                report.errors.append(
                    f"{path}:{line} names `make {name}`, which is declared but carries "
                    "no recipe, so it exits 0 without running"
                )
            else:
                report.errors.append(
                    f"{path}:{line} names `make {name}`, which the Makefile does not define"
                )


def workflow_commands(text: str) -> Iterator[tuple[str, int]]:
    """Every shell line a workflow's `run:` steps execute, with its line number."""
    lines = text.splitlines()
    index = 0
    while index < len(lines):
        match = RUN_STEP_RE.match(lines[index])
        index += 1
        if match is None:
            continue
        inline = match.group("inline").strip()
        if inline and inline not in BLOCK_SCALARS:
            yield inline, index
            continue
        indent = len(match.group("indent"))
        while index < len(lines):
            body = lines[index]
            if body.strip() and len(body) - len(body.lstrip()) <= indent:
                break
            index += 1
            if body.strip():
                yield body.strip(), index


def _command_paths(command: str) -> Iterator[str]:
    """Every token in a shell line that is written as a path."""
    for raw in COMMAND_SPLIT_RE.split(command):
        token = raw.strip("\"'`,")
        # `--cov=src/x` and `KEY=path` carry the path on the right of the `=`.
        if "=" in token:
            token = token.rpartition("=")[2].strip("\"'")
        token = token.removeprefix("./")
        if "/" not in token or token.startswith("-"):
            continue
        if any(mark in token for mark in UNRESOLVABLE):
            continue
        yield token


def check_workflow_paths(root: Path, report: Report) -> None:
    """Resolve every repository path a CI step runs.

    `tools/punch_list.py` was deleted with every documentation reference to it
    found and fixed, while the workflow step invoking it was missed and would
    have failed on merge. A broken CI reference is discovered at the worst
    possible moment - after review, on the merge - so it is held to the same
    standard as a path cited in prose.
    """
    workflows = sorted(
        path for pattern in WORKFLOW_GLOBS for path in root.glob(pattern) if path.is_file()
    )
    if not workflows:
        return
    # A token claims to be a repository path when its first segment names
    # something at the top of the checkout. That is what separates `bin/docket`
    # from `actions/checkout@v7.0.1`, and it is why the suffix rule in
    # `_is_path_citation` does not work here: `bin/docket` has no suffix, and
    # it is exactly the reference this check exists to hold.
    top_level = {child.name for child in root.iterdir()}
    for path in workflows:
        relative = path.relative_to(root)
        reported: set[tuple[str, int]] = set()
        for command, line in workflow_commands(path.read_text(encoding="utf-8")):
            for token in _command_paths(command):
                if PurePosixPath(token).parts[0] not in top_level:
                    continue
                if (token, line) in reported:
                    continue
                reported.add((token, line))
                if not (root / token).exists():
                    report.errors.append(f"{relative}:{line}: runs `{token}`, which does not exist")


def _without_code(text: str) -> list[str]:
    """Every line with its code blanked, so only prose reaches the math rules.

    Blanking rather than deleting keeps the line numbering true. Well-formed
    math spans are blanked too: they are correct by construction, and what the
    rules look for is the debris a malformed one leaves behind.
    """
    lines: list[str] = []
    fenced = False
    for line in text.splitlines():
        if ANY_FENCE_RE.match(line):
            fenced = not fenced
            lines.append("")
            continue
        if fenced:
            lines.append("")
            continue
        blank = MATH_SPAN_RE.sub(lambda m: " " * len(m.group(0)), line)
        lines.append(BACKTICK_RUN_RE.sub(lambda m: " " * len(m.group(0)), blank))
    return lines


def check_math_delimiters(root: Path, report: Report) -> None:
    """Hold every markdown file to the math syntax GitHub actually renders.

    Two failures, both silent: the wrong delimiters render as literal text, and
    a correct expression split across a source line break renders as literal
    text on both sides. Neither raises anything anywhere - the page simply
    shows `(F_D)` where it should show a symbol, which is a traceability
    failure in a document whose symbol table is how a reader maps a displayed
    clinical value back to the equation that produced it.

    Every markdown file is read, not only `DOC_GLOBS`: this is a question about
    rendering rather than about claims held to the tree, and a queue item
    renders on GitHub like anything else.
    """
    for path in _walk(root):
        if path.suffix != ".md":
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UNREADABLE:
            continue
        relative = path.relative_to(root)
        for number, line in enumerate(_without_code(text), 1):
            for match in TEX_DELIMITER_RE.finditer(line):
                report.errors.append(
                    f"{relative}:{number} writes math as `{match.group(0)}`, which GitHub "
                    "does not render; use `$`...`$` inline or a `$$` fence for a block"
                )
            for match in MATH_EDGE_RE.finditer(line):
                report.errors.append(
                    f"{relative}:{number} leaves `{match.group(0)}` unpaired, so an inline "
                    "expression is split across a line break and renders as literal text"
                )


def _frontmatter(text: str) -> list[str] | None:
    """The YAML frontmatter block's lines, or `None` if the file has none."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return lines[1:index]
    return None


def is_path_scoped(text: str) -> bool:
    """Does this rules file defer itself to the sessions that match its paths?

    A rule carrying `paths:` frontmatter loads when a session reads a matching
    file; one without it loads at launch with the same priority as
    `.claude/CLAUDE.md`. That distinction is the whole content of the resident
    total, so it is read here exactly as Claude Code documents it.
    """
    block = _frontmatter(text)
    return block is not None and any(PATHS_KEY_RE.match(line) for line in block)


def _measure(name: str, text: str) -> tuple[str, int] | None:
    """One resident file as its path and its line count, or `None` if deferred."""
    if name.startswith(f"{RULES_DIR}/") and is_path_scoped(text):
        return None
    return name, len(text.splitlines())


def measure_resident(root: Path) -> list[tuple[str, int]]:
    """Which instruction files load at launch in this working tree, and how big."""
    measured: list[tuple[str, int]] = []
    names = [name for name in RESIDENT_ROOTS if (root / name).is_file()]
    rules = root / RULES_DIR
    if rules.is_dir():
        names += sorted(
            path.relative_to(root).as_posix() for path in rules.rglob("*.md") if path.is_file()
        )
    for name in names:
        row = _measure(name, (root / name).read_text(encoding="utf-8"))
        if row is not None:
            measured.append(row)
    return measured


def _git_text(root: Path, *args: str) -> str | None:
    """Git's stdout verbatim, or `None` when it could not answer.

    `_git` drops blank lines, which is right for listing refs and wrong for
    counting the lines of a file, so the two readers are kept apart.
    """
    try:
        result = subprocess.run(
            ("git", *args), cwd=root, capture_output=True, text=True, timeout=10, check=False
        )
    except GIT_UNAVAILABLE:
        return None
    return None if result.returncode else result.stdout


def _resident_baseline(root: Path) -> tuple[str, tuple[tuple[str, int], ...]] | None:
    """The same measurement at the tip of the default branch.

    The tip rather than the merge base, because the question this answers is
    "does merging this make every session's resident context larger than it is
    on the default branch" - which a merge base cannot see, since it reports
    nothing when the growth arrived on the branch being merged into.
    """
    for ref in DEFAULT_BRANCHES:
        listing = _git_text(
            root, "ls-tree", "-r", "--name-only", ref, "--", *RESIDENT_ROOTS, RULES_DIR
        )
        if listing is None:
            continue
        measured: list[tuple[str, int]] = []
        for name in sorted(listing.splitlines()):
            if not name.endswith(".md"):
                continue
            text = _git_text(root, "show", f"{ref}:{name}")
            if text is None:
                continue
            row = _measure(name, text)
            if row is not None:
                measured.append(row)
        return ref, tuple(measured)
    return None


def check_resident_instructions(root: Path, report: Report) -> None:
    """Report what every session loads before it has read anything.

    Claude Code's memory documentation ties instruction-file size to adherence
    rather than to token cost: a long resident file makes every rule in it
    slightly less likely to be followed, the safety-critical standard among
    them. Nothing in this project's history ever shortened one - the rule that
    a behavior change takes effect in the session that asks for it guarantees
    growth, and PL-034's one-time trim regrew within a release.

    So the total is printed on every run and growth is named, which puts
    `PL-H7XN`'s routing question in front of whoever added the rule: at what
    moment does a session need this, and what is the cheapest thing that
    delivers it then - a check, the skill, a path-scoped rule, or resident.

    Reported, never thresholded, and this is the deliberate half. A limit would
    be met by deleting a rule to reach a number, which is the one outcome the
    routing pass must not produce; and no number this tool could hold would
    know which rules a session must see before it reads anything. Growth is a
    fact about the files; whether it is justified is not, so the judgment is
    left where `stranded` leaves its own.

    A net total cannot see the outcome a limit would have caused, though, which
    is why the second advisory exists. A change that adds resident text and
    trims other resident text to pay for it sums to nothing here, so the trim
    never appears as growth and the diff reads as free. That is the forbidden
    outcome arriving without a limit to blame, and it is decidable without
    judgment: growth and shrinkage in the same change, whatever they sum to.
    A routing pass that only moves text out still shrinks alone, and is still
    silent. `PL-BKQW` carries the reasoning; `PL-K6QR` records the project
    owner asking for text to be added without other text suffering for it.
    """
    files = measure_resident(root)
    if not files:
        return
    baseline = _resident_baseline(root)
    report.resident = ResidentInstructions(
        files=tuple(files),
        baseline_ref=None if baseline is None else baseline[0],
        baseline_files=None if baseline is None else baseline[1],
    )
    deltas = report.resident.deltas()
    if not deltas:
        return
    rendered = ", ".join(f"{name} {count:+d}" for name, count in deltas)
    ref = report.resident.baseline_ref
    growth = report.resident.growth
    if growth is not None and growth > 0:
        report.advisories.append(
            f"resident instructions grew {growth} lines against {ref} ({rendered}); every "
            "session loads this before it has read anything. Two answers, and there is no "
            "third: route it to the cheapest thing that delivers it when it is needed - a "
            "check, the `docket` skill, a path-scoped rule - or keep it and say why a "
            "session could violate it before it would look anything up. Text the project "
            "owner asked for is the second answer, already given. Never trim other "
            "resident text to offset the number. `PL-H7XN` carries the test."
        )
    if any(count > 0 for _, count in deltas) and any(count < 0 for _, count in deltas):
        report.advisories.append(
            f"resident instructions both grew and shrank against {ref} ({rendered}); the "
            "two net out in the total, so text cut to pay for an addition never shows up "
            "as growth at all. Check that the removed lines were routed somewhere a "
            "session still reads them, rather than cut to make room - making room is not "
            "one of the two answers to the growth advisory. `PL-BKQW` carries the test."
        )


def analyze(root: Path) -> Report:
    """Run every mechanical documentation check over a checkout."""
    report = Report()
    documents = read_docs(root)
    if not documents:
        report.errors.append("no documentation files found; is this a repository checkout?")
        return report
    check_package_maps(root, report)
    check_provenance(root, report)
    check_citations(root, documents, report)
    check_timeline(root, report)
    check_baseline(root, report)
    check_gate_counts(root, report)
    check_tags(root, report)
    check_make_targets(root, documents, report)
    check_workflow_paths(root, report)
    check_math_delimiters(root, report)
    check_resident_instructions(root, report)
    return report


def _plural(count: int, singular: str, plural: str) -> str:
    return f"{count} {singular if count == 1 else plural}"


def _format_resident(resident: ResidentInstructions) -> str:
    """One line: what every session loads, and how that compares to the base."""
    breakdown = ", ".join(f"{name} {count}" for name, count in resident.files)
    growth = resident.growth
    if growth is None:
        against = "no default branch here to compare against"
    elif growth > 0:
        against = f"{growth} more than {resident.baseline_ref}"
    elif growth < 0:
        against = f"{-growth} fewer than {resident.baseline_ref}"
    else:
        against = f"unchanged against {resident.baseline_ref}"
    return (
        f"resident instructions: {_plural(resident.total, 'line', 'lines')} "
        f"loaded at launch ({breakdown}) - {against}"
    )


def format_check(report: Report) -> str:
    summary = (
        "documentation: "
        f"{_plural(len(report.errors), 'error', 'errors')}, "
        f"{_plural(len(report.advisories), 'advisory', 'advisories')}"
    )
    if report.declined:
        summary += f", {len(report.declined)} not checked"
    lines = [summary]
    if report.resident is not None:
        lines.append(_format_resident(report.resident))
    if report.errors:
        lines.append("")
        lines.append("Errors (the documentation is wrong; fix before committing):")
        lines.extend(f"  {message}" for message in report.errors)
    if report.advisories:
        lines.append("")
        lines.append("Advisories (judgment needed):")
        lines.extend(f"  {message}" for message in report.advisories)
    if report.declined:
        lines.append("")
        lines.append("Not checked (this checkout cannot answer; nothing is claimed):")
        lines.extend(f"  {message}" for message in report.declined)
    if not report.errors and not report.advisories and not report.declined:
        lines.append(
            "Package map, provenance table, citations, release train, current "
            "baseline, release tags, documented make targets and CI paths all resolve."
        )
    return "\n".join(lines)


def _git(root: Path, *args: str) -> list[str]:
    # `git` is resolved through `PATH` rather than pinned, for the same reason
    # as docket's `vcs._run_git`: the path differs by environment, and a
    # checkout that cannot run git is answered with an empty list here rather
    # than treated as an error.
    result = subprocess.run(("git", *args), cwd=root, capture_output=True, text=True, check=False)
    if result.returncode:
        return []
    return [line for line in result.stdout.splitlines() if line.strip()]


# What a diff changes that documentation is likely to name: a definition, a
# data-file key, or the file itself.
DEFINITION_RE = re.compile(r"^[-+]\s*(?:async\s+)?(?:def|class)\s+(\w+)")
JSON_KEY_RE = re.compile(r'^[-+]\s*"(\w+)"\s*:')
REMOVED_HEADING_RE = re.compile(r"^-#{1,6}\s+(.+?)\s*#*\s*$")


def _changed_paths(root: Path, base: str) -> list[str]:
    paths = _git(root, "diff", "--name-only", base)
    paths += _git(root, "ls-files", "--others", "--exclude-standard")
    return sorted(set(paths))


def changed_tokens(root: Path, base: str, documents: Iterable[Path]) -> dict[str, set[str]]:
    """What each changed file gives the documentation a chance to contradict.

    A changed *source* file is named in prose by its filename or by a
    definition it declares, so those are the tokens to look for. A changed
    *documentation* file is different: what breaks is a cross-reference to a
    heading it no longer has, so a removed heading is the token. Searching a
    documentation file by its own name only reports that other documents link
    to it, which is true whether or not anything drifted.
    """
    docs = {str(path) for path in documents}
    tokens: dict[str, set[str]] = {}
    for relative in _changed_paths(root, base):
        diff = _git(root, "diff", "-U0", base, "--", relative)
        if relative in docs:
            found = {
                match.group(1)
                for line in diff
                if (match := REMOVED_HEADING_RE.match(line)) is not None
            }
        else:
            name = PurePosixPath(relative)
            found = {name.name, name.stem}
            for line in diff:
                for pattern in (DEFINITION_RE, JSON_KEY_RE):
                    if (match := pattern.match(line)) is not None:
                        found.add(match.group(1))
        tokens[relative] = {token for token in found if len(token) > 3}
    return tokens


def format_candidates(root: Path, base: str) -> str:
    """Print the documentation lines a close-out sweep would grep for."""
    documents = read_docs(root)
    tokens = changed_tokens(root, base, documents)
    if not tokens:
        return f"No changes against {base}; nothing to sweep."

    lines = [f"Documentation to review for the diff against {base}:", ""]
    total = 0
    for relative, wanted in tokens.items():
        # One entry per documentation line, however many tokens hit it, so a
        # rename does not print the same line a dozen times.
        hits: dict[tuple[Path, int], str] = {}
        for token in sorted(wanted):
            for doc, doc_text in documents.items():
                if doc == Path(relative):
                    continue
                for number, line in enumerate(doc_text.splitlines(), start=1):
                    if token in line:
                        hits.setdefault((doc, number), token)
        if not hits:
            continue
        total += len(hits)
        lines.append(f"  {relative}")
        lines.extend(
            f"    {doc}:{number}  ({token})" for (doc, number), token in sorted(hits.items())
        )
        lines.append("")

    if not total:
        lines.append("  Nothing in the documentation mentions anything this diff changed.")
        lines.append("")
    lines.append(
        "These are candidates, not findings: the mechanical half already ran in "
        "`check` mode. Read each line and decide whether it still states the truth."
    )
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("mode", choices=("check", "candidates"))
    parser.add_argument("--root", type=Path, default=None, help="path to the repository")
    parser.add_argument("--base", default="HEAD", help="candidates mode: revision to diff against")
    args = parser.parse_args(argv)

    root = (args.root or Path(__file__).resolve().parent.parent).resolve()

    if args.mode == "candidates":
        print(format_candidates(root, args.base))
        return 0

    report = analyze(root)
    print(format_check(report))
    return 1 if report.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
