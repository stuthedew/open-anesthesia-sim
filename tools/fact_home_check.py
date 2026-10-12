"""Refuse a second reader of a fact the apparatus already answers, and say where the first is.

`CLAUDE.md` § "Architecture and development discipline" makes one source of
truth for a shared fact a hard principle of the code (project owner,
2026-10-12). Three generator heads stated it for the apparatus - `PL-PVW2`,
`PL-KGYT`, `PL-5DZ8` - and each closed on a sweep bounded by an enumeration
and re-entered, because nothing refused the next copy: a new tool that needs
git, the tree, the GitHub API or a Bash command's words wrote its own reader,
with its own timeout, decoding and error path, and the two then answered
differently at the moment one was trusted (`PL-4S6C`). This is the decidable
part of that principle, as `tools/literal_home_check.py` is for a number under
`src/`.

Two rules over every tracked Python file under `tools/`,
`subprojects/docket/src/docket/` and `.claude/hooks/`, read through
`tracked_files` so that this check is not itself a second reader of the tree:

1. **A primitive that produces a shared fact is read from its home.** `HOMES`
   names each one with the module that owns it and the reason, and a site
   outside the home is a finding: a `subprocess` call whose argv starts with
   `git`; a recursive walk of the tree - `os.walk`, `rglob`, a `**` glob;
   the GitHub API's host; a `main` or `origin/main` literal; `shlex.split` or
   `shlex.shlex`. A listing of one directory is not a walk, since it reads
   what a path holds and not what the repository holds, and `shlex.quote` and
   `shlex.join` write a command rather than read one.
2. **A module-level name is defined once.** An upper-case name bound at the
   top of two files is two spellings of one table - `ID_RE` in three files
   where `store.ID_PATTERN` is the record - or two facts that should not share
   a name; either way one of them changes. An alias of another module's name
   (`X = other.X`) is an import and not a definition. `EXEMPT_NAMES` holds the
   one name every tool must spell itself, with the reason.

Today's sites sit in `BASELINE`, keyed by file, rule and enclosing scope and
never by line, and it only shrinks: a count above an entry fails, and so does
an entry the tree no longer fills, so a copy a member removes cannot return
and the baseline cannot drift into a list nobody reads. The open members of
`PL-5DZ8` drain it; `PL-HNXS` and `PL-9NZ3` drained the walks they named, and
`PL-J4YY` the rest, moving the list into `docket.vcs` beside git's one runner;
`PL-S9JK` drained the tools' and `verify`'s own git runners into it.

Not read: the hooks written in shell, which call git directly and are held by
their own tests; the test trees, where a `git init` in a fixture reads no
shared fact; an argv built from a name (`[GIT, ...]`), which no site here
uses; a glob whose pattern is held in a name; and a walk written by hand over
`iterdir` or `scandir`, which this check reads as the listing it calls and not
the recursion around it - `doc_check._walk` was one until `PL-2P5L`. Nor this file,
whose tables spell the very literals the rules look for and whose baseline
names a scope called `main`. A file not yet added to git is not read until it
is, which is `tracked_files`'s trade and the one CI's run of this check
closes. A home is the whole file unless a scope is
named beside it. A hook can import docket - the Bash guards read it through
`shell_split`, which puts its `src` on the path (`PL-JNYL`, `PL-ZXCN`) - but
every guard pays its imports on every Bash call, so `stop_hook_patch.py`, which
imports none of it, keeps a git home of its own.

Standard library only and floor-parseable, like every tool under `tools/`,
and it reads trees that are held to the floor themselves, so both gates run
it bare: `python3 tools/fact_home_check.py` in `make check` and in
`quality.yml`'s floor section.
"""

from __future__ import annotations

import argparse
import ast
import re
from collections import Counter, defaultdict
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from workflow_paths_check import tracked_files

#: The trees held to both rules, as the repository-relative prefixes of their files.
TREES = ("tools/", "subprojects/docket/src/docket/", ".claude/hooks/")

#: The one file under them this check does not read: its own. See the docstring.
SELF = "tools/fact_home_check.py"

DOCKET = "subprojects/docket/src/docket/"
HOOKS = ".claude/hooks/"


