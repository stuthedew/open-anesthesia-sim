"""`tools/literal_home_check.py` must refuse a second home for a number and say where the first is.

The direction that matters most is the false green: a literal the walk misses,
or a baseline that grows without failing, leaves the rule asserted and not
held. The suggestion is the opposite risk - it names a constant, so naming one
a site cannot import, or one the walk evaluated wrongly, points a reader at the
wrong quantity with the check's authority behind it.
"""

from __future__ import annotations

from pathlib import Path

from literal_home_check import analyze, format_report, main

REPO_ROOT = Path(__file__).resolve().parents[2]

PACKAGE = "src/anesthesia_sim"


def _tree(root: Path, **modules: str) -> None:
    """Write a synthetic package; `__` in a keyword is a directory separator."""
    for name, source in modules.items():
        path = root / PACKAGE / (name.replace("__", "/") + ".py")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(source, encoding="utf-8")


def _report(root: Path, baseline: dict[str, dict[tuple[str, str], int]] | None = None) -> str:
    return format_report(analyze(root, baseline=baseline or {}))


def test_a_new_literal_fails_naming_file_line_and_scope(tmp_path: Path) -> None:
    _tree(tmp_path, core__dose="class Pump:\n    def rate(self, x):\n        return x * 7\n")

    report = analyze(tmp_path, baseline={})

    assert report.errors == 1
    assert f"{PACKAGE}/core/dose.py:3: 7 in Pump.rate" in format_report(report)


def test_a_module_level_constant_and_a_table_inside_one_pass(tmp_path: Path) -> None:
    _tree(
        tmp_path,
        core__units=(
            "RATE = 7.5\nDOUBLED: float = RATE * 3\nTABLE = (dict(span_s=3600.0), [5, 6])\n"
        ),
    )

    assert analyze(tmp_path, baseline={}).errors == 0


def test_the_exempt_values_bool_and_a_format_precision_pass(tmp_path: Path) -> None:
    _tree(
        tmp_path,
        app__view=(
            "def place(x, items):\n"
            "    flags = (True, False)\n"
            "    middle = x / 2 + 2.0 * x - 2 + items[-1] + items[0] + 1.0\n"
            '    return f"{middle:.3f}", flags\n'
        ),
    )

    assert analyze(tmp_path, baseline={}).errors == 0


def test_a_class_default_is_a_bare_literal(tmp_path: Path) -> None:
    _tree(tmp_path, core__circuit="class BreathingCircuit:\n    volume_l: float = 6.0\n")

    assert "6.0 in BreathingCircuit" in _report(tmp_path)


def test_a_negative_literal_keeps_its_sign_in_the_finding_and_the_baseline(tmp_path: Path) -> None:
    _tree(tmp_path, core__bound="def floor():\n    return -2.5\n")
    path = f"{PACKAGE}/core/bound.py"

    assert "-2.5 in floor" in _report(tmp_path)
    assert analyze(tmp_path, baseline={path: {("floor", "-2.5"): 1}}).errors == 0


def test_the_baseline_covers_what_it_names_and_refuses_one_more(tmp_path: Path) -> None:
    path = f"{PACKAGE}/app/layout.py"
    baseline = {path: {("build", "8"): 1}}
    _tree(tmp_path, app__layout="def build(row):\n    row.gap(8)\n")
    assert analyze(tmp_path, baseline=baseline).errors == 0

    (tmp_path / path).write_text("def build(row):\n    row.gap(8)\n    row.pad(8)\n")
    printed = _report(tmp_path, baseline)

    assert f"{path}:2: 8 in build" in printed
    assert f"{path}:3: 8 in build" in printed
    assert "the baseline allows 1 of these in build, and 2 are there" in printed


def test_an_entry_the_tree_no_longer_fills_is_stale(tmp_path: Path) -> None:
    path = f"{PACKAGE}/app/layout.py"
    _tree(tmp_path, app__layout="def build(row):\n    row.gap(8)\n")
    baseline = {
        path: {("build", "8"): 2, ("build", "12"): 1},
        f"{PACKAGE}/app/gone.py": {("draw", "6"): 1},
    }

    report = analyze(tmp_path, baseline=baseline)
    printed = format_report(report)

    assert report.errors == 3
    assert f"{path}, 8 in build: baseline 2, found 1 - set it to 1" in printed
    assert f"{path}, 12 in build: baseline 1, found 0 - delete it" in printed
    assert "the file no longer exists; delete its entries" in printed


