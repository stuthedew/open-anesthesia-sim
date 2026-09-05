"""The bare-interpreter scripts must stay runnable by the interpreter that runs them.

Two directories qualify, for one reason. `tools/` is invoked by `make check`
and CI; `.claude/hooks/` is invoked by Claude Code, which runs
`python3 "$CLAUDE_PROJECT_DIR/.claude/hooks/stop_hook_patch.py"` at session
start. Neither goes through the project virtualenv, so both carry a `ruff.toml`
pinning the formatter to the floor and both are covered here. `PL-W4H9` moved
the hook out of `tools/`, and covering it by directory rather than by name is
what keeps the next one from arriving unguarded.

`make check` invokes `python3 tools/doc_check.py check` with whatever bare
`python3` is on PATH - no virtualenv, no install step - and CI does the same.
This suite, by contrast, runs under the project virtualenv on the version
`pyproject.toml` requires, so a tool that has become unparseable by the older
interpreter passes every test and fails only at the end of `make check`, with a
`SyntaxError` in a file nothing appeared to have touched.

That is not hypothetical. The repository targets 3.14, where PEP 758 makes the
parentheses in `except (OSError, TimeoutError):` redundant; `ruff format` at
that target removes them, and 3.11 cannot parse the result.
`subprojects/docket/` was broken this exact way once and now carries its own
`ruff.toml` and `tests/test_portability.py`. `tools/` makes the same promise
and, until this file, had the same exposure with the guard written for one file
and one construct.

Four checks. Three approximate the bare-interpreter run cheaply enough to sit
in `make check` before a push: the formatter target agrees with the declared
floor, every file here parses at it, and nothing here imports a package that
exists only inside the project virtualenv. The fourth holds
`.github/workflows/quality.yml`'s `floor` job to that same declared floor -
that job *performs* the run the other three approximate, so it, and not they,
is what proves the promise.

The approximations stay because they are not redundant: they name the offending
file, import or construct where a traceback from CI would not, they run before
a push rather than after one, and they reach a file or a lazily-imported branch
that job's two commands never touch.
"""

from __future__ import annotations

import ast
import re
import sys
import tomllib
from collections.abc import Iterator
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
#: The directories whose `*.py` runs under bare `python3`. Each declares its
#: own `ruff.toml`, and both are held to the floor below.
BARE_ROOTS = (REPO_ROOT / "tools", REPO_ROOT / ".claude" / "hooks")
SOURCES = sorted(path for root in BARE_ROOTS for path in root.rglob("*.py"))

#: Importable here despite not being in the standard library, because a bare
#: checkout carries it too. `tools/doc_check.py` reads the release-train
#: grammar and the tag list from `docket`, in-tree under
#: `subprojects/docket/src` and itself standard-library-only, by inserting that
#: path rather than by installing anything. Anything else added to this set
#: has to meet the same bar: present in a fresh clone, and no dependencies of
#: its own outside the standard library.
VENDORED = frozenset({"docket"})


def _bare_python_floor() -> tuple[int, int]:
    """The oldest interpreter anything under `tools/` may assume.

    Read from `subprojects/docket/pyproject.toml` rather than declared again
    here: `tools/doc_check.py` imports `docket.roadmap`, so the interpreter that
    can run the tools is exactly the interpreter that can run that package.
    Raising the floor there raises it here, and reading it is what keeps the two
    from drifting apart the way the guard itself did.
    """
    with (REPO_ROOT / "subprojects" / "docket" / "pyproject.toml").open("rb") as handle:
        requires = tomllib.load(handle)["project"]["requires-python"]
    match = re.search(r">=\s*(\d+)\.(\d+)", requires)
    assert match is not None, requires
    return int(match.group(1)), int(match.group(2))


def _ruff_target(root: Path) -> tuple[int, int]:
    """The Python version the formatter may emit syntax for under `root`.

    Resolved through `extend`, because `.claude/hooks/ruff.toml` inherits the
    pin from `tools/ruff.toml` rather than restating it: reading only the local
    key would report the inheriting config as declaring no target at all.
    """
    while True:
        with (root / "ruff.toml").open("rb") as handle:
            config = tomllib.load(handle)
        if "target-version" in config:
            break
        root = (root / config["extend"]).resolve().parent
    match = re.fullmatch(r"py(\d)(\d+)", config["target-version"])
    assert match is not None, config["target-version"]
    return int(match.group(1)), int(match.group(2))


def test_the_formatter_target_matches_the_declared_floor() -> None:
    """A formatter aimed past the floor rewrites the source into syntax it cannot run.

    Asked of every bare-interpreter directory, so a second one cannot be added
    with the repository's own 3.14 target left in force.
    """
    for root in BARE_ROOTS:
        assert _ruff_target(root) == _bare_python_floor(), root


def test_there_are_sources_to_check() -> None:
    assert SOURCES, "no bare-interpreter scripts found; the glob is wrong"
    for root in BARE_ROOTS:
        assert any(path.is_relative_to(root) for path in SOURCES), root


def test_every_tool_parses_under_the_interpreter_that_actually_runs_it() -> None:
    """Every file under every bare-interpreter directory, not the one that broke.

    `feature_version` is not a full older-interpreter parser - it gates the
    syntax CPython's own parser version-checks, PEP 758 among them - so this
    catches the rewrite that has actually happened here rather than proving
    compatibility in general. Proof for the files the `floor` job runs is that
    job parsing them for real; this covers every file under `tools/` and
    `.claude/hooks/`, including the ones that job never invokes.
    """
    floor = _bare_python_floor()

    for path in SOURCES:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path), feature_version=floor)