@dataclass(frozen=True)
class Home:
    """One primitive that produces a shared fact, and the module that owns it."""

    rule: str
    #: What a site of it does, for the finding line.
    reads: str
    #: `(path, scope)` pairs; a scope of `None` is the whole file.
    where: tuple[tuple[str, str | None], ...]
    why: str
    remedy: str

    def holds(self, path: str, scope: str) -> bool:
        return any(
            path == home_path and (home_scope is None or _within(scope, home_scope))
            for home_path, home_scope in self.where
        )

    @property
    def named(self) -> str:
        return ", ".join(
            path if scope is None else f"`{scope}` in {path}" for path, scope in self.where
        )


def _within(scope: str, home_scope: str) -> bool:
    return scope == home_scope or scope.startswith(home_scope + ".")


HOMES: tuple[Home, ...] = (
    Home(
        rule="git",
        reads="runs git",
        where=((DOCKET + "vcs.py", None), (HOOKS + "stop_hook_patch.py", "_git")),
        why=(
            "`call_git` in `docket.vcs` is the one runner - it decodes a path as written, "
            "times out, and `_run_git` and `read_git` read its exit by one classification, "
            "which tells a silent repository from an empty answer - and every tool reaches "
            "docket, as `push-check-guard.sh` does on a push (`PL-ZXCN`); `_git` in "
            "`stop_hook_patch.py` is the runner of a hook that imports no docket"
        ),
        remedy=(
            "read git through `docket.vcs` - `call_git`, or `read_git` where a failure must "
            "raise - or through `stop_hook_patch._git` from a hook"
        ),
    ),
    Home(
        rule="walk",
        reads="walks the tree",
        where=((DOCKET + "vcs.py", "tracked_files"), (DOCKET + "grep.py", "_walk")),
        why=(
            "`tracked_files` asks git which files the repository holds and walks only a tree "
            "that is not a checkout, so a reader of it never sees another checkout under "
            "`.claude/worktrees/`, a virtualenv or a build product (`PL-HNXS`); `_walk` in "
            "`docket.grep` is the model of what `grep -r` reads, which is the disk, so a "
            "`verify:` command's grep is explained by the files it read (`PL-J4YY`)"
        ),
        remedy="read the files through `tracked_files`, or `tracked_under` for one subtree",
    ),
    Home(
        rule="github-api",
        reads="names the GitHub API's host",
        where=(("tools/open_pull_requests.py", None),),
        why=(
            "`open_pull_requests.py` is the one client, imported by five tools already; a "
            "second host string is a second place the API's version, headers and paging are "
            "spelled"
        ),
        remedy="read the API through `open_pull_requests`, adding the call there if it is new",
    ),
    Home(
        rule="default-branch",
        reads="names the default branch",
        where=((DOCKET + "vcs.py", None),),
        why=(
            "`vcs.default_base` prefers the remote's ref and marks an answer nothing "
            "established; a literal `main` is the local branch, which a fresh clone can hold "
            "many commits behind the remote"
        ),
        remedy="read `vcs.default_base`",
    ),
    Home(
        rule="shell-lexer",
        reads="lexes a shell command",
        where=((DOCKET + "shell.py", None), (HOOKS + "shell_split.py", None)),
        why=(
            "`docket.shell` reads a Bash command the way the hooks' guards must, and "
            "`shell_split.py` is the hooks' view of it, reading each command through "
            "`docket.shell` (`PL-JNYL`); "
            "`shlex` splits by a simpler grammar, so a command it reads differently is read "
            "two ways by one repository (`PL-C45K`)"
        ),
        remedy="read the command through `docket.shell`, or `shell_split` from a hook",
    ),
)

#: Rule 2's name in a finding and a baseline key.
DEFINITION = "definition"

#: Names rule 2 does not count, each with its reason.
EXEMPT_NAMES: dict[str, str] = {
    "ROOT": (
        "a tool's own location is the one fact it must read before it can import "
        "anything, and the expression depends on each file's own `__file__`"
    )
}

#: What rule 2 counts as a constant's name: upper case, two characters or more.
NAME_RE = re.compile(r"^_?[A-Z][A-Z0-9_]+$")

SUBPROCESS_CALLS = frozenset({"run", "check_output", "check_call", "call", "Popen"})
WALK_FUNCTIONS = frozenset({"walk", "fwalk"})
GLOB_FUNCTIONS = frozenset({"glob", "iglob"})
LEXER_FUNCTIONS = frozenset({"split", "shlex"})
GITHUB_HOST = "api.github.com"
DEFAULT_BRANCH_LITERALS = frozenset({"main", "origin/main", "refs/heads/main"})

