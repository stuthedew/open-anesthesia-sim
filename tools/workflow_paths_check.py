"""Refuse a file whose side of the lane boundary nobody decided, or decided against its imports.

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
`tests/reference/` imports it. There is no test file in the tree the rule has
to guess about, which is what earns it a hard failure rather than an advisory:
whether a file imports a package is decidable, and only *whether the file
should exist* is not.

An import is the right question rather than a proxy for one. A test that
exercises the simulator has to import it; a test that exercises a `tools/`
script or a shell hook has nothing to import from `src/`. That is why the two
sets separate cleanly, and it is why the rule keeps working on files nobody has
written yet - the next `tools/` check's test will import `tools/`, not
`anesthesia_sim`, without anybody having decided to make it so.

**A support module is held to half the rule, because it has no such obligation
(`PL-12P8`).** A test file is one pytest collects; anything else under `tests/`
- a `conftest.py`, a constant or fixture builder the tests import, a harness
like `tests/benchmarks/frame_cost.py` - supports them, and imports what it
needs rather than what it serves, which can be nothing at all. So one direction
stays exact: a support module importing `anesthesia_sim` is built on the
simulator and is refused a `workflow_paths` entry, as a test would be. The
other is declined, and a module importing no `anesthesia_sim` sits wherever
`workflow_paths` puts it - the simulator's unless listed. Enforcing that
direction too told `PL-4GN8`'s one-constant `tests/reference/mass_balance_gate.py`
and `tests/conftest.py`, which selects Qt's headless platform for the product's
tests, to declare themselves apparatus. The conftest's entry then made an item
touching it and the Qt test it serves `crossing`, offered to neither lane - the
false entry in the file that draws the boundary which the check exists to
prevent, reached through its own remedy. The clean report counts the modules
left to the list, so what the check could not decide is said rather than
rounded off.

**A second list in the same file drifts the same way, so it is checked here
too (`PL-BBDD`).** `docket.toml`'s `gate_paths` names the files a delegated diff
may not touch, and `docs/worker.md` sends a reader there rather than restating
it, so the `ruff.toml` coverage is `tools/ruff.toml` and
`subprojects/docket/ruff.toml` named one by one - a hand-maintained list of
files that appear as `tools/` and the subprojects grow, which is exactly the
shape that drifted above. A missed one is silent in the
direction that hurts: `docket verify`'s "the checks themselves are unedited"
audit reads `gate_paths`, so an uncovered `ruff.toml` lets a delegated diff relax
the linter config that keeps these scripts parseable by the bare `python3` that
runs them, and the audit still reports ACCEPT. The rule is the same shape as the
one above and equally decidable: every `ruff.toml` in the tree must be covered by
some `gate_paths` entry.

**Outside `tests/`, a tracked path is placed by one list or the other, and a
path under neither is refused (`PL-8ZGY`).** `Item.lane` reads `workflow_paths`
alone and places every other path on the simulator's side, so a path's side
was a decision only where somebody had written one down, and an apparatus file
nobody listed crossed the boundary in silence: measured 2026-09-27,
`docs/resident-instructions.md` alone had set 22 items aside from both lanes,
none ever filed, and the root `conftest.py`, `docs/pr-bodies/` and the docket
launcher under `bin/` were in the same position. Six items had misread that one
default before the file was found. So `docket.toml` now carries
`product_paths` beside `workflow_paths` - the simulator's side, each entry with
its reason - and this check reads the tree the repository tracks and refuses
the shortest ancestor of any file that neither list reaches into, naming both
lines that would place it. Which list is the author's judgment; that nobody
has made it is a fact about two lists and a `git ls-files`, which is what earns
the refusal. Two entries are refused with it, being the two ways the record
itself goes wrong: one both lists cover, since the lists then disagree about a
side, and one no tracked file is under, since it places nothing - `.mailmap`
was listed for weeks with no such file in the tree. `tests/` is exempt from
the placement rule and from neither list's dead-entry rule, because its files
are decided above, one by one. Where `docket.toml` declares no `product_paths`
the rule declines, as the `gate_paths` rule below declines an absent list.

**Deliberately not decided here: which side a path belongs on, or anything
about the rest of either list.** Directory entries, what `product_paths` says
about `ROADMAP.md` or `docs/ARCHITECTURE.md`, whether `gate_paths` should hold
some file that is not a `ruff.toml`, and whether either boundary is drawn in
the right place at all are judgments, argued in `docket.toml`'s own comments. A
tool guessing at the rest would be the "worse than no tool" case `CLAUDE.md`
names.

**Invoked through `uv run python`, not bare `python3`.** It parses repository
source with `ast`, and `tests/` is free to use the language `.python-version`
pins, so it can only run under the project interpreter -
`tests/unit/test_tools_portability.py` states that rule and names
`contrast_check.py` and `import_boundary_check.py` as the other two. Like them,
this file itself imports only what that suite admits - the standard library,
and the in-tree `docket` package for `is_under` - and parses at the declared
floor, which is what keeps it in that suite's scope.
"""

