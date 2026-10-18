"""Tests for `app/stylesheets.py`: each stylesheet composed in one place, and no toolkit there.

`PL-Y4YX` moved the ten composers the view modules held into one module beside
`app/theme.py` and kept the toolkit out of both (project owner, 2026-10-03,
ratified). Two properties make that more than a file move, and each is held
here: the module imports with no toolkit loaded, which is why it could sit
beside the theme at all, and every stylesheet a widget under `app/` is given is
a call to one of its composers, which is what making each visual decision once
means in the tree. What the strings draw is held where a widget is built to
show it, in `tests/integration/`.
"""

import ast
import inspect
import subprocess
import sys
from pathlib import Path

from anesthesia_sim.app import stylesheets, theme

#: The interface's package directory, which every module styling a widget is in.
APP = Path(stylesheets.__file__).parent

#: The packages the interface's toolkit arrives as.
TOOLKIT_PACKAGES = frozenset({"PySide6", "shiboken6", "pyqtgraph"})

#: Every function the module defines, which is every composer it offers.
COMPOSERS = frozenset(
    name
    for name, member in inspect.getmembers(stylesheets, inspect.isfunction)
    if member.__module__ == stylesheets.__name__
)

#: The modules that style a widget today. Held so that the walk below cannot
#: pass by reading nothing, which a moved package or a renamed method would do.
STYLING_MODULES = frozenset(
    {"qt_chart.py", "qt_widgets.py", "run_surfaces.py", "run_view.py", "simulation_view.py"}
)


def test_the_composers_import_with_no_toolkit_loaded() -> None:
    """A fresh interpreter imports the module, and the theme under it, and holds no toolkit.

    Run apart from this session, which the integration tests have already
    loaded PySide6 into, so that what is measured is what the import itself
    costs - including anything `app/theme.py` imports on its behalf.
    """

    loaded = subprocess.run(
        [
            sys.executable,
            "-c",
            "import sys\n"
            "import anesthesia_sim.app.stylesheets\n"
            "print('\\n'.join(sorted({name.split('.')[0] for name in sys.modules})))",
        ],
        capture_output=True,
        check=True,
        text=True,
    ).stdout.split()

    assert "anesthesia_sim" in loaded
    assert TOOLKIT_PACKAGES.isdisjoint(loaded), sorted(TOOLKIT_PACKAGES.intersection(loaded))


def test_the_module_imports_nothing_but_the_theme_and_the_standard_library() -> None:
    """An import inside a composer would load the toolkit after the import above had passed.

    It could name the toolkit, or a view module that imports it, so what is
    bounded is everything the module imports rather than the toolkit's names.
    """

    tree = ast.parse(Path(stylesheets.__file__).read_text(encoding="utf-8"))
    imported = {
        name.name for node in ast.walk(tree) if isinstance(node, ast.Import) for name in node.names
    } | {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }
    beyond = {
        module
        for module in imported
        if module != theme.__name__ and module.split(".")[0] not in sys.stdlib_module_names
    }

    assert not beyond, sorted(beyond)


def _composer_names(tree: ast.Module) -> frozenset[str]:
    """The names a module imports composers under, less any it also binds to something else."""

    imported = {
        alias.asname or alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module == stylesheets.__name__
        for alias in node.names
        if alias.name in COMPOSERS
    }
    rebound: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
            rebound.add(node.name)
        elif isinstance(node, ast.arg):
            rebound.add(node.arg)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            rebound.add(node.id)
        elif isinstance(node, ast.Import) or (
            isinstance(node, ast.ImportFrom) and node.module != stylesheets.__name__
        ):
            rebound.update(alias.asname or alias.name for alias in node.names)

    return frozenset(imported - rebound)


def _stylesheet_writes(tree: ast.Module) -> list[tuple[int, ast.expr | None]]:
    """Each stylesheet a module gives a widget, with its line, or None where its shape is not one.

    Qt takes one three ways: `setStyleSheet`, the `styleSheet=` keyword its
    constructors accept, and `setProperty("styleSheet", ...)`.
    """

    writes: list[tuple[int, ast.expr | None]] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        method = node.func.attr if isinstance(node.func, ast.Attribute) else None
        if method == "setStyleSheet":
            writes.append((node.lineno, node.args[0] if len(node.args) == 1 else None))
        elif (
            method == "setProperty"
            and node.args
            and isinstance(node.args[0], ast.Constant)
            and node.args[0].value == "styleSheet"
        ):
            writes.append((node.lineno, node.args[1] if len(node.args) == 2 else None))
        writes.extend(
            (keyword.value.lineno, keyword.value)
            for keyword in node.keywords
            if keyword.arg == "styleSheet"
        )

    return writes


def test_every_stylesheet_under_app_is_a_composer_call() -> None:
    """A stylesheet written out where a widget is given it is a visual decision made a second time.

    Each one must be a call to a function `app/stylesheets.py` defines, by a
    name the module imports it under and binds to nothing else. A colour a
    widget's role decides is still passed at the call site -
    `foreground_stylesheet(MUTED)` - so the method `tools/contrast_check.py`
    cites for a pair is where the pair is chosen; what may not be written
    there is the stylesheet itself.
    """

    writes_read: dict[str, int] = {}
    written_out: list[str] = []

    for module in sorted(APP.rglob("*.py")):
        relative = module.relative_to(APP).as_posix()
        tree = ast.parse(module.read_text(encoding="utf-8"), filename=str(module))
        composers = _composer_names(tree)
        for line, value in _stylesheet_writes(tree):
            writes_read[relative] = writes_read.get(relative, 0) + 1
            if not (
                isinstance(value, ast.Call)
                and isinstance(value.func, ast.Name)
                and value.func.id in composers
            ):
                written_out.append(f"{relative}:{line}")

    assert not written_out, (
        "compose the stylesheet in app/stylesheets.py and pass the composer's call, so "
        f"the decision is written once (PL-Y4YX): {written_out}"
    )
    assert STYLING_MODULES <= set(writes_read), writes_read