#: Every second reader when this landed: file, then `(rule, enclosing scope)`,
#: then how many. It may only shrink.
BASELINE: dict[str, dict[tuple[str, str], int]] = {
    "subprojects/docket/src/docket/arming.py": {
        ("definition", "BEHIND"): 1,
        ("definition", "LANDED"): 1,
        ("definition", "RECORDS"): 1,
    },
    "subprojects/docket/src/docket/checks.py": {("definition", "SOFT_BREAK"): 1},
    "subprojects/docket/src/docket/claiming.py": {("definition", "ID"): 1, ("git", "_git"): 1},
    "subprojects/docket/src/docket/claims.py": {
        ("definition", "ID"): 1,
        ("definition", "RECORDS"): 1,
    },
    "subprojects/docket/src/docket/cli.py": {("shell-lexer", "_run_forge_command"): 1},
    "subprojects/docket/src/docket/frontmatter.py": {("definition", "FENCE"): 1},
    "subprojects/docket/src/docket/grep.py": {("definition", "MARKER"): 1},
    "subprojects/docket/src/docket/markdown.py": {
        ("definition", "FENCE"): 2,
        ("definition", "MARKER"): 1,
    },
    "subprojects/docket/src/docket/model.py": {("definition", "CONTINUATION_RE"): 1},
    "subprojects/docket/src/docket/notes.py": {("definition", "ID_RE"): 1},
    "subprojects/docket/src/docket/roadmap.py": {("definition", "UNPLACED"): 1},
    "subprojects/docket/src/docket/store.py": {("definition", "ID_RE"): 1},
    "subprojects/docket/src/docket/trend.py": {
        ("definition", "APPARATUS"): 1,
        ("definition", "UNPLACED"): 1,
    },
    "subprojects/docket/src/docket/vcs.py": {
        ("definition", "BEHIND"): 1,
        ("definition", "LANDED"): 1,
        ("definition", "UNPARSABLE"): 1,
    },
    "subprojects/docket/src/docket/verify.py": {
        ("definition", "ASSERTION_RE"): 1,
        ("definition", "UNPARSABLE"): 1,
    },
    "tools/agent_identity_check.py": {("definition", "APP"): 1},
    "tools/branch_sweep.py": {("git", "_git"): 1},
    "tools/contrast_check.py": {
        ("definition", "APP"): 1,
        ("definition", "EXEMPT"): 1,
        ("definition", "LINE_CITATION_RE"): 1,
    },
    "tools/dead_ends.py": {
        ("definition", "ITEMS"): 1,
        ("definition", "ITEM_ID"): 1,
        ("definition", "REPO"): 1,
    },
    "tools/doc_check.py": {
        ("definition", "ABSENT"): 1,
        ("definition", "APPARATUS"): 1,
        ("definition", "ASSERTION_RE"): 1,
        ("definition", "CONTINUATION_RE"): 1,
        ("definition", "JSON_KEY_RE"): 1,
        ("definition", "LINE_CITATION_RE"): 1,
        ("definition", "SOFT_BREAK"): 1,
    },
    "tools/fixture_id_check.py": {("definition", "JSON_KEY_RE"): 1, ("definition", "MARKER"): 1},
    "tools/generator_check.py": {("definition", "ID_RE"): 1},
    "tools/item_reads.py": {
        ("definition", "ITEMS"): 1,
        ("definition", "ITEM_ID"): 1,
        ("definition", "REPO"): 1,
    },
    "tools/literal_home_check.py": {("definition", "EXEMPT"): 1},
    "tools/main_ci_status.py": {
        ("definition", "API"): 1,
        ("definition", "TIMEOUT_S"): 1,
        ("git", "main"): 1,
        ("github-api", "<module>"): 1,
    },
    "tools/open_pull_requests.py": {("definition", "PAGE"): 1, ("git", "_git"): 1},
    "tools/pr_body_check.py": {
        ("definition", "API"): 1,
        ("definition", "TIMEOUT_S"): 1,
        ("github-api", "<module>"): 1,
    },
    "tools/required_checks_check.py": {
        ("definition", "API_VERSION"): 1,
        ("git", "_repo_from_git"): 1,
        ("github-api", "<module>"): 1,
    },
    "tools/tag_release.py": {("definition", "ABSENT"): 1, ("git", "_git"): 1},
    "tools/update_armed.py": {
        ("definition", "API"): 1,
        ("definition", "API_VERSION"): 1,
        ("definition", "PAGE"): 1,
        ("github-api", "<module>"): 1,
    },
}


