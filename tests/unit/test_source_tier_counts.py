"""What `tools/source_tier_counts.py` prints, and when it prints no count at all.

A count is only worth reading if a wrong one cannot be printed, so each way
the `authority_for` link can break is held to a refusal here, beside the exact
text of a clean run.
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable
from pathlib import Path
from typing import Any

import doc_check
import pytest
import source_tier_counts

Files = dict[str, dict[str, Any]]

HEADER = (
    "Stored values by the tier of the source adopted for each, read from each sources "
    "entry's authority_for under src/anesthesia_sim/data/.\n"
)
TOTALS_RE = re.compile(
    r"All files: (\d+) stored values? - (\d+) tier 1 \(primary\), (\d+) tier 2 \(secondary\), "
    r"(\d+) tier 3 \(reference implementation\), (\d+) with no adopted source\."
)


def _files() -> Files:
    """An agent-like, a machine-like and a patient-like file, built fresh for each test."""
    return {
        "agents/demo.json": {
            "schema_version": 3,
            "id": "demo",
            "display_name": "Demo agent",
            "blood_gas_partition_coefficient": 0.5,
            "tissue_gas_partition_coefficients": {"vessel_rich": 1.0, "fat": 20.0},
            "max_delivered_concentration_percent": 8.0,
            "mac_percent": 2.0,
            "sources": [
                {
                    "citation": "Primary P, Second S, Third T. Partition coefficients measured "
                    "in human tissue at 37 C.",
                    "tier": "primary",
                    "adopted": True,
                    "authority_for": [
                        "tissue_gas_partition_coefficients.vessel_rich",
                        "tissue_gas_partition_coefficients.fat",
                    ],
                },
                {
                    "citation": "Table T. A simulator's parameter set.",
                    "tier": "reference-implementation",
                    "adopted": True,
                    # Out of file order, which the output is not.
                    "authority_for": ["mac_percent", "blood_gas_partition_coefficient"],
                },
                {
                    "citation": "Vaporizer V. A calibration.",
                    "tier": "primary",
                    "adopted": True,
                    "authority_for": ["max_delivered_concentration_percent"],
                },
                {
                    "citation": "Review R. A synthesis.",
                    "tier": "secondary",
                    "adopted": False,
                    "authority_for": [],
                },
                {
                    # Cited beside a tier it shares with adopted entries, and
                    # never listed under that tier: a reader takes a citation
                    # printed there as provenance.
                    "citation": "Measured M. A primary measurement cited and not adopted.",
                    "tier": "primary",
                    "adopted": False,
                    "authority_for": [],
                },
            ],
        },
        "machines/demo.json": {
            "schema_version": 3,
            "id": "demo_circuit",
            "circuit_volume_l": 6.0,
            "deliverable_fresh_gas_flow_range": None,
            "provenance_gap": "No source is adopted for this file's value.",
            "sources": [
                {
                    "citation": "Workbook W. A teaching simulator.",
                    "tier": "reference-implementation",
                    "adopted": False,
                    "authority_for": [],
                }
            ],
        },
        "patients/demo.json": {
            "schema_version": 3,
            "id": "demo_patient",
            "weight_kg": 70.0,
            "venous_pool_volume_l": 1.2,
            "tissue_groups": {"fat": {"volume_l": 14.5, "perfusion_fraction": 0.05}},
            "provenance_gap": "No primary source is adopted for this file's values.",
            "sources": [
                {
                    "citation": "Workbook W. A default patient.",
                    "tier": "reference-implementation",
                    "adopted": True,
                    "authority_for": [
                        "tissue_groups.fat.volume_l",
                        "tissue_groups.fat.perfusion_fraction",
                    ],
                },
                {
                    "citation": "Synthesis S. A physiological model.",
                    "tier": "secondary",
                    "adopted": True,
                    "authority_for": ["venous_pool_volume_l"],
                },
            ],
        },
    }


def _tree(tmp_path: Path, files: Files) -> Path:
    data = tmp_path / "src" / "anesthesia_sim" / "data"
    for relative, document in files.items():
        (data / relative).parent.mkdir(parents=True, exist_ok=True)
        (data / relative).write_text(json.dumps(document, indent=4), encoding="utf-8")
    return tmp_path


def _run(root: Path, capsys: pytest.CaptureFixture[str]) -> tuple[int, str, str]:
    code = source_tier_counts.main(["--root", str(root)])
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def test_values_are_grouped_by_the_tier_of_their_adopted_source(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code, out, err = _run(_tree(tmp_path, _files()), capsys)
    assert (code, err) == (0, "")
    assert out == HEADER + (
        "\n"
        "data/agents/demo.json: 5 stored values\n"
        "  tier 1 (primary): 3\n"
        "    Primary P, Second S, Third T. Partition coefficients meas...: "
        "tissue_gas_partition_coefficients.vessel_rich, tissue_gas_partition_coefficients.fat\n"
        "    Vaporizer V. A calibration.: max_delivered_concentration_percent\n"
        "  tier 3 (reference implementation): 2\n"
        "    Table T. A simulator's parameter set.: blood_gas_partition_coefficient, "
        "mac_percent\n"
        "data/machines/demo.json: 1 stored value\n"
        "  no adopted source: 1\n"
        "    circuit_volume_l\n"
        "data/patients/demo.json: 4 stored values\n"
        "  tier 2 (secondary): 1\n"
        "    Synthesis S. A physiological model.: venous_pool_volume_l\n"
        "  tier 3 (reference implementation): 2\n"
        "    Workbook W. A default patient.: tissue_groups.fat.volume_l, "
        "tissue_groups.fat.perfusion_fraction\n"
        "  no adopted source: 1\n"
        "    weight_kg\n"
        "\n"
        "All files: 10 stored values - 3 tier 1 (primary), 1 tier 2 (secondary), "
        "4 tier 3 (reference implementation), 2 with no adopted source.\n"
        "sources entries: 8 - 5 adopted (2 tier 1, 1 tier 2, 2 tier 3), "
        "3 cited and not adopted.\n"
    )


def test_a_file_that_adopts_nothing_still_totals_every_tier(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    files = {"machines/demo.json": _files()["machines/demo.json"]}
    code, out, _err = _run(_tree(tmp_path, files), capsys)
    assert code == 0
    assert out == HEADER + (
        "\n"
        "data/machines/demo.json: 1 stored value\n"
        "  no adopted source: 1\n"
        "    circuit_volume_l\n"
        "\n"
        "All files: 1 stored value - 0 tier 1 (primary), 0 tier 2 (secondary), "
        "0 tier 3 (reference implementation), 1 with no adopted source.\n"
        "sources entries: 1 - 0 adopted (0 tier 1, 0 tier 2, 0 tier 3), "
        "1 cited and not adopted.\n"
    )


def _without_authority_for(files: Files) -> str:
    del files["agents/demo.json"]["sources"][0]["authority_for"]
    return "data/agents/demo.json sources[0]"


def _naming_what_is_not_a_stored_value(files: Files) -> str:
    files["agents/demo.json"]["sources"][1]["authority_for"].append("display_name")
    return "data/agents/demo.json sources[1]"


def _naming_a_value_another_entry_names(files: Files) -> str:
    files["patients/demo.json"]["sources"][1]["authority_for"].append("tissue_groups.fat.volume_l")
    return "data/patients/demo.json sources[1]"


def _disagreeing_with_adopted(files: Files) -> str:
    files["machines/demo.json"]["sources"][0]["authority_for"] = ["circuit_volume_l"]
    return "data/machines/demo.json sources[0]"


@pytest.mark.parametrize(
    "break_link",
    [
        _without_authority_for,
        _naming_what_is_not_a_stored_value,
        _naming_a_value_another_entry_names,
        _disagreeing_with_adopted,
    ],
)
def test_a_broken_link_prints_no_count(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], break_link: Callable[[Files], str]
) -> None:
    files = _files()
    where = break_link(files)
    code, out, err = _run(_tree(tmp_path, files), capsys)
    assert (code, out) == (1, "")
    assert where in err
    assert "python3 tools/doc_check.py check" in err


def test_a_file_that_is_not_json_prints_no_count(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _tree(tmp_path, _files())
    (root / "src" / "anesthesia_sim" / "data" / "agents" / "demo.json").write_text(
        "{", encoding="utf-8"
    )
    code, out, err = _run(root, capsys)
    assert (code, out) == (1, "")
    assert "data/agents/demo.json: cannot be read as JSON" in err


def test_a_tree_with_no_data_directory_exits_2(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code, out, err = _run(tmp_path, capsys)
    assert (code, out) == (2, "")
    assert "no data directory" in err


def test_the_real_tree_counts_each_stored_value_once(capsys: pytest.CaptureFixture[str]) -> None:
    """The tier split sums to the stored values; today's numbers are deliberately not pinned."""
    root = Path(doc_check.__file__).resolve().parent.parent
    code, out, err = _run(root, capsys)
    assert code == 0, err

    stored = sum(
        len(list(doc_check._leaf_numbers(json.loads(path.read_text(encoding="utf-8")))))
        for path in (root / "src" / "anesthesia_sim" / "data").rglob("*.json")
    )
    totals = next(line for line in out.splitlines() if line.startswith("All files: "))
    match = TOTALS_RE.fullmatch(totals)
    assert match is not None, totals
    total, *by_tier = (int(count) for count in match.groups())
    assert total == stored
    assert sum(by_tier) == stored
