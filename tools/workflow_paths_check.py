"""Refuse a test file whose side of the lane boundary disagrees with what it imports.

`docket.toml`'s `workflow_paths` decides which half of the project an item
belongs to: `Item.lane()` reads each declared `touches` path against it, and an
item whose paths land on both sides is `crossing` - set aside by `docket next
workflow` and by `docket next product` alike, for a session that can hold the
whole change.

Most of that list is directories, which do not drift. The exceptions are the
`tests/unit/test_*.py` entries, which are named one by one because they are
apparatus tests wearing a product path: they exercise `tools/` scripts and
`.claude/` hooks, and only live in the simulator's test tree because that is
where pytest is configured to look.

**Named one by one, they drifted, which is what this check is for (`PL-JBZK`).**
The list held three when it was written. Nine more test files were in exactly
the same position by 2026-09-06 - the `tools/` scripts `branch_id_check`,
`ignore_check`, `pr_title_check` and `rules_paths_check`, the four
`.claude/hooks/` guards, and `test_tools_portability.py` - and two of the nine
had arrived the day before. So the list does not fall behind once and get
corrected; it falls behind continuously, at the rate `tools/` grows, and every
gap is silent. `PL-8XPQ` is the shape of the loss: an item declaring
`tools/glyph_check.py`, `tests/unit/test_glyph_check.py` and `Makefile` touches
no product code at all, and would be set aside from both lanes by a filename.

**The rule, and why it can be a check rather than a judgment.** A test file
under `tests/` is apparatus when it does not import the product package, and
product when it does. Measured against this repository on 2026-09-06 the
partition is exact and unanimous: 26 of the 38 files under `tests/unit/` import
`anesthesia_sim` and none of those touches `tools/` or `.claude/` as anything
but fixture text, while the 12 that do not import it are precisely the twelve
apparatus tests, and every file under `tests/integration/` and
`tests/reference/` imports it. There is no file in the tree the rule has to
guess about, which is what earns it a hard failure rather than an advisory:
whether a file imports a package is decidable, and only *whether the file
should exist* is not.

An import is the right question rather than a proxy for one. A test that
exercises the simulator has to import it; a test that exercises a `tools/`
script or a shell hook has nothing to import from `src/`. That is why the two
sets separate cleanly, and it is why the rule keeps working on files nobody has
written yet - the next `tools/` check's test will import `tools/`, not
`anesthesia_sim`, without anybody having decided to make it so.

**Deliberately not decided here: anything about the rest of the list.**
Directory entries, what `workflow_paths` says about `ROADMAP.md` or
`docs/ARCHITECTURE.md`, and whether the boundary is drawn in the right place at
all are judgments, argued in `docket.toml`'s own comments. This check reads only
the files under `tests/`, and only asks whether each one's side matches what its
imports say. A tool guessing at the rest would be the "worse than no tool" case
`CLAUDE.md` names.

**Invoked through `uv run python`, not bare `python3`.** It parses repository
source with `ast`, and `tests/` is free to use the language `.python-version`
pins, so it can only run under the project interpreter -
`tests/unit/test_tools_portability.py` states that rule and names
`contrast_check.py` and `import_boundary_check.py` as the other two. Like them,
this file itself imports only the standard library and parses at the declared
floor, which is what keeps it in that suite's scope.
"""

from __future__ import annotations

import argparse
import ast
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: Where this check looks. `subprojects/*/tests/` is out of scope: those trees
#: are already covered whole by the `subprojects` entry, so no file in them can
#: land on the product side by omission.
TESTS_DIR = Path("tests")

#: The store's own settings file, which holds the list being checked.
CONFIG = Path("docket.toml")

#: Importing this is what makes a test file the simulator's. Named once here
#: because the rule is about this package specifically, not about any import.
PRODUCT_PACKAGE = "anesthesia_sim"


def imported_modules(tree: ast.Module) -> set[str]:
    """Every module name one file imports, in either import form.

    `ast` rather than a regular expression because the question is about
    imports and not about text: a package named in a docstring, in a fixture
    path or in a comment is not a dependency, and several of the apparatus
    tests here write `src/anesthesia_sim/...` as fixture data precisely because
    they check tools that read the tree.
    """
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            found.add(node.module)
    return found