@dataclass(frozen=True)
class Site:
    """One reader of a shared fact outside its home, or one definition of a shared name."""

    path: str
    line: int
    rule: str
    scope: str
    detail: str

    @property
    def key(self) -> tuple[str, str]:
        return (self.rule, self.scope)


@dataclass(frozen=True)
class Definition:
    """A module-level upper-case name and the file that binds it."""

    path: str
    line: int
    name: str

    @property
    def shared(self) -> str:
        return self.name.lstrip("_")


@dataclass(frozen=True)
class Module:
    """What one file contributes to each rule."""

    sites: tuple[Site, ...]
    definitions: tuple[Definition, ...]


class _Readers(ast.NodeVisitor):
    """Collects rule 1's sites with the dotted scope that encloses each."""

    def __init__(self, path: str) -> None:
        self.path = path
        self.scope: list[str] = []
        self.found: list[Site] = []
        self.docstrings: set[int] = set()
        #: Names bound by `from subprocess import run` and its kin, to their module.
        self.imported: dict[str, str] = {}

    def visit_Module(self, node: ast.Module) -> None:
        self._note_docstring(node)
        self.generic_visit(node)

    def _scoped(self, node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef) -> None:
        self._note_docstring(node)
        self.scope.append(node.name)
        self.generic_visit(node)
        self.scope.pop()

    visit_FunctionDef = _scoped
    visit_AsyncFunctionDef = _scoped
    visit_ClassDef = _scoped

    def _note_docstring(self, node: ast.AST) -> None:
        body = getattr(node, "body", None)
        if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
            if isinstance(body[0].value.value, str):
                self.docstrings.add(id(body[0].value))

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module in {"subprocess", "os", "glob", "shlex"}:
            for alias in node.names:
                self.imported[alias.asname or alias.name] = f"{node.module}.{alias.name}"

    def _callee(self, node: ast.Call) -> str | None:
        """`module.function` for a call this check reads, or `None`."""
        func = node.func
        if isinstance(func, ast.Attribute):
            if isinstance(func.value, ast.Name) and func.value.id in {
                "subprocess",
                "os",
                "glob",
                "shlex",
            }:
                return f"{func.value.id}.{func.attr}"
            return f"<any>.{func.attr}"
        if isinstance(func, ast.Name):
            return self.imported.get(func.id)
        return None

    def visit_Call(self, node: ast.Call) -> None:
        callee = self._callee(node)
        if callee is not None:
            module, _, function = callee.rpartition(".")
            if module == "subprocess" and function in SUBPROCESS_CALLS:
                argv = _argv(node)
                if argv is not None and _runs_git(argv):
                    self._record(node, "git", f'subprocess.{function}(["git", ...])')
            elif module == "os" and function in WALK_FUNCTIONS:
                self._record(node, "walk", f"os.{function}")
            elif function == "rglob":
                self._record(node, "walk", "rglob")
            elif module == "glob" and function in GLOB_FUNCTIONS and _recursive(node):
                self._record(node, "walk", f"glob.{function}")
            elif module == "<any>" and function == "glob" and _recursive(node):
                self._record(node, "walk", 'glob("**")')
            elif module == "shlex" and function in LEXER_FUNCTIONS:
                self._record(node, "shell-lexer", f"shlex.{function}")
        self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant) -> None:
        value = node.value
        if not isinstance(value, str) or id(node) in self.docstrings:
            return
        if GITHUB_HOST in value:
            self._record(node, "github-api", f'"{GITHUB_HOST}"')
        elif value in DEFAULT_BRANCH_LITERALS:
            self._record(node, "default-branch", f'"{value}"')

    def _record(self, node: ast.AST, rule: str, detail: str) -> None:
        scope = ".".join(self.scope) or "<module>"
        self.found.append(Site(self.path, getattr(node, "lineno", 0), rule, scope, detail))


