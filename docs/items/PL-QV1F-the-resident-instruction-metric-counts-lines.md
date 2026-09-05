---
id: PL-QV1F
title: The resident-instruction metric counts lines, but 21% of CLAUDE.md's text sits on 6% of its lines, so a 433-character cut inside one paragraph reported as unchanged
priority: P2
effort: S
status: done
classes: defect, infra
feature: worker-instructions
touches: tools/doc_check.py, tests/unit/test_doc_check.py, CLAUDE.md
added: 2026-09-05
closed: 2026-09-05
pr: 348
verify: uv run pytest tests/unit/test_doc_check.py && grep -q 'def test_a_cut_inside_an_unwrapped_paragraph_is_visible' tests/unit/test_doc_check.py
---

**Problem.** `measure_resident` in `tools/doc_check.py` reports
`len(text.splitlines())`, and `check_resident_instructions` compares that
against the merge base. `CLAUDE.md` is not uniformly wrapped: measured
2026-09-05, 24 of its 359 non-blank lines run over 120 characters and carry
6286 of its 29787 characters — **21% of the text on 6% of the lines**, at
roughly ten times the density of the hard-wrapped remainder.
`.claude/rules/instruction-writing.md`, the other resident file, has no such
line at all, so the two files are being measured on different scales.

Found by landing `PL-6SBB`: routing the apparatus standard out cut the
two-standards paragraph from 1334 characters to 901. It is one physical line
either way, so the gate printed "unchanged against origin/main" for a 32% cut
in the largest paragraph in the file.

**Why it matters.** This is the failure mode `CLAUDE.md` names as earning an
interruption — a check that gives a wrong answer silently. It passes while the
guarantee it stands for is partly void, and it is void in both directions: a
long paragraph can absorb several hundred characters of new instruction and
report zero growth, and the routing the same advisory demands earns no credit
when it works. The advisory's own text tells a session to route rather than
trim, then cannot see that it routed.

It also mismeasures what it is a proxy for. The advisory's reasoning
(`PL-H7XN`) is about how much a session loads before reading anything, which is
characters or tokens, not newlines.

**Where.** `measure_resident` and `ResidentInstructions` in
`tools/doc_check.py`, and the baseline it stores. Options, and the middle one
is probably right:

- **Count characters instead of lines.** Smallest change, measures the real
  thing, and makes every stored baseline number incomparable with the new one
  in exactly one commit. The advisory text quotes line counts, so it moves too.
- **Count both, threshold on characters, print lines.** Keeps the familiar
  number visible while the gate reads the honest one.
- **Hard-wrap `CLAUDE.md` and keep counting lines.** Makes the existing metric
  correct rather than replacing it, and a wrap width is itself enforceable. But
  it is a whole-file reformat that collides with `PL-3VKZ` (rewrite the
  over-verbose prose) and would put a large diff in front of it.

Whichever is chosen, the baseline comparison has to survive the change: a
metric switch that reports every file as grown on the first run is the same
defect arriving from the other side.

**Done when.** A material reduction inside an unwrapped paragraph is visible to
`make check`, and a material addition to one cannot report as unchanged.

**Resolution.** The second option, with a floor the three options did not name.
`measure_resident` now records characters and lines per file; every comparison
reads characters and the printed line carries both, because their ratio is what
made the defect invisible and a reader shown one number alone cannot tell that
the two disagree.

The baseline needed no migration: `_resident_baseline` re-measures the default
branch's *file contents* out of git with the same `_measure`, so nothing stored
was in the old unit and the first run compares like with like.

The floor is the part worth recording. Characters resolve a typo, so switching
unit without one would newly demand a routing justification for a
four-character term swap - the same defect as the blindness it fixes, arriving
from the other side, and the failure `CLAUDE.md` names when it says a check
earns its place every run. `MATERIAL_RESIDENT_DELTA` is 40 characters, measured
rather than picked: over the 79 commits that had moved this measurement by
2026-09-05, every wording fix moved at most 30 characters and every change that
added or removed a rule moved at least 79, with nothing at all in between. It
gates the advisories only - the total and the exact delta print either way, so
a smaller change stays visible and only the demand for a justification is
withheld.

The same scan restated the case in the metric's own terms: six commits had
moved the resident text without moving a line at all, the largest by 409
characters, and eight moved 200 characters or more while moving at most two
lines.