from __future__ import annotations

import argparse
import ast
import fnmatch
import subprocess
import sys
import tomllib
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "subprojects" / "docket" / "src"))

from docket.model import is_under  # noqa: E402

#: Where this check looks. `subprojects/*/tests/` is out of scope: those trees
#: are already covered whole by the `subprojects` entry, so no file in them can
#: land on the product side by omission.
TESTS_DIR = Path("tests")

#: The store's own settings file, which holds the lists being checked.
CONFIG = Path("docket.toml")

#: Directories a checkout carries but does not author. Skipped by
#: `ruff_configs`, and by the walk that stands in for `git ls-files` in a tree
#: that is not a checkout.
SKIP_DIRS = frozenset(
    {".git", ".venv", "venv", "node_modules", "__pycache__", ".mypy_cache", ".ruff_cache"}
)

#: Importing this is what makes a test file the simulator's. Named once here
#: because the rule is about this package specifically, not about any import.
PRODUCT_PACKAGE = "anesthesia_sim"

#: What pytest collects as a test module: its default `python_files`, which
#: this repository does not override. Restated rather than read, and
#: `tests/unit/test_workflow_paths_check.py` compares it with the setting its
#: own run collected under, so a changed `python_files` fails a test instead
#: of quietly turning a new test into a support module.
TEST_FILE_PATTERNS = ("test_*.py", "*_test.py")


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


def imports_product(tree: ast.Module) -> bool:
    """Whether a file imports the simulator, which makes any file under `tests/` the simulator's."""
    return any(
        module == PRODUCT_PACKAGE or module.startswith(PRODUCT_PACKAGE + ".")
        for module in imported_modules(tree)
    )


def is_test_file(name: str) -> bool:
    """Whether pytest collects a file of this name, rather than it supporting what it collects."""
    return any(fnmatch.fnmatchcase(name, pattern) for pattern in TEST_FILE_PATTERNS)


def declared_workflow_paths(root: Path) -> tuple[str, ...]:
    """`[docket] workflow_paths` from the store's settings file."""
    with (root / CONFIG).open("rb") as handle:
        data = tomllib.load(handle)
    section = data.get("docket", {})
    return tuple(section.get("workflow_paths", ()))


def declared_product_paths(root: Path) -> tuple[str, ...]:
    """`[docket] product_paths` from the store's settings file, or empty where none is declared.

    Docket itself does not read this list: `Item.lane` places every path
    `workflow_paths` does not cover on the product side. The list exists so
    that placement is a decision this check can hold the tree to.
    """
    with (root / CONFIG).open("rb") as handle:
        data = tomllib.load(handle)
    section = data.get("docket", {})
    return tuple(section.get("product_paths", ()))


def declared_gate_paths(root: Path) -> tuple[str, ...]:
    """`[docket] gate_paths` from the store's settings file."""
    with (root / CONFIG).open("rb") as handle:
        data = tomllib.load(handle)
    section = data.get("docket", {})
    return tuple(section.get("gate_paths", ()))


def ruff_configs(root: Path) -> list[str]:
    """Every `ruff.toml` in the tree, as repository-relative paths.

    Skipping the directories a checkout carries but does not author. A
    `ruff.toml` vendored inside `.venv` is somebody else's file and naming it
    in `gate_paths` would be meaningless.
    """
    found = []
    for path in sorted(root.rglob("ruff.toml")):
        relative = path.relative_to(root)
        if any(part in SKIP_DIRS for part in relative.parts):
            continue
        found.append(relative.as_posix())
    return found


def gate_problems(root: Path) -> list[str]:
    """Every `ruff.toml` in the tree that no `gate_paths` entry covers."""
    roots = declared_gate_paths(root)
    if not roots:
        # Declined rather than failed. `docket.config` supplies package defaults
        # for an absent `gate_paths`, and this file may import the standard
        # library only, so a settings file that does not state the list is one
        # whose effective list this tool cannot read. Reporting "no gate_paths"
        # there would be a check answering a question it did not ask. This
        # repository states the list - the whole reason `docket.toml` writes out
        # values that are also defaults - so the rule fires where it matters.
        return []
    return [
        f"{relative} is a linter config no {CONFIG.as_posix()} gate_paths entry covers, so "
        f"`docket verify` would accept a delegated diff that relaxed it. Add "
        f'"{relative}" to gate_paths, or an entry covering it'
        for relative in ruff_configs(root)
        if not is_under(relative, roots)
    ]