def _argv(node: ast.Call) -> ast.expr | None:
    if node.args:
        return node.args[0]
    for keyword in node.keywords:
        if keyword.arg == "args":
            return keyword.value
    return None


def _runs_git(argv: ast.expr) -> bool:
    if isinstance(argv, (ast.List, ast.Tuple)) and argv.elts:
        first = argv.elts[0]
        return isinstance(first, ast.Constant) and first.value == "git"
    if isinstance(argv, ast.Constant) and isinstance(argv.value, str):
        return argv.value == "git" or argv.value.startswith("git ")
    return False


def _recursive(node: ast.Call) -> bool:
    """Whether a glob call reaches below its directory: a `**` pattern or `recursive=True`."""
    for keyword in node.keywords:
        if keyword.arg == "recursive":
            return isinstance(keyword.value, ast.Constant) and keyword.value.value is True
    pattern = node.args[0] if node.args else None
    return (
        isinstance(pattern, ast.Constant)
        and isinstance(pattern.value, str)
        and "**" in pattern.value
    )


def read_module(source: str, path: str) -> Module:
    """Both rules' view of one file.

    Args:
        source: The module's text.
        path: Its repository-relative path, which every finding carries.

    Raises:
        SyntaxError: The text does not parse.
    """
    tree = ast.parse(source, filename=path)
    visitor = _Readers(path)
    visitor.visit(tree)
    definitions: list[Definition] = []
    for statement in tree.body:
        if not isinstance(statement, (ast.Assign, ast.AnnAssign)) or statement.value is None:
            continue
        if isinstance(statement.value, (ast.Name, ast.Attribute)):
            continue  # an alias of a name defined elsewhere is an import, not a definition
        targets = statement.targets if isinstance(statement, ast.Assign) else [statement.target]
        for target in targets:
            if isinstance(target, ast.Name) and NAME_RE.match(target.id):
                if target.id.lstrip("_") not in EXEMPT_NAMES:
                    definitions.append(Definition(path, statement.lineno, target.id))
    return Module(tuple(visitor.found), tuple(definitions))


@dataclass(frozen=True)
class Overflow:
    """A file, rule and scope found more often than the baseline allows."""

    path: str
    key: tuple[str, str]
    allowed: int
    found: tuple[Site, ...]


@dataclass(frozen=True)
class Stale:
    """A baseline entry the tree no longer fills."""

    path: str
    key: tuple[str, str]
    allowed: int
    found: int
    missing: bool


@dataclass(frozen=True)
class Report:
    """Everything one run decided."""

    scanned: int
    readers: int
    allowed: int
    overflows: tuple[Overflow, ...]
    stale: tuple[Stale, ...]
    unparsed: tuple[tuple[str, str], ...]
    #: Every file that defines each shared name, for the finding's list.
    defined: Mapping[str, tuple[Definition, ...]]

    @property
    def errors(self) -> int:
        return len(self.overflows) + len(self.stale) + len(self.unparsed) + (self.scanned == 0)


def sources(root: Path) -> Iterator[str]:
    """Every tracked Python file under the trees, repository-relative, in a stable order."""
    for relative in tracked_files(root):
        if relative.endswith(".py") and relative.startswith(TREES) and relative != SELF:
            yield relative


def _home(rule: str) -> Home | None:
    return next((home for home in HOMES if home.rule == rule), None)


