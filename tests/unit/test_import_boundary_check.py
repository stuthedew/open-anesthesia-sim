"""`tools/import_boundary_check.py` must accuse only what it can prove.

Two failure directions matter here and they are not symmetric. Missing a real
import leaves the boundary unguarded while `make check` reports it green, which
is the false-green the tool exists to remove. Accusing an import that is not
there is louder but cheaper: it fails a build somebody then reads.

The third direction is the one a boundary check is uniquely prone to and the
reason `analyze` reports an empty tree as an error: a check that inspects
nothing passes, and passing over nothing is indistinguishable from passing.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from import_boundary_check import BOUNDARIES, Boundary, analyze, format_report, main, module_imports

REPO_ROOT = Path(__file__).resolve().parents[2]


def _tree(root: Path, **modules: str) -> None:
    """Write a synthetic package, one keyword argument per module."""
    package = root / "src" / "pkg"
    package.mkdir(parents=True)
    for name, source in modules.items():
        (package / f"{name}.py").write_text(source, encoding="utf-8")


def _boundary(*allowed: str, package: str = "pydantic") -> Boundary:
    return Boundary(package=package, tree="src/pkg", allowed=allowed, why="a test fixture")


class TestModuleImports:
    """Every form that reaches a package, and every form that does not."""

    @pytest.mark.parametrize(
        ("source", "expected"),
        [
            ("import pydantic", "pydantic"),
            ("import pydantic.fields", "pydantic"),
            ("import pydantic as p", "pydantic"),
            ("from pydantic import BaseModel", "pydantic"),
            ("from pydantic.fields import Field", "pydantic"),
            ("from importlib import import_module\nx = import_module('pydantic')", "pydantic"),
            ("import importlib\nx = importlib.import_module('pydantic.fields')", "pydantic"),
            ("x = __import__('pydantic')", "pydantic"),
        ],
    )
    def test_reaches_the_package(self, source: str, expected: str) -> None:
        assert expected in {entry.root for entry in module_imports(source)}

    @pytest.mark.parametrize(
        "source",
        [
            "from . import pydantic",
            "from .pydantic import thing",
            "from ..core.pydantic import thing",
            "import importlib\nx = importlib.import_module('.pydantic', __package__)",
            "name = 'pyd' + 'antic'\nimport importlib\nx = importlib.import_module(name)",
            "import importlib\nx = importlib.import_module()",
            "pydantic = 1\nresult = pydantic + 1",
            "'a docstring mentioning pydantic'",
        ],
    )
    def test_does_not_reach_the_package(self, source: str) -> None:
        assert "pydantic" not in {entry.root for entry in module_imports(source)}

    def test_a_computed_dynamic_name_is_a_stated_limit(self) -> None:
        """Not a defect to fix later: a computed name is undecidable from source.

        Recorded as a test so that a future reader meeting the gap knows it was
        chosen rather than overlooked. The guard is against an accidental
        import, not against a module determined to evade it.
        """
        found = module_imports("import importlib\nx = importlib.import_module(chosen_name)")
        assert {entry.root for entry in found} == {"importlib"}

    def test_an_import_guarded_by_type_checking_still_counts(self) -> None:
        """No runtime dependency, but the module's API now mentions the type."""
        source = (
            "from typing import TYPE_CHECKING\n"
            "if TYPE_CHECKING:\n"
            "    from pydantic import BaseModel\n"
        )
        assert "pydantic" in {entry.root for entry in module_imports(source)}

    def test_an_import_inside_a_function_still_counts(self) -> None:
        source = "def load():\n    import pydantic\n    return pydantic\n"
        assert "pydantic" in {entry.root for entry in module_imports(source)}

    def test_the_reported_line_is_the_import_statement(self) -> None:
        source = "import json\n\n\nfrom pydantic import BaseModel\n"
        (found,) = [entry for entry in module_imports(source) if entry.root == "pydantic"]
        assert found.line == 4
        assert found.statement == "from pydantic import ..."

    def test_unparseable_source_raises_rather_than_reporting_clean(self) -> None:
        """A file the parser cannot read is not a file with no imports."""
        with pytest.raises(SyntaxError):
            module_imports("def broken(:\n")


