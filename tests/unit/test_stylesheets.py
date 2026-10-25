"""Tests for `app/stylesheets.py`: each stylesheet is composed in one place that loads no toolkit.

`PL-Y4YX` moved the ten composers that the view modules held into one module
beside `app/theme.py`, and kept the toolkit out of both (project owner,
2026-10-03, ratified). Two properties make that more than a file move, and
this file tests each of them. First, the module imports with no toolkit
loaded, which is why it could sit beside the theme at all. Second, every
stylesheet given to a widget under `app/` is a call to one of its composers.
That is what making each visual decision once means in the code. What the
strings draw is tested where a widget is built to show it, in
`tests/integration/`.
"""

import ast
import inspect
import subprocess
import sys
from pathlib import Path

from anesthesia_sim.app import stylesheets, theme

#: The interface's package directory, which every module styling a widget is in.
APP = Path(stylesheets.__file__).parent

#: The top-level packages that make up the interface's toolkit.
TOOLKIT_PACKAGES = frozenset({"PySide6", "shiboken6", "pyqtgraph"})

#: Every function the module defines, which is every composer it offers.
COMPOSERS = frozenset(
    name
    for name, member in inspect.getmembers(stylesheets, inspect.isfunction)
    if member.__module__ == stylesheets.__name__
)

#: The modules that style a widget today. They are listed so that the walk
#: below cannot pass by finding nothing, as it would after a package moved or a
#: method was renamed.
STYLING_MODULES = frozenset(
    {"qt_chart.py", "qt_widgets.py", "run_surfaces.py", "run_view.py", "simulation_view.py"}
)


def test_the_composers_import_with_no_toolkit_loaded() -> None:
    """A fresh interpreter imports the module and the theme it uses, and loads no toolkit.

    The import runs in a separate process, because the integration tests
    have already loaded PySide6 into this one. The test therefore measures
    only what the import itself loads, including anything that `app/theme.py`
    imports on the module's behalf.
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
    """An import inside a composer would load the toolkit after the test above had passed.

    Such an import could name the toolkit, or a view module that imports the
    toolkit. The test therefore limits everything the module imports, rather
    than checking only for the toolkit's names.
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
    """Return the names under which a module imports composers, minus any it also rebinds."""

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
    """Return each stylesheet that a module gives a widget, with its line number.

    The stylesheet is None where the call does not have the expected shape.
    Qt accepts a stylesheet in three ways: `setStyleSheet`, the `styleSheet=`
    keyword its constructors accept, and `setProperty("styleSheet", ...)`.
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
    """A stylesheet written out at the widget that uses it repeats a visual decision.

    Each stylesheet must be a call to a function that `app/stylesheets.py`
    defines. The call must use the name under which the module imports that
    function, and the module must bind that name to nothing else. A colour
    that a widget's role decides is still passed at the call site, as in
    `foreground_stylesheet(MUTED)`. The method that `tools/contrast_check.py`
    cites for a colour pair is therefore where the pair is chosen. What may
    not be written there is the stylesheet itself.
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
