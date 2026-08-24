"""Deterministic checks for the documentation this repository must keep true.

`CLAUDE.md` requires a session to sweep the documentation before calling an
item done, because a reader who trusts a wrong statement about which module
runs, what a constant is, or where a file lives can reach a wrong clinical
conclusion from a correct number. That sweep is a grep over five documents
and a judgment on every hit, run at the end of a session, by hand. It leaks:
`weight_kg` sat out of the provenance table until someone noticed it.

Three of the failure modes the sweep looks for need no judgment at all, so
they are checked here and never left to a session to remember:

- **Package map.** Every module under `src/anesthesia_sim/` (and `tools/`)
  appears in the matching tree in `docs/ARCHITECTURE.md`, and every path
  those trees name still exists.
- **Provenance table.** Every scientific constant in a `data/**/*.json` file
  has exactly one row in `docs/MODEL.md`'s provenance table, and every row
  names a key that file actually holds, carrying the value the table states.
- **Citations.** Every repository path and every section heading cited from
  a documentation file resolves to something that exists.

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
runs in a bare checkout exactly as it runs in CI.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

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
    ".claude/skills/*/SKILL.md",
    "subprojects/*/README.md",
)

# Where the package map lives, and where the provenance table lives.
ARCHITECTURE = Path("docs/ARCHITECTURE.md")
MODEL = Path("docs/MODEL.md")

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
HEADING_RE = re.compile(r"^(?P<hashes>#{1,6})\s+(?P<title>.+?)\s*#*\s*$")
CODE_SPAN_RE = re.compile(r"`([^`\n]+)`")
LINK_RE = re.compile(r"\[[^\]\n]*\]\((?P<target>[^)\s]+)\)")
TABLE_ROW_RE = re.compile(r"^\|(?P<cells>.+)\|\s*$")
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


@dataclass
class Report:
    """Findings, split by whether a machine or a human has to resolve them."""

    errors: list[str] = field(default_factory=list)
    advisories: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class TreeMap:
    """One package-map tree, as drawn in `docs/ARCHITECTURE.md`."""

    root: PurePosixPath
    line: int
    files: frozenset[PurePosixPath]
    # Directories drawn without any children beneath them. Such an entry
    # stands for its whole subtree (`tools/review-verification/` is mapped as
    # one unit and documented by its own README), so files under it are
    # covered without being listed.
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


def _table_rows(text: str, heading: str) -> Iterator[tuple[int, list[str]]]:
    """Yield the rows of the first markdown table under `heading`."""
    lines = text.splitlines()
    in_section = False
    started = False
    for index, line in enumerate(lines, start=1):
        if line.startswith("## "):
            if started:
                return
            in_section = line[3:].strip() == heading
            continue
        if not in_section:
            continue
        match = TABLE_ROW_RE.match(line)
        if match is None:
            if started:
                return
            continue
        cells = [cell.strip() for cell in match.group("cells").split("|")]
        if all(set(cell) <= set("-: ") and cell for cell in cells):
            started = True
            continue
        if started:
            yield index, cells


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
    rows = list(_table_rows(path.read_text(encoding="utf-8"), "Parameter provenance"))
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
    return report


def _plural(count: int, singular: str, plural: str) -> str:
    return f"{count} {singular if count == 1 else plural}"


def format_check(report: Report) -> str:
    lines = [
        "documentation: "
        f"{_plural(len(report.errors), 'error', 'errors')}, "
        f"{_plural(len(report.advisories), 'advisory', 'advisories')}"
    ]
    if report.errors:
        lines.append("")
        lines.append("Errors (the documentation is wrong; fix before committing):")
        lines.extend(f"  {message}" for message in report.errors)
    if report.advisories:
        lines.append("")
        lines.append("Advisories (judgment needed):")
        lines.extend(f"  {message}" for message in report.advisories)
    if not report.errors and not report.advisories:
        lines.append("Package map, provenance table, and citations all resolve.")
    return "\n".join(lines)


def _git(root: Path, *args: str) -> list[str]:
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
