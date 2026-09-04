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


def _boundary(*allowed: str) -> Boundary:
    return Boundary(package="pydantic", tree="src/pkg", allowed=allowed, why="a test fixture")


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

    def test_the_pydantic_boundary_is_the_one_declared(self) -> None:
        """The rule this file is about, stated where a reader will look for it."""
        (boundary,) = BOUNDARIES
        assert boundary.package == "pydantic"
        assert boundary.allowed == ("src/anesthesia_sim/core/parameters.py",)

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
        assert first.startswith("import boundaries: 1 declared,")
        assert first.endswith("0 errors")

    def test_a_violation_names_the_file_the_line_and_the_reason(self, tmp_path: Path) -> None:
        _tree(tmp_path, allowed="import pydantic\n", other="from pydantic import BaseModel\n")
        boundary = _boundary("src/pkg/allowed.py")
        rendered = format_report(analyze(tmp_path, [boundary]), [boundary])
        assert "src/pkg/other.py:1" in rendered
        assert "a test fixture" in rendered
        assert "src/pkg/allowed.py" in rendered

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
        package = tmp_path / "src" / "anesthesia_sim"
        package.mkdir(parents=True)
        (package / "core.py").write_text("from pydantic import BaseModel\n", encoding="utf-8")
        assert main(["--root", str(tmp_path)]) == 1
        assert "src/anesthesia_sim/core.py:1" in capsys.readouterr().out
