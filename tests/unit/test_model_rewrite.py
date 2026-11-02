"""`tools/model_rewrite.py` must list the ids a section still cites, and every fact a rewrite drops.

Each section part of `PL-ZT47` moves decision history out of `docs/MODEL.md`
and rewrites the rest. `ids` is how a part knows the history is out, and its
`verify:` runs it. `lost` is how the part, and the owner reading it, see every
equation, code span, citation and number the rewrite no longer carries. A fact
this tool fails to list is a fact nobody accounts for.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from model_rewrite import cited_ids, facts, gone_facts, main, report_ids

DOCUMENT = """\
# Model

## Hazards

The run is named (`PL-B2B2`), and this row has no test yet (`PL-C3C3`).
A wrapped form also counts: no test
yet (`PL-D4D4`), and so does PL-F5F5 written bare.

### A subsection

It cites `PL-G6G6`.

## Equations

Fresh gas enters at $`\\dot V_{FGF}`$ of 6 L/min, measured 2026-10-03 in #1808.

```math
F_A = 1 - e^{-t/\\tau}
```

See `tests/unit/test_alveolar.py` and doi 10.1213/00000539-199103000-00007, pp. 161-162.
"""


def _lines() -> list[str]:
    return DOCUMENT.splitlines()


def test_ids_skips_the_declared_none_form_even_when_it_wraps() -> None:
    lines = _lines()
    found = cited_ids(lines, 2, 12)

    assert [(cited.line, cited.ids) for cited in found] == [
        (5, ("PL-B2B2",)),
        (7, ("PL-F5F5",)),
        (11, ("PL-G6G6",)),
    ]


def test_a_section_holds_its_subsections_and_stops_at_its_sibling() -> None:
    status, out = report_ids(_lines(), ["Hazards"])

    assert status == 1
    assert [line.split(": ")[1] for line in out] == ["PL-B2B2", "PL-F5F5", "PL-G6G6"]
    assert report_ids(_lines(), ["Equations"]) == (0, [])


def test_a_heading_the_document_does_not_hold_exits_2() -> None:
    status, out = report_ids(_lines(), ["Equations", "Nowhere"])

    assert status == 2
    assert out == ['docs/MODEL.md: no heading reads "Nowhere"']


def test_facts_reads_each_kind_once() -> None:
    """A number inside an equation is the equation's; a pull request number is not a fact."""
    found = {(kind, text) for kind, text, _ in facts(DOCUMENT)}

    assert ("equation", "\\dot V_{FGF}") in found
    assert ("equation", "F_A = 1 - e^{-t/\\tau}") in found
    assert ("code", "tests/unit/test_alveolar.py") in found
    assert ("item id", "PL-B2B2") in found
    assert ("item id", "PL-F5F5") in found
    assert ("date", "2026-10-03") in found
    assert ("citation", "10.1213/00000539-199103000-00007") in found
    assert ("citation", "pp. 161-162") in found
    numbers = {text for kind, text in found if kind == "number"}
    assert numbers == {"6 L/min"}


def test_a_number_keeps_its_sign_exponent_and_unit_and_a_list_ordinal_is_not_one() -> None:
    """Each change below alters a value, so each must read as a lost fact."""
    before = (
        "A residual of 9.262e-14 L and 1.67e5 steps.\n"
        "A shift of −2.29 SD in 1.32 L, at 6L.\n"
        "1. Fat spans 4 px.\n"
        "2. It reaches 3 MAC.\n"
    )
    after = (
        "A residual of 9.999e-14 L and 1.92e5 steps.\n"
        "A shift of 2.29 SD in 1.32 mL, at 6 mL.\n"
        "1. Fat spans 4 px.\n"
        "2. It reaches 3.\n"
        "3. A third point.\n"
    )

    gone = {item.text for item in gone_facts(before, after, "")}

    assert gone == {"9.262e-14 L", "1.67e5", "−2.29", "1.32 L", "6L", "3 MAC"}


def test_gone_facts_counts_what_the_rewrite_holds_fewer_times_and_marks_the_moved() -> None:
    after = DOCUMENT.replace("of 6 L/min, measured 2026-10-03 in #1808.", "of 6 L/min.").replace(
        "```math\nF_A = 1 - e^{-t/\\tau}\n```\n", ""
    )
    added = "Measured 2026-10-03 at 6 L/min."

    gone = {(item.kind, item.text): item for item in gone_facts(DOCUMENT, after, added)}

    assert set(gone) == {("equation", "F_A = 1 - e^{-t/\\tau}"), ("date", "2026-10-03")}
    assert gone[("date", "2026-10-03")].moved
    assert not gone[("equation", "F_A = 1 - e^{-t/\\tau}")].moved
    assert gone[("equation", "F_A = 1 - e^{-t/\\tau}")].line == 18


def _git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


def test_lost_reads_the_fork_and_a_new_item_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _git(tmp_path, "init", "-q", "-b", "main")
    for key, value in (("user.email", "t@example.com"), ("user.name", "T")):
        _git(tmp_path, "config", key, value)
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs/MODEL.md").write_text(DOCUMENT, encoding="utf-8")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-qm", "seed")
    _git(tmp_path, "checkout", "-qb", "work")
    rewritten = DOCUMENT.replace(", pp. 161-162", "").replace("of 6 L/min", "of")
    (tmp_path / "docs/MODEL.md").write_text(rewritten, encoding="utf-8")
    (tmp_path / "docs/items").mkdir()
    (tmp_path / "docs/items/PL-B2B2-x.md").write_text("Moved: 6 L/min.\n", encoding="utf-8")

    assert main(["--root", str(tmp_path), "lost", "--base", "main"]) == 0
    out = capsys.readouterr().out
    assert "2 equations, code spans, citations and numbers" in out
    assert "1 of them were added to an item file" in out
    assert "  gone  pp. 161-162  (fork line 21:" in out
    assert "  moved 6 L/min  (fork line 15:" in out