def is_apparatus(tree: ast.Module) -> bool:
    """Whether this test file exercises the apparatus rather than the simulator."""
    return not any(
        module == PRODUCT_PACKAGE or module.startswith(PRODUCT_PACKAGE + ".")
        for module in imported_modules(tree)
    )


def is_covered(path: str, roots: tuple[str, ...]) -> bool:
    """Whether one path falls inside any of `roots`, as `workflow_paths` reads it.

    The same `/`-separated prefix comparison as `docket.model.is_under`, which
    is what actually assigns the lane. Restated here rather than imported
    because every tool in this directory may depend on the standard library
    only, so that a bare checkout can run it; `tests/unit/test_tools_portability.py`
    is the rule. The duplication is pinned instead by
    `tests/unit/test_workflow_paths_check.py`, which imports both and asserts
    they agree on this repository's own list - so a change to one that the
    other does not follow fails a test rather than going unnoticed.
    """
    candidate = path.strip().strip("/")
    for root in roots:
        target = root.strip().strip("/")
        if not target:
            continue
        if candidate == target or candidate.startswith(target + "/"):
            return True
    return False


def declared_workflow_paths(root: Path) -> tuple[str, ...]:
    """`[docket] workflow_paths` from the store's settings file."""
    with (root / CONFIG).open("rb") as handle:
        data = tomllib.load(handle)
    section = data.get("docket", {})
    return tuple(section.get("workflow_paths", ()))


def problems(root: Path) -> list[str]:
    """Every test file whose declared side disagrees with what it imports."""
    roots = declared_workflow_paths(root)
    if not roots:
        return [
            f"{CONFIG.as_posix()} declares no workflow_paths, so every item is "
            f"unplaced and no lane can be answered"
        ]

    found: list[str] = []
    for path in sorted((root / TESTS_DIR).rglob("*.py")):
        relative = path.relative_to(root).as_posix()
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=relative)
        except SyntaxError as error:
            # Reported rather than skipped: a file this check cannot read is a
            # file whose side it cannot vouch for, and passing it silently is
            # the failure the check exists to stop.
            found.append(f"{relative} could not be parsed, so its side is unknown: {error}")
            continue
        apparatus = is_apparatus(tree)
        covered = is_covered(relative, roots)
        if apparatus and not covered:
            found.append(
                f"{relative} imports no `{PRODUCT_PACKAGE}`, so it is apparatus, but "
                f"{CONFIG.as_posix()}'s workflow_paths does not cover it. An item "
                f"declaring it alongside the thing it tests lands in neither lane. "
                f'Add "{relative}" to workflow_paths'
            )
        elif not apparatus and covered:
            found.append(
                f"{relative} imports `{PRODUCT_PACKAGE}`, so it is the simulator's, "
                f"but {CONFIG.as_posix()}'s workflow_paths covers it. A product item "
                f"declaring it would be offered to a workflow session. Remove "
                f'"{relative}" from workflow_paths'
            )
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="repository to check")
    args = parser.parse_args()

    found = problems(args.root)
    if not found:
        total = sum(1 for _ in (args.root / TESTS_DIR).rglob("*.py"))
        roots = declared_workflow_paths(args.root)
        apparatus = sum(
            1
            for path in (args.root / TESTS_DIR).rglob("*.py")
            if is_covered(path.relative_to(args.root).as_posix(), roots)
        )
        print(
            f"workflow-paths: {total} test file(s) under {TESTS_DIR.as_posix()}, "
            f"{apparatus} of them apparatus, each on the side its imports put it"
        )
        return 0

    print(
        f"workflow-paths: {len(found)} test file(s) on the wrong side of the lane "
        f"boundary.\n" + "".join(f"  {problem}\n" for problem in found) + "  A test "
        "file under tests/ is apparatus when it does not import "
        f"`{PRODUCT_PACKAGE}`, and the simulator's when it does. workflow_paths has "
        "to agree, or an item declaring one of these alongside the thing it tests is "
        "set aside from both lanes and offered to nobody (`PL-JBZK`).",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