class TestAnalyze:
    def test_the_repository_holds_its_declared_boundaries(self) -> None:
        report = analyze(REPO_ROOT)
        assert not report.errors, format_report(report)
        assert report.scanned > 0

    def test_the_declared_boundaries_are_the_ones_this_file_is_about(self) -> None:
        """The rules, stated where a reader will look for them.

        A boundary added or dropped without a reason written beside it fails
        here, which is the point: `BOUNDARIES` is a specification, and a
        specification that can be edited without anybody noticing is prose.
        """
        assert tuple(boundary.package for boundary in BOUNDARIES) == (
            "pydantic",
            "subprocess",
            "time",
            "datetime",
            "random",
            "secrets",
            "uuid",
        )
        by_package = {boundary.package: boundary for boundary in BOUNDARIES}
        assert by_package["pydantic"].allowed == ("src/anesthesia_sim/core/parameters.py",)
        assert by_package["subprocess"].allowed == ("src/anesthesia_sim/app_metadata.py",)
        assert all(boundary.why.strip() for boundary in BOUNDARIES)

    @pytest.mark.parametrize("package", ["time", "datetime", "random", "secrets", "uuid"])
    def test_the_clock_and_generator_boundaries_permit_no_module_under_core(
        self, package: str
    ) -> None:
        """`CLAUDE.md`'s never-wall-clock rule, and MODEL.md's guarantee, measured.

        The tree is `core/` and not the whole package deliberately: the
        interface schedules its ticks with the wall clock, which the guarantee
        permits. Widening this to `src/anesthesia_sim` would fail on a real
        import the design allows; narrowing the packages would leave a route in.
        """
        (boundary,) = [entry for entry in BOUNDARIES if entry.package == package]
        assert boundary.tree == "src/anesthesia_sim/core"
        assert boundary.allowed == ()

    def test_a_boundary_permitting_no_module_admits_nothing(self, tmp_path: Path) -> None:
        """An empty `allowed` is a confinement out of the tree, not a disabled rule."""
        _tree(tmp_path, compartment="import time\n", other="import json\n")
        report = analyze(tmp_path, [_boundary(package="time")])
        (violation,) = report.violations
        assert violation.path == "src/pkg/compartment.py"
        assert violation.imported.line == 1
        assert report.errors

    def test_a_boundary_permitting_no_module_has_no_allowance_to_go_stale(
        self, tmp_path: Path
    ) -> None:
        """The unused- and missing-allowance branches have nothing to iterate."""
        _tree(tmp_path, other="import json\n")
        report = analyze(tmp_path, [_boundary(package="time")])
        assert not report.errors
        assert report.unused == () and report.unenforced == ()

    def test_an_import_outside_the_allowed_module_is_a_violation(self, tmp_path: Path) -> None:
        _tree(
            tmp_path,
            allowed="from pydantic import BaseModel\n",
            other="import json\n\nfrom pydantic import BaseModel\n",
        )
        report = analyze(tmp_path, [_boundary("src/pkg/allowed.py")])
        (violation,) = report.violations
        assert violation.path == "src/pkg/other.py"
        assert violation.imported.line == 3
        assert report.errors

    def test_every_offending_import_in_one_module_is_reported(self, tmp_path: Path) -> None:
        """One line per site: a reader fixing this needs all of them, not the first."""
        _tree(
            tmp_path,
            allowed="import pydantic\n",
            other="import pydantic\nfrom pydantic import BaseModel\n",
        )
        report = analyze(tmp_path, [_boundary("src/pkg/allowed.py")])
        assert [entry.imported.line for entry in report.violations] == [1, 2]

    def test_the_allowed_module_may_make_the_import(self, tmp_path: Path) -> None:
        _tree(tmp_path, allowed="from pydantic import BaseModel\n", other="import json\n")
        report = analyze(tmp_path, [_boundary("src/pkg/allowed.py")])
        assert not report.errors

    def test_an_allowance_naming_a_missing_file_is_an_error(self, tmp_path: Path) -> None:
        """A rename would otherwise move the exception somewhere nothing checks."""
        _tree(tmp_path, other="import json\n")
        report = analyze(tmp_path, [_boundary("src/pkg/renamed_away.py")])
        assert [path for _, path in report.unenforced] == ["src/pkg/renamed_away.py"]
        assert report.errors

    def test_an_allowance_no_longer_used_is_an_error(self, tmp_path: Path) -> None:
        """The `KNOWN_SHORTFALLS`-that-starts-passing rule, for allowances."""
        _tree(tmp_path, allowed="import json\n", other="import json\n")
        report = analyze(tmp_path, [_boundary("src/pkg/allowed.py")])
        assert [path for _, path in report.unused] == ["src/pkg/allowed.py"]
        assert report.errors

    def test_a_tree_with_no_python_files_is_an_error(self, tmp_path: Path) -> None:
        """The failure this check is uniquely prone to: passing over nothing."""
        (tmp_path / "src").mkdir()
        report = analyze(tmp_path, [_boundary("src/pkg/allowed.py")])
        assert len(report.empty) == 1
        assert report.scanned == 0
        assert report.errors

    def test_nesting_trees_do_not_inflate_the_module_count(self, tmp_path: Path) -> None:
        """`scanned` is evidence of how much source is guarded, so it counts files.

        Two boundaries over nesting trees read the same module. A count of
        module-*reads* would grow when a boundary was added rather than when
        the source did, which is the one thing the number is for.
        """
        _tree(tmp_path, one="import json\n", two="import json\n")
        outer = _boundary(package="time")
        inner = Boundary(package="random", tree="src", allowed=(), why="a nesting fixture")
        assert analyze(tmp_path, [outer, inner]).scanned == 2

    def test_a_module_importing_something_else_is_not_a_violation(self, tmp_path: Path) -> None:
        _tree(
            tmp_path, allowed="import pydantic\n", other="import pydantic_settings\nimport json\n"
        )
        report = analyze(tmp_path, [_boundary("src/pkg/allowed.py")])
        assert not report.violations

    def test_nested_modules_are_walked(self, tmp_path: Path) -> None:
        _tree(tmp_path, allowed="import pydantic\n")
        nested = tmp_path / "src" / "pkg" / "deep"
        nested.mkdir()
        (nested / "buried.py").write_text("from pydantic import BaseModel\n", encoding="utf-8")
        report = analyze(tmp_path, [_boundary("src/pkg/allowed.py")])
        assert [entry.path for entry in report.violations] == ["src/pkg/deep/buried.py"]


