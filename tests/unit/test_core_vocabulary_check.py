"""`tools/core_vocabulary_check.py` must fire on a real drift and on nothing else.

Each of its three rules gets a fixture that violates it, because a check nobody
has watched fail is a check that might only be reporting success. The near-miss
cases matter as much: `require_concentration_fraction` is a live name in
`core/validation.py` that contains a retired one, and a rule that matched
substrings would fail the repository today against a name nobody has agreed to
change - which is how a check gets suppressed instead of obeyed.

The fourth direction is the one a check of this shape is uniquely prone to, and
it is why `analyze` reports an empty tree and an unreadable table as errors: a
rule that inspects nothing passes, and passing over nothing is
indistinguishable from passing.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from core_vocabulary_check import (
    CORE_TREE,
    MODEL_DOC,
    PHASES,
    RETIRED_NAMES,
    analyze,
    format_report,
    main,
)

REPO_ROOT = Path(__file__).resolve().parents[2]

#: A class every symbol fixture can point at, so a test about one rule does not
#: fail on another's fixture.
_COMPARTMENT = '''
from dataclasses import dataclass


@dataclass
class AlveolarCompartment:
    """A stand-in carrying one field, one property and one late attribute."""

    gas_volume_l: float = 2.5

    def __post_init__(self) -> None:
        self.agent_amount_l = 0.0

    @property
    def partial_pressure_fraction(self) -> float:
        return self.agent_amount_l / self.gas_volume_l
'''


def _root(tmp_path: Path, *, rows: list[str] | None = None, **modules: str) -> Path:
    """Write a synthetic repository: a `core/` tree and a Symbols table.

    Args:
        tmp_path: The root to build under.
        rows: Symbols table body rows, written between the pipes already. The
            default is one row resolving against `_COMPARTMENT`.
        modules: One keyword argument per module under `core/`. The default is
            `_COMPARTMENT` alone.
    """
    core = tmp_path / CORE_TREE
    core.mkdir(parents=True)
    for name, source in (modules or {"alveolar": _COMPARTMENT}).items():
        (core / f"{name}.py").write_text(source, encoding="utf-8")

    body = (
        rows
        if rows is not None
        else ["| $`F_A`$ | Alveolar | — | `AlveolarCompartment.partial_pressure_fraction` |"]
    )
    table = "\n".join(
        [
            "## Symbols",
            "",
            "| Symbol | Meaning | Unit | Code |",
            "| --- | --- | --- | --- |",
            *body,
            "",
            "## Compartment capacities",
        ]
    )
    document = tmp_path / MODEL_DOC
    document.parent.mkdir(parents=True, exist_ok=True)
    document.write_text(table, encoding="utf-8")
    return tmp_path


class TestSymbolMap:
    """Rule 1: every Code cell names something `core/` actually has."""

    def test_symbol_code_cell_must_resolve(self, tmp_path: Path) -> None:
        """The rule this whole file exists for: a cell naming a gone accessor fails."""
        report = analyze(
            _root(
                tmp_path,
                rows=["| $`F_A`$ | Alveolar | — | `AlveolarCompartment.concentration_fraction` |"],
            )
        )
        assert [problem.reference for problem in report.unresolved] == [
            "AlveolarCompartment.concentration_fraction"
        ]
        assert "no attribute, property or field called concentration_fraction" in format_report(
            report
        )

    def test_a_field_a_property_and_a_post_init_attribute_all_resolve(self, tmp_path: Path) -> None:
        """A dataclass declares most state in the body; a setter may add to it."""
        report = analyze(
            _root(
                tmp_path,
                rows=[
                    "| $`V_A`$ | Volume | L | `AlveolarCompartment.gas_volume_l` |",
                    "| $`F_A`$ | Fraction | — | `AlveolarCompartment.partial_pressure_fraction` |",
                    "| $`M_A`$ | Amount | L | `AlveolarCompartment.agent_amount_l` |",
                ],
            )
        )
        assert report.unresolved == ()
        assert report.cells == 3

    def test_a_cell_naming_no_class_in_core_is_reported(self, tmp_path: Path) -> None:
        report = analyze(
            _root(
                tmp_path,
                rows=["| $`Q`$ | Output | L/min | `PatientCompartments.cardiac_output_l_min` |"],
            )
        )
        assert "no class named PatientCompartments" in format_report(report)

    def test_a_class_defined_twice_names_no_one_expression(self, tmp_path: Path) -> None:
        """The column claims to name *the one* expression, so ambiguity is a failure."""
        report = analyze(_root(tmp_path, alveolar=_COMPARTMENT, duplicate=_COMPARTMENT))
        assert len(report.unresolved) == 1
        assert "is defined more than once" in format_report(report)

    def test_an_em_dash_cell_must_say_what_the_code_reads_instead(self, tmp_path: Path) -> None:
        """An em dash alone leaves the reader hunting an attribute never meant to exist."""
        report = analyze(_root(tmp_path, rows=["| $`F_a`$ | Arterial | — | — |"]))
        assert "is an em dash with nothing after it" in format_report(report)

    def test_an_em_dash_cell_with_prose_resolves_the_code_it_names(self, tmp_path: Path) -> None:
        """The substitute it points at is checked too, or the sentence rots unread."""
        good = analyze(
            _root(
                tmp_path / "good",
                rows=[
                    "| $`F_a`$ | Arterial | — | — no attribute: the code reads "
                    "`AlveolarCompartment.partial_pressure_fraction` instead |"
                ],
            )
        )
        assert good.unresolved == ()

        bad = analyze(
            _root(
                tmp_path / "bad",
                rows=[
                    "| $`F_a`$ | Arterial | — | — no attribute: the code reads "
                    "`AlveolarCompartment.arterial_fraction` instead |"
                ],
            )
        )
        assert [problem.reference for problem in bad.unresolved] == [
            "AlveolarCompartment.arterial_fraction"
        ]

    def test_a_cell_naming_two_expressions_is_reported(self, tmp_path: Path) -> None:
        report = analyze(
            _root(
                tmp_path,
                rows=[
                    "| $`F_A`$ | Alveolar | — | `AlveolarCompartment.gas_volume_l` or "
                    "`AlveolarCompartment.agent_amount_l` |"
                ],
            )
        )
        assert "names 2 `ClassName.accessor` expressions" in format_report(report)


class TestRetiredNames:
    """Rule 2: the vocabulary `PL-9SH6` closed stays closed."""

    @pytest.mark.parametrize("retired", [entry.name for entry in RETIRED_NAMES])
    def test_every_declared_retired_name_is_caught(self, tmp_path: Path, retired: str) -> None:
        """Each entry is checked, so adding one that nothing matches is visible."""
        report = analyze(
            _root(
                tmp_path,
                alveolar=_COMPARTMENT,
                revived=f"def read(patient):\n    return patient.{retired}\n",
            )
        )
        assert [use.identifier.name for use in report.retired] == [retired]

    def test_the_message_names_the_replacement(self, tmp_path: Path) -> None:
        report = analyze(
            _root(
                tmp_path,
                alveolar=_COMPARTMENT,
                revived="def read(circuit):\n    return circuit.circuit_concentration_fraction\n",
            )
        )
        assert "in favour of inspired_partial_pressure_fraction" in format_report(report)

    def test_a_live_name_that_merely_contains_a_retired_one_passes(self, tmp_path: Path) -> None:
        """`require_concentration_fraction` is the [0, 1] guard, not a retired accessor.

        It is a real name in `core/validation.py`, so a substring rule would
        fail the repository today over a rename nobody has agreed to - which is
        `PL-6KNM`'s open question, not this check's to answer.
        """
        report = analyze(
            _root(
                tmp_path,
                alveolar=_COMPARTMENT,
                guard="def require_concentration_fraction(name, value):\n    return value\n",
            )
        )
        assert report.retired == ()

    def test_a_retired_name_written_in_a_docstring_passes(self, tmp_path: Path) -> None:
        """Explaining the rename must stay possible, so only identifiers count."""
        report = analyze(
            _root(
                tmp_path,
                alveolar=_COMPARTMENT,
                history='"""Renamed from concentration_fraction by PL-9SH6."""\n',
            )
        )
        assert report.retired == ()

    def test_one_name_is_one_finding_per_module(self, tmp_path: Path) -> None:
        """Twenty call sites are one defect; two modules are two places to fix."""
        repeated = (
            "def read(a, b):\n"
            "    x = a.arterial_fraction\n"
            "    y = b.arterial_fraction\n"
            "    return x + y\n"
        )
        one = analyze(_root(tmp_path / "one", alveolar=_COMPARTMENT, revived=repeated))
        assert len(one.retired) == 1
        assert one.retired[0].identifier.line == 2

        two = analyze(
            _root(tmp_path / "two", alveolar=_COMPARTMENT, revived=repeated, elsewhere=repeated)
        )
        assert sorted(use.identifier.path for use in two.retired) == [
            f"{CORE_TREE}/elsewhere.py",
            f"{CORE_TREE}/revived.py",
        ]


class TestPartitionCoefficients:
    """Rule 3: an identifier names both phases, in order, so it cannot be its own reciprocal."""

    @pytest.mark.parametrize(
        "name",
        [
            "blood_gas_partition_coefficient",
            "tissue_gas_partition_coefficient",
            "tissue_blood_partition_coefficient",
            "fat_tissue_gas_partition_coefficient",
            "vessel_rich_tissue_blood_partition_coefficient",
            "tissue_gas_partition_coefficients",
        ],
    )
    def test_well_formed(self, tmp_path: Path, name: str) -> None:
        report = analyze(
            _root(
                tmp_path,
                alveolar=_COMPARTMENT,
                agent=f"def read(agent):\n    return agent.{name}\n",
            )
        )
        assert report.malformed == ()

    @pytest.mark.parametrize(
        ("name", "fragment"),
        [
            ("gas_blood_partition_coefficient", "which is the reciprocal"),
            ("blood_tissue_partition_coefficient", "which is the reciprocal"),
            ("gas_tissue_partition_coefficient", "which is the reciprocal"),
            ("blood_blood_partition_coefficient", "which is the reciprocal"),
            ("partition_coefficient", "names 0 of the two phases"),
            ("tissue_partition_coefficient", "names 1 of the two phases"),
            ("oil_gas_partition_coefficient", "names oil, which is not a declared phase"),
            (
                "oil_rubber_partition_coefficient",
                "names oil and rubber, which are not declared phases",
            ),
            ("lambda_partition_coefficient", "names 1 of the two phases"),
        ],
    )
    def test_malformed(self, tmp_path: Path, name: str, fragment: str) -> None:
        report = analyze(
            _root(
                tmp_path,
                alveolar=_COMPARTMENT,
                agent=f"def read(agent):\n    return agent.{name}\n",
            )
        )
        assert [problem.identifier.name for problem in report.malformed] == [name]
        assert fragment in format_report(report)

    def test_the_reciprocal_message_names_the_form_that_would_be_right(
        self, tmp_path: Path
    ) -> None:
        """The reader must be able to act on it without opening this script."""
        report = analyze(
            _root(
                tmp_path,
                alveolar=_COMPARTMENT,
                agent="def read(agent):\n    return agent.gas_blood_partition_coefficient\n",
            )
        )
        assert "so this is blood_gas_partition_coefficient" in format_report(report)

    def test_a_new_phase_is_one_entry(self, tmp_path: Path) -> None:
        """The ordering generalizes, so declaring a phase is what admits its coefficients."""
        from core_vocabulary_check import _phase_pair

        assert _phase_pair("oil_gas_partition_coefficient") is not None
        assert PHASES.index("tissue") > PHASES.index("blood") > PHASES.index("gas")


class TestPassingOverNothing:
    """The failure a check of this shape is uniquely prone to."""

    def test_an_empty_core_tree_is_an_error(self, tmp_path: Path) -> None:
        root = _root(tmp_path)
        for module in (root / CORE_TREE).glob("*.py"):
            module.unlink()
        report = analyze(root)
        assert report.empty_tree
        assert report.errors
        assert "inspected nothing" in format_report(report)

    @pytest.mark.parametrize(
        ("find", "replace"),
        [
            ("## Symbols", "## Notation"),
            ("| Symbol | Meaning | Unit | Code |", "| Sym | M | U | Impl |"),
        ],
    )
    def test_a_renamed_section_or_column_is_an_error(
        self, tmp_path: Path, find: str, replace: str
    ) -> None:
        root = _root(tmp_path)
        document = root / MODEL_DOC
        document.write_text(document.read_text(encoding="utf-8").replace(find, replace), "utf-8")
        report = analyze(root)
        assert report.empty_table
        assert report.errors


class TestTheRepository:
    """All three rules against the tree they were written for."""

    def test_the_tree_passes(self) -> None:
        report = analyze(REPO_ROOT)
        assert report.errors == 0, format_report(report)

    def test_every_symbol_cell_is_read(self) -> None:
        """A table this stops parsing halfway through would pass on what it read."""
        report = analyze(REPO_ROOT)
        assert report.cells == 24
        assert report.modules > 1

    def test_main_exits_zero(self, capsys: pytest.CaptureFixture[str]) -> None:
        assert main(["--root", str(REPO_ROOT)]) == 0
        assert "0 errors" in capsys.readouterr().out
