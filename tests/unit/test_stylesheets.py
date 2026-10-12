"""Tests for `app/stylesheets.py`: each stylesheet composed in one place, and no toolkit there.

`PL-Y4YX` moved the ten composers the view modules held into one module beside
`app/theme.py` and kept the toolkit out of both (project owner, 2026-10-03,
ratified). Two properties make that more than a file move, and each is held
here: the module imports with no toolkit loaded, which is why it could sit
beside the theme at all, and every `setStyleSheet` call under `app/` passes one
of its composers, which is what making each visual decision once means in the
tree. What the strings draw is held where a widget is built to show it, in
`tests/integration/`.
"""

import ast
import inspect
import subprocess
import sys
from pathlib import Path

from anesthesia_sim.app import stylesheets

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
STYLING_MODULES = frozenset({"qt_chart.py", "qt_widgets.py", "run_view.py", "simulation_view.py"})


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


def test_no_composer_imports_a_toolkit_when_it_runs() -> None:
    """An import inside a function would load the toolkit after the import above had passed."""

    tree = ast.parse(Path(stylesheets.__file__).read_text(encoding="utf-8"))
    imported = {
        name.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for name in node.names
    } | {
        node.module.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }

    assert TOOLKIT_PACKAGES.isdisjoint(imported), sorted(TOOLKIT_PACKAGES.intersection(imported))


def _style_sheet_calls(module: Path) -> list[ast.Call]:
    tree = ast.parse(module.read_text(encoding="utf-8"), filename=str(module))

    return [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "setStyleSheet"
    ]


def test_every_set_style_sheet_call_under_app_passes_a_composer() -> None:
    """A stylesheet written out at its call site is a visual decision made a second time.

    Each call's one argument must be a call to a function `app/stylesheets.py`
    defines, by the name it is imported under. A colour a widget's role
    decides is still passed at the call site - `foreground_stylesheet(MUTED)`
    - so the method `tools/contrast_check.py` cites for a pair is where the
    pair is chosen; what may not be written there is the stylesheet itself.
    """

    calls_read: dict[str, int] = {}
    written_out: list[str] = []

    for module in sorted(APP.rglob("*.py")):
        relative = module.relative_to(APP).as_posix()
        for call in _style_sheet_calls(module):
            calls_read[relative] = calls_read.get(relative, 0) + 1
            argument = call.args[0] if len(call.args) == 1 and not call.keywords else None
            if not (
                isinstance(argument, ast.Call)
                and isinstance(argument.func, ast.Name)
                and argument.func.id in COMPOSERS
            ):
                written_out.append(f"{relative}:{call.lineno}")

    assert not written_out, (
        "compose the stylesheet in app/stylesheets.py and pass the composer's call, so "
        f"the decision is written once (PL-Y4YX): {written_out}"
    )
    assert STYLING_MODULES <= set(calls_read), calls_read
