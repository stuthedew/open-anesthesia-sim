---
id: PL-11YF
title: MODEL.md says the readouts sit in one row without saying above what width
priority: P2
effort: S
status: ready
classes: docs, defect
feature: model-spec-accuracy
touches: docs/MODEL.md
added: 2026-09-02
verify: python3 tools/doc_check.py check && grep -q 'METRIC_GRID_COLUMNS' docs/MODEL.md
---

**Problem.** `docs/MODEL.md` § "Displayed precision" states twice, without
qualification, that the six concentration readouts are "placed in one row" and
"sit in one row and are read comparatively". The interface is responsive: the
row seats all seven panels side by side at 1200 CSS pixels and wider, four at
992, two at 768 and one below that. So the claim holds at the width the app
actually opens at — full screen — and not below it. It was already conditional
before PL-8M05 changed the thresholds; that change only made the conditions
explicit in the code without recording them in the specification.

**Why it matters.** Two arguments in that section rest on the one-row
arrangement: that a uniform display resolution is right because "different
decimal counts across those tiles would put different magnitudes at the same
glyph position", and that the splitting error cannot mislead a reader who
compares the readouts "the way the row is designed to be compared". Both are
weaker when the readouts are on two lines, and a reader of the specification
has no way to know the arrangement has a width condition at all. `CLAUDE.md`
makes `docs/MODEL.md` the authoritative specification for what the interface
displays, so an unconditional statement there is read as a commitment.

**Where.** `docs/MODEL.md` § "Displayed precision", the two sentences at the
paragraphs beginning "The comparison the interface actually invites" and "Why
the resolution is uniform rather than per-compartment";
`METRIC_GRID_COLUMNS` in `src/anesthesia_sim/app/simulation_view.py` holds the
thresholds. A third instance sits outside that section, in § "Independent-
solution test" ("The six readouts are placed in one row to be read
comparatively"), carrying the same argument about a difference between two
readings; it needs the same qualification.

**Done when.** The specification states the width above which the readouts sit
in one row, and says what the reflow below it means for the ordinal-reading and
uniform-resolution arguments that depend on it — or records that it deliberately
specifies only the full-screen case.