class TestFormatReport:
    def test_a_clean_run_leads_with_its_verdict(self) -> None:
        report = analyze(REPO_ROOT)
        first = format_report(report).splitlines()[0]
        assert first.startswith(f"import boundaries: {len(BOUNDARIES)} declared,")
        assert first.endswith("0 errors")

    def test_a_violation_names_the_file_the_line_and_the_reason(self, tmp_path: Path) -> None:
        _tree(tmp_path, allowed="import pydantic\n", other="from pydantic import BaseModel\n")
        boundary = _boundary("src/pkg/allowed.py")
        rendered = format_report(analyze(tmp_path, [boundary]), [boundary])
        assert "src/pkg/other.py:1" in rendered
        assert "a test fixture" in rendered
        assert "src/pkg/allowed.py" in rendered

    def test_a_boundary_permitting_nothing_says_so_rather_than_naming_an_empty_list(
        self, tmp_path: Path
    ) -> None:
        """`", ".join(())` would render "allowed only in , because" - a defect."""
        _tree(tmp_path, compartment="import time\n")
        boundary = _boundary(package="time")
        rendered = format_report(analyze(tmp_path, [boundary]), [boundary])
        assert "permitted in no module under src/pkg/, because" in rendered
        assert "allowed only in ," not in rendered
        assert "a test fixture" in rendered

    def test_each_error_kind_says_what_to_do_about_it(self, tmp_path: Path) -> None:
        _tree(tmp_path, allowed="import json\n")
        boundary = _boundary("src/pkg/allowed.py", "src/pkg/gone.py")
        rendered = format_report(analyze(tmp_path, [boundary]), [boundary])
        assert "absent from the tree" in rendered
        assert "remove the entry" in rendered


class TestMain:
    def test_a_clean_tree_exits_zero(self, capsys: pytest.CaptureFixture[str]) -> None:
        assert main(["--root", str(REPO_ROOT)]) == 0
        assert "0 errors" in capsys.readouterr().out

    def test_a_violation_exits_one(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Against the real `BOUNDARIES`, which `main` does not let a caller replace."""
        core = tmp_path / "src" / "anesthesia_sim" / "core"
        core.mkdir(parents=True)
        (core / "parameters.py").write_text("from pydantic import BaseModel\n", encoding="utf-8")
        (core / "tissue.py").write_text("import time\n", encoding="utf-8")
        app = tmp_path / "src" / "anesthesia_sim" / "app"
        app.mkdir()
        (app / "main.py").write_text("from pydantic import BaseModel\n", encoding="utf-8")
        assert main(["--root", str(tmp_path)]) == 1
        out = capsys.readouterr().out
        assert "src/anesthesia_sim/core/tissue.py:1" in out
        assert "src/anesthesia_sim/app/main.py:1" in out

    def test_the_interface_may_read_the_clock_the_compartments_may_not(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """The asymmetry, pinned end-to-end so widening the tree cannot pass quietly.

        `docs/MODEL.md` "The reproducibility guarantee" permits the interface
        its wall clock - what it forbids is a tick's real duration reaching the
        run - so a boundary that failed here would be enforcing a rule the
        design does not hold.
        """
        core = tmp_path / "src" / "anesthesia_sim" / "core"
        core.mkdir(parents=True)
        (core / "parameters.py").write_text("from pydantic import BaseModel\n", encoding="utf-8")
        package = tmp_path / "src" / "anesthesia_sim"
        # The one module allowed to ask the environment which build is running.
        # Present because an allowance naming a module that is not there is
        # itself an error, which is what keeps a stale allowance from rotting.
        (package / "app_metadata.py").write_text("import subprocess\n", encoding="utf-8")
        app = package / "app"
        app.mkdir()
        (app / "playback.py").write_text(
            "import time\n"
            "from datetime import datetime\n"
            "import random\n"
            "import secrets\n"
            "import uuid\n",
            encoding="utf-8",
        )
        assert main(["--root", str(tmp_path)]) == 0
        assert "0 errors" in capsys.readouterr().out