def analyze(root: Path, baseline: Mapping[str, Mapping[tuple[str, str], int]] = BASELINE) -> Report:
    """Evaluate both rules against the source on disk."""
    found: dict[str, Counter[tuple[str, str]]] = defaultdict(Counter)
    sites: dict[tuple[str, tuple[str, str]], list[Site]] = defaultdict(list)
    definitions: list[Definition] = []
    unparsed: list[tuple[str, str]] = []
    scanned = 0

    for relative in sources(root):
        scanned += 1
        try:
            module = read_module((root / relative).read_text(encoding="utf-8"), relative)
        except (SyntaxError, UnicodeDecodeError, ValueError) as error:
            unparsed.append((relative, str(error)))
            continue
        for site in module.sites:
            home = _home(site.rule)
            if home is not None and home.holds(site.path, site.scope):
                continue
            found[relative][site.key] += 1
            sites[(relative, site.key)].append(site)
        definitions.extend(module.definitions)

    by_name: dict[str, list[Definition]] = defaultdict(list)
    for definition in definitions:
        by_name[definition.shared].append(definition)
    defined = {
        name: tuple(entries)
        for name, entries in sorted(by_name.items())
        if len({entry.path for entry in entries}) > 1
    }
    for name, entries in defined.items():
        for entry in entries:
            site = Site(entry.path, entry.line, DEFINITION, name, f"{entry.name} = ...")
            found[entry.path][site.key] += 1
            sites[(entry.path, site.key)].append(site)

    overflows: list[Overflow] = []
    for (path, key), listed in sorted(sites.items()):
        allowed = baseline.get(path, {}).get(key, 0)
        if len(listed) > allowed:
            overflows.append(Overflow(path, key, allowed, tuple(listed)))

    unread = {path for path, _ in unparsed}
    stale: list[Stale] = []
    for path, expected in baseline.items():
        if path in unread:
            continue
        missing = not (root / path).is_file()
        for key, allowed in expected.items():
            count = 0 if missing else found[path][key]
            if count < allowed:
                stale.append(Stale(path, key, allowed, count, missing))

    return Report(
        scanned=scanned,
        readers=sum(sum(counts.values()) for counts in found.values()),
        allowed=sum(sum(entries.values()) for entries in baseline.values()),
        overflows=tuple(overflows),
        stale=tuple(stale),
        unparsed=tuple(unparsed),
        defined=defined,
    )


def format_report(report: Report) -> str:
    """Render a report the way `bin/docket check` renders one: verdict first."""
    lines = [
        f"fact homes: {report.scanned} modules read, {report.readers} second readers "
        f"against a baseline of {report.allowed}, {report.errors} errors"
    ]

    if report.scanned == 0:
        lines.append("")
        lines.append(f"No tracked Python files under {', '.join(TREES)} - the check read nothing.")
        lines.append(
            "  A moved tree or a listing git could not give leaves both rules passing over nothing."
        )

    if report.unparsed:
        lines.append("")
        lines.append("Not checked - these files do not parse, so what they read is unknown:")
        for path, error in report.unparsed:
            lines.append(f"  {path}: {error}")

    by_rule: dict[str, list[Overflow]] = defaultdict(list)
    for overflow in report.overflows:
        by_rule[overflow.key[0]].append(overflow)

    for home in HOMES:
        overflows = by_rule.get(home.rule)
        if not overflows:
            continue
        lines.append("")
        lines.append(f"A second reader outside its home - one that {home.reads}:")
        for overflow in overflows:
            for site in overflow.found:
                lines.append(f"  {site.path}:{site.line}: {site.detail} in {site.scope}")
            if overflow.allowed:
                lines.append(
                    f"    the baseline allows {overflow.allowed} of these in {overflow.key[1]}, "
                    f"and {len(overflow.found)} are there"
                )
        lines.append(f"  Home: {home.named}, because {home.why}.")
        lines.append(f"  So {home.remedy}; the baseline does not grow.")

    if by_rule.get(DEFINITION):
        lines.append("")
        lines.append("A name defined in more than one module:")
        named: set[str] = set()
        for overflow in by_rule[DEFINITION]:
            name = overflow.key[1]
            if name in named:
                continue
            named.add(name)
            where = ", ".join(f"{d.path}:{d.line} {d.name}" for d in report.defined[name])
            lines.append(f"  {name}: {where}")
        lines.append(
            "  Keep one definition and import it everywhere else; where they are two facts, "
            "name them apart. Two copies agree only until one is edited; the baseline does "
            "not grow."
        )

    if report.stale:
        lines.append("")
        lines.append(
            "Baselined but no longer there - lower the entry, so the count stays a ratchet:"
        )
        for entry in report.stale:
            rule, scope = entry.key
            if entry.missing:
                remedy = "the file no longer exists; delete its entries"
            elif entry.found:
                remedy = f"set it to {entry.found}"
            else:
                remedy = "delete it"
            lines.append(
                f"  {entry.path}, {rule} in {scope}: baseline {entry.allowed}, "
                f"found {entry.found} - {remedy}"
            )

    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.partition("\n")[0])
    parser.add_argument("--root", type=Path, default=None, help="path to the repository")
    args = parser.parse_args(argv)

    root = (args.root or Path(__file__).resolve().parent.parent).resolve()
    report = analyze(root)
    print(format_report(report))
    return 1 if report.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
