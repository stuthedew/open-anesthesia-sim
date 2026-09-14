---
id: PL-11YF
title: MODEL.md says the readouts sit in one row without saying above what width
priority: P2
effort: S
status: done
classes: docs, defect
feature: model-spec-accuracy
touches: docs/MODEL.md
added: 2026-09-02
closed: 2026-09-14
pr: 555
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

**What v0.4.1 does to this (added 2026-09-03).** The responsive finding is independent and
stands - `METRIC_GRID_COLUMNS` in `app/simulation_view.py` reflows the readout
row at a width `docs/MODEL.md` does not state. But one of the two arguments this
item wants qualified is that "the splitting error cannot mislead a reader who
compares the readouts the way the row is designed to be compared", and its third
instance sits in § "Independent-solution test" - both rewritten by `PL-X9KD`.
Cheaper after it; if taken before, qualify the width claim and leave the
splitting-error sentence for `PL-X9KD` to replace.

**Half the target text is deleted rather than qualified, after `PL-GS5X`
(2026-09-06).** One of the two arguments this item wants width-qualified is
that "the splitting error cannot mislead a reader who compares the readouts the
way the row invites". That claim, and the sequencing-bias analysis behind it,
are **withdrawn** — `docs/MODEL.md` records the withdrawal in both places the
claim appeared. There is no bias with a sign, so a gap between two readouts is
now no less accurate than either reading it is taken from.

The other argument, about the ordinal reading the row invites, is untouched and
is still worth qualifying. Re-scope to it alone.

## Landed 2026-09-14, on the re-scoped half

`docs/MODEL.md` § "Displayed precision" now states the width above which the
readouts sit in one row, and what the reflow below it does to each argument
that rests on the arrangement.

**The thresholds, read from the code rather than from the brief.**
`METRIC_GRID_COLUMNS` maps Flet's breakpoints to column counts — XS 1, MD 2,
LG 4, XL 7 — and every panel spans exactly one column, both held by
`test_every_readout_reserves_a_qualifier_line_and_an_equal_column`. Flet's
breakpoint minima are xs 0, sm 576, md 768, lg 992, xl 1200 CSS pixels, and a
width takes the largest declared step at or below it. SM is not declared, so
576–767 falls to XS. The seven panels therefore seat side by side at 1200 and
wider, four per line from 992 to 1199, two from 768 to 991, one below 768 —
which is what the brief said, now stated in the specification with the
constant named.

**Both instances were qualified, and the two arguments are not affected
equally.** That asymmetry is the part the brief could not have known without
the analysis:

- **The ordinal reading weakens**, as the brief expected. Below 1200 the
  comparison the row invites becomes a scan across lines rather than a glance.
  But only the *invitation* narrows: the 1 485 000 pair comparisons behind the
  ordering claim compare displayed values, not their positions, so the
  measurement is untouched by layout.
- **The uniform resolution holds at every width**, and this is the finding.
  Its argument is that differing decimal counts put different magnitudes at the
  same glyph position, and the grid aligns value glyphs within a column at
  every breakpoint. It never rested on the six being in a single line, so the
  reflow does not weaken it. Qualifying it as though it did would have recorded
  a weaker claim than the code supports.

**One thing the brief did not ask for and the specification needed.** The
arrangement is unconditional in practice today because
`src/anesthesia_sim/app/main.py` opens the window full screen, so the
conditional widths are reachable only by resizing. That is a property of the
startup behaviour rather than of the specification, and `PL-005` — the sized,
centered startup window, which ships with the Qt port — turns those widths into
the ordinary case. Recorded, so a reader is not left to infer that a
width-conditional claim is unreachable.

**The third instance the brief names is already gone.** § "Independent-solution
test" carried "The six readouts are placed in one row to be read comparatively"
with the splitting-error argument behind it; `PL-GS5X` withdrew that claim in
both places on 2026-09-06. Checked rather than assumed — `grep` for "one row"
across `docs/MODEL.md` returns four hits, two of which are about data-table
rows.