def problems(root: Path) -> list[str]:
    """Every file under `tests/` whose declared side disagrees with what its imports decide.

    A support module importing no `anesthesia_sim` is never one: its imports
    decide nothing about its side, so the list's declaration stands either way.
    """
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
        product = imports_product(tree)
        covered = is_under(relative, roots)
        # A test file only: a support module that imports no product may
        # serve either side, and telling one to join the list is `PL-12P8`.
        if not product and not covered and is_test_file(path.name):
            found.append(
                f"{relative} imports no `{PRODUCT_PACKAGE}`, so it is apparatus, but "
                f"{CONFIG.as_posix()}'s workflow_paths does not cover it. An item "
                f"declaring it alongside the thing it tests lands in neither lane. "
                f'Add "{relative}" to workflow_paths'
            )
        elif product and covered:
            found.append(
                f"{relative} imports `{PRODUCT_PACKAGE}`, so it is the simulator's, "
                f"but {CONFIG.as_posix()}'s workflow_paths covers it. A product item "
                f"declaring it would be offered to a workflow session. Remove "
                f'"{relative}" from workflow_paths'
            )
    return found


def tracked_files(root: Path) -> list[str]:
    """Every file the repository tracks, as posix paths relative to `root`.

    `git ls-files` where `root` is a checkout, because an untracked file - a
    scratch script, a build product, a virtualenv - is nobody's to place. A
    tree that is not a checkout, which is what the tests build, is walked
    instead, skipping only `SKIP_DIRS`; that walk sees every file and stands
    in for git rather than replacing it. Git failing in a checkout is raised
    to the caller, which reports it: a tree this check could not list is one
    it cannot vouch for, and passing it silently is the failure the check
    exists to stop.
    """
    if (root / ".git").exists():
        completed = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z"],
            capture_output=True,
            check=True,
            encoding="utf-8",
        )
        return sorted(name for name in completed.stdout.split("\0") if name)
    found = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if path.is_file() and not any(part in SKIP_DIRS for part in relative.parts):
            found.append(relative.as_posix())
    return found


def unplaced_ancestor(relative: str, entries: tuple[str, ...]) -> str:
    """The shortest ancestor of an uncovered file that no entry reaches into.

    This is the line the reader would add. For `docs/references/README.md`
    with `docs/items` listed, it is `docs/references`: `docs` is a directory
    the lists already reach into, and naming it would cover what they place.
    For a file in a new top-level tree it is that tree's root, and for a root
    file it is the file.
    """
    parts = PurePosixPath(relative.strip("/")).parts
    for depth in range(1, len(parts) + 1):
        prefix = "/".join(parts[:depth])
        if not any(is_under(entry, (prefix,)) for entry in entries):
            return prefix
    return relative