def test_the_finding_names_a_derived_constant_of_the_same_value(tmp_path: Path) -> None:
    _tree(
        tmp_path,
        core__units=(
            "SECONDS_PER_MINUTE = 60.0\n"
            "MINUTES_PER_HOUR = 60.0\n"
            "SECONDS_PER_HOUR = SECONDS_PER_MINUTE * MINUTES_PER_HOUR\n"
        ),
        core__ranges="def hours(limit_s):\n    return limit_s / 3600\n",
    )

    printed = _report(tmp_path)

    assert f"the same value as `SECONDS_PER_HOUR` in {PACKAGE}/core/units.py" in printed


def test_a_core_site_is_never_offered_a_constant_from_app(tmp_path: Path) -> None:
    _tree(
        tmp_path,
        app__geometry="GAP = 7\n",
        app__layout="def build(row):\n    row.gap(7)\n",
        core__dose="def rate(x):\n    return x * 7\n",
    )

    lines = _report(tmp_path).splitlines()
    app_finding = lines.index(f"  {PACKAGE}/app/layout.py:2: 7 in build")
    core_finding = lines.index(f"  {PACKAGE}/core/dose.py:2: 7 in rate")

    assert "`GAP`" in lines[app_finding + 1]
    assert "`GAP`" not in lines[core_finding + 1]


def test_a_constant_defined_in_two_modules_fails_and_an_import_does_not(tmp_path: Path) -> None:
    _tree(
        tmp_path,
        core__parameters="FLOW_FRACTION_TOLERANCE = 1e-12\n",
        core__perfusion="FLOW_FRACTION_TOLERANCE = 1e-12\n",
    )

    printed = _report(tmp_path)

    assert "FLOW_FRACTION_TOLERANCE: " in printed
    assert f"{PACKAGE}/core/parameters.py:1" in printed
    assert f"{PACKAGE}/core/perfusion.py:1" in printed

    (tmp_path / PACKAGE / "core" / "perfusion.py").write_text(
        "from anesthesia_sim.core.parameters import FLOW_FRACTION_TOLERANCE\n"
    )
    assert analyze(tmp_path, baseline={}).errors == 0


def test_a_leading_underscore_does_not_make_a_copy_a_new_name(tmp_path: Path) -> None:
    """`PL-QRBB`'s fix removed two `app/` copies spelled `_MILLISECONDS_PER_SECOND`."""
    _tree(
        tmp_path,
        core__units="MILLISECONDS_PER_SECOND = 1000\n",
        app__run_view="_MILLISECONDS_PER_SECOND = 1000\n",
    )

    printed = _report(tmp_path)

    assert "MILLISECONDS_PER_SECOND: " in printed
    assert f"{PACKAGE}/app/run_view.py:1 _MILLISECONDS_PER_SECOND = 1000" in printed
    assert f"{PACKAGE}/core/units.py:1 MILLISECONDS_PER_SECOND = 1000" in printed


def test_a_tree_with_no_python_files_is_an_error(tmp_path: Path) -> None:
    (tmp_path / PACKAGE).mkdir(parents=True)

    report = analyze(tmp_path, baseline={})

    assert report.errors == 1
    assert "the check read nothing" in format_report(report)


def test_a_file_that_does_not_parse_fails_and_its_entries_are_not_called_stale(
    tmp_path: Path,
) -> None:
    path = f"{PACKAGE}/app/broken.py"
    _tree(tmp_path, app__broken="def build(:\n")

    report = analyze(tmp_path, baseline={path: {("build", "8"): 1}})
    printed = format_report(report)

    assert report.errors == 1
    assert "Not checked - these files do not parse" in printed
    assert "delete it" not in printed


def test_the_real_tree_passes() -> None:
    assert main(["--root", str(REPO_ROOT)]) == 0