def _imported_roots(tree: ast.Module) -> Iterator[str]:
    """The top-level module name of every absolute import in `tree`.

    `import a.b` and `from a.b import c` both reach `a`, which is the name that
    has to be resolvable; the submodule cannot be present without it. Relative
    imports are skipped: `tools/` is a directory of scripts with no package
    around them, so a relative import there resolves to nothing and fails on
    the first run rather than only in a bare checkout, which is the failure
    this test exists to catch.
    """
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name.split(".")[0]
        elif isinstance(node, ast.ImportFrom) and node.level == 0:
            yield (node.module or "").split(".")[0]


def test_no_tool_imports_outside_the_standard_library() -> None:
    """The no-dependency promise is what lets a bare checkout run these.

    `make check` ends with `python3 tools/doc_check.py check` under whatever
    interpreter is on PATH, with no virtualenv and no install step, so an
    import satisfied only by `uv sync` turns that line into a
    `ModuleNotFoundError` in a file the whole suite has just passed - the
    import twin of the `SyntaxError` above.

    `sys.stdlib_module_names` rather than a hand-written allowlist: it is a
    frozenset the interpreter maintains, so nothing here goes stale as the
    standard library grows. It answers for the interpreter running this test
    and not for the floor, so a module added to the standard library between
    the two passes here - `annotationlib` and `compression`, at 3.14 against a
    3.11 floor. That is a bound rather than a hole: the `floor` job imports the
    tools at the floor for real and decides outright what this frozenset can
    only approximate. What is left to this test is naming the file and the
    import, and covering what that job's two commands never reach.
    """
    allowed = sys.stdlib_module_names | VENDORED

    for path in SOURCES:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for root in _imported_roots(tree):
            assert root in allowed, (
                f"{path.relative_to(REPO_ROOT)} imports '{root}', which is neither in the "
                f"standard library nor in-tree; `python3 {path.relative_to(REPO_ROOT)}` "
                "cannot run in a checkout with no virtualenv"
            )


# A concrete `major.minor` pin. `3.x` and friends are deliberately not matched:
# `drift.yml` pins `'3.x'` to run on the *newest* interpreter, which is the whole
# point of that job, and holding it to the floor would invert it.
CONCRETE_PIN_RE = r"""^\s*python-version:\s*['"]?([0-9]+\.[0-9]+)['"]?\s*$"""


def _concrete_pins(workflow: Path) -> list[str]:
    """Every concrete `python-version:` pin in one workflow file.

    Read with a regular expression rather than a YAML parser, for the reason
    `tools/doc_check.py` gives for the same choice: nothing in the standard
    library reads YAML, and one key's value is not worth a dependency. The
    pattern is anchored to a whole line so that a job's comment about
    deliberately *not* setting this input cannot match.
    """
    return re.findall(CONCRETE_PIN_RE, workflow.read_text(encoding="utf-8"), re.MULTILINE)


def _workflows() -> list[Path]:
    found = sorted((REPO_ROOT / ".github" / "workflows").glob("*.yml"))
    assert found, "no workflows found; the glob is wrong"
    return found


def _ci_floor_pin() -> str:
    """The Python version `.github/workflows/quality.yml` installs for its `floor` job."""
    pins = _concrete_pins(REPO_ROOT / ".github" / "workflows" / "quality.yml")
    assert len(pins) == 1, f"expected exactly one python-version pin in the workflow, found {pins}"
    return pins[0]


def test_the_ci_floor_job_pins_the_declared_floor() -> None:
    """The job that proves the promise has to be running the interpreter it is about.

    Raising `requires-python` in `subprojects/docket/pyproject.toml` without
    touching the workflow would leave CI exercising an interpreter the project
    no longer supports, and the new floor guarded by nothing - the same drift
    the formatter-target check above exists to catch, one layer out.

    Exactly one pin, deliberately: the `checks` job sets no `python-version`
    input, because doing so would set `UV_PYTHON` and override
    `.python-version`. A second pin appearing anywhere in this file means that
    invariant has been broken or a third job has arrived unexamined, and either
    is worth stopping for.
    """
    major, minor = _bare_python_floor()

    assert _ci_floor_pin() == f"{major}.{minor}"


def test_every_concrete_workflow_pin_is_the_declared_floor() -> None:
    """One pin held to the floor is not enough once there is more than one workflow.

    `PL-79N5` is why this exists. `PL-3V8K` split the pull-request title check
    into its own workflow and dropped `uv` with it, correctly, since the script
    is standard library only - but that left it running on whatever interpreter
    the runner image shipped, under neither `.python-version` nor the floor.
    Pinning it fixes that and introduces a *second* constant that can drift from
    `subprojects/docket/pyproject.toml`, which is the defect one layer out.

    The predecessor of this test read `quality.yml` alone, so a pin anywhere
    else was unheld by construction. This reads every workflow, which also means
    a workflow added later is covered without anyone remembering to come here.

    Only concrete `major.minor` pins are held. `drift.yml` pins `3.x` to run on
    the newest interpreter available, which is that job's entire purpose.
    """
    floor = "{}.{}".format(*_bare_python_floor())

    offenders = {
        workflow.name: pins
        for workflow in _workflows()
        if (pins := [pin for pin in _concrete_pins(workflow) if pin != floor])
    }

    assert not offenders, (
        f"every concrete python-version pin must be the declared floor {floor}; found {offenders}"
    )