def placement_problems(root: Path) -> list[str]:
    """Every tracked path outside `tests/` under neither list, and every entry that misplaces.

    An entry misplaces when both lists cover it, since they then disagree
    about a side, or when no tracked file is under it, since it then places
    nothing.

    Declined where `docket.toml` declares no `product_paths`: the rule needs
    both sides drawn, and a settings file that draws one is not this tool's to
    complete.
    """
    workflow = declared_workflow_paths(root)
    product = declared_product_paths(root)
    if not workflow or not product:
        return []
    found: list[str] = []
    for entry in product:
        if is_under(entry, workflow):
            found.append(
                f'"{entry}" is in product_paths, but workflow_paths covers it, so the two lists '
                f"disagree about its side. Remove it from one of them"
            )
    listed_as_product = {entry.strip().strip("/") for entry in product}
    for entry in workflow:
        # An entry both lists name verbatim was reported once already, above.
        if entry.strip().strip("/") not in listed_as_product and is_under(entry, product):
            found.append(
                f'"{entry}" is in workflow_paths, but product_paths covers it, so the two lists '
                f"disagree about its side. Remove it from one of them"
            )
    try:
        tracked = tracked_files(root)
    except (OSError, subprocess.CalledProcessError) as error:
        found.append(
            f"the tracked files could not be listed ({error}), so no path outside "
            f"{TESTS_DIR.as_posix()}/ can be vouched for"
        )
        return found
    entries = workflow + product
    unplaced: dict[str, int] = {}
    prefixes: set[str] = set()
    for relative in tracked:
        parts = PurePosixPath(relative).parts
        prefixes.update("/".join(parts[:depth]) for depth in range(1, len(parts) + 1))
        if parts[0] == TESTS_DIR.name:
            continue
        if is_under(relative, workflow) or is_under(relative, product):
            continue
        ancestor = unplaced_ancestor(relative, entries)
        unplaced[ancestor] = unplaced.get(ancestor, 0) + 1
    for ancestor, count in sorted(unplaced.items()):
        found.append(
            f'"{ancestor}" is tracked ({count} file(s)) and neither workflow_paths nor '
            f"product_paths in {CONFIG.as_posix()} places it, so an item declaring it lands on "
            f'the simulator\'s side by default rather than by a decision. Add "{ancestor}" to '
            f"workflow_paths if it exists so sessions can be productive, or to product_paths "
            f"if a reader of the simulator needs it"
        )
    for name, declared in (("workflow_paths", workflow), ("product_paths", product)):
        for entry in declared:
            if entry.strip().strip("/") not in prefixes:
                found.append(
                    f'"{entry}" is in {name}, but no tracked file is under it, so the entry '
                    f"places nothing. Remove it, or fix its spelling"
                )
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="repository to check")
    args = parser.parse_args()

    found = problems(args.root)
    placement = placement_problems(args.root)
    gate = gate_problems(args.root)
    if not found and not placement and not gate:
        roots = declared_workflow_paths(args.root)
        product = declared_product_paths(args.root)
        outside = sum(
            1 for name in tracked_files(args.root) if PurePosixPath(name).parts[0] != TESTS_DIR.name
        )
        files = sorted((args.root / TESTS_DIR).rglob("*.py"))
        tests = [path for path in files if is_test_file(path.name)]
        support = [path for path in files if not is_test_file(path.name)]
        apparatus = sum(
            1 for path in tests if is_under(path.relative_to(args.root).as_posix(), roots)
        )
        declared = sum(
            1
            for path in support
            if not imports_product(ast.parse(path.read_text(encoding="utf-8")))
        )
        print(
            f"workflow-paths: {len(tests)} test file(s) under {TESTS_DIR.as_posix()}, "
            f"{apparatus} of them apparatus, each on the side its imports put it; "
            f"{len(support)} support module(s), {declared} importing no `{PRODUCT_PACKAGE}` "
            f"and so on whichever side workflow_paths declares, which imports cannot "
            f"confirm; "
            + (
                f"{outside} tracked file(s) outside {TESTS_DIR.as_posix()}/, each under one of "
                f"{len(roots)} workflow_paths or {len(product)} product_paths entries; "
                if product
                else f"product_paths undeclared, so placement outside {TESTS_DIR.as_posix()}/ "
                f"was not checked; "
            )
            + f"{len(ruff_configs(args.root))} linter config(s), each covered by gate_paths"
        )
        return 0

    if found:
        print(
            f"workflow-paths: {len(found)} file(s) under {TESTS_DIR.as_posix()}/ on the "
            f"wrong side of the lane boundary.\n"
            + "".join(f"  {problem}\n" for problem in found)
            + "  A test file under tests/ is apparatus when it does not import "
            f"`{PRODUCT_PACKAGE}`, and the simulator's when it does. workflow_paths has "
            "to agree, or an item declaring one of these alongside the thing it tests is "
            "set aside from both lanes and offered to nobody (`PL-JBZK`). A support "
            "module, which pytest does not collect, is held to the second half only "
            "(`PL-12P8`).",
            file=sys.stderr,
        )
    if placement:
        print(
            f"workflow-paths: {len(placement)} path(s) outside {TESTS_DIR.as_posix()}/ that "
            f"neither list places, or entries that place nothing.\n"
            + "".join(f"  {problem}\n" for problem in placement)
            + "  A tracked path under neither workflow_paths nor product_paths is on the "
            "simulator's side by default rather than by a decision, and an item declaring it "
            "beside apparatus is set aside from both lanes as reaching both halves. Which "
            "list is yours to judge; that nobody has decided is what this refuses (`PL-8ZGY`).",
            file=sys.stderr,
        )
    if gate:
        print(
            f"workflow-paths: {len(gate)} linter config(s) no gate_paths entry covers.\n"
            + "".join(f"  {problem}\n" for problem in gate)
            + "  `docs/worker.md` forbids a delegated diff from editing any `ruff.toml`, "
            "and `docket verify` enforces that by reading gate_paths - so a config the "
            "list does not cover is one the audit will not defend (`PL-BBDD`).",
            file=sys.stderr,
        )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
