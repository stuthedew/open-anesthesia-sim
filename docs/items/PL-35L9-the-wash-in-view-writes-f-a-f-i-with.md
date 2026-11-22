---
id: PL-35L9
title: The wash-in View writes F_A/F_I with underscores, a programmer's notation, where the anesthesia literature writes FA/FI with subscripts
priority: P3
effort: S
status: done
classes: ux
feature: interface-design-review
milestone: v0.6.20
touches: src/anesthesia_sim/app/chart_frame.py, src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/qt_chart.py, tests
added: 2026-11-22
closed: 2026-11-22
pr: 2213
payoff: the wash-in View names FA/FI as the anesthesia literature typesets it, with subscripts
tests: tests/integration/simulation_view/test_simulation_view_whole_interface.py::test_the_wash_in_view_writes_its_fractions_with_subscripts
---

**Problem.** The wash-in View writes F_A/F_I with underscores, a programmer's notation, where the anesthesia literature writes FA/FI with subscripts

**Go-ahead.** The design review that found this was approved by the project owner (project owner, 2026-11-22). It ran offscreen on `a7eb53f`, with screenshots of each Workspace and each View at 1366 by 768 and 1920 by 1080 in `/mnt/project-files/v0.7.0/design-review/`.

**What a learner sees.** "Wash-in: F_A/F_I, alveolar as a fraction of the
modelled circuit", a legend row "F_A/F_I (solid)", "Now: F_A/F_I = 0.77", an
axis title "F_A/F_I" and "F_I = modelled circuit, not the vaporizer dial"
(`view-wash_in-1920x1080.png`).

**Why it matters.** The underscore is how a programmer writes a subscript. The
learner knows the ratio as FA/FI with the A and I set as subscripts, which
is how `docs/INTERFACE.md` § "F_A/F_I as a displayed ratio" typesets it.

**What to do.** Write the subscripts as subscripts: rich text with `<sub>` in
the labels, and the plot's axis title as HTML, which pyqtgraph accepts. Keep a
plain "FA/FI" for the accessible name. Every string changes in the approved
wording list.

**Done when.** No visible string in the wash-in View contains "F_A" or "F_I",
and the approved wording list shows the new forms.

**Built (2026-11-22).** `app/chart_frame.py` holds the three names once, as
`ALVEOLAR_FRACTION_NAME`, `INSPIRED_FRACTION_NAME` and `WASH_IN_RATIO_NAME`,
written with `<sub>` markup. The heading, the caption, both legend rows, the
"Now:" line and the plot's axis title are composed from them. Qt labels and
pyqtgraph's axis title render the markup, which the screenshots in
`/mnt/project-files/v0.7.0/design-review/before-after/` show. The hover readout
is drawn as plain text, so it uses `WASH_IN_RATIO_PLAIN_NAME`, "FA/FI",
derived from the marked-up name by removing the tags. "FA/FI" is how the
abstract of Yasuda et al. 1991 writes the ratio in plain text
(doi:10.1097/00000542-199103000-00017, read in its PubMed record on
2026-11-22). Qt's accessibility layer reads a marked-up label as its plain
text, so a screen reader hears "Now: FA/FI = 0.77" (measured offscreen).

**Regression run on the code before the fix.**
`test_the_wash_in_view_writes_its_fractions_with_subscripts`, run on `f5c8227`
with this branch's test file, fails with
`AssertionError: assert ['F_A/F_I', '...A/F_I = 0.41'] == []`.

**Docs sweep.** `docs/INTERFACE.md` § "F_A/F_I as a displayed ratio" already
typesets the ratio with subscripts and quotes none of the changed strings.
`docs/MODEL.md` and `README.md` quote none of them. Checked by searching each
for "F_A/F_I (solid)", "Now: F_A", "Equilibrium, F_A" and "Wash-in: F_A".

The independent review found one string the search missed. `docs/INTERFACE.md`
§ "Which series answer a hover, and which do not" quoted the hover readout as
"Wash-in F_A/F_I (alveolar / modelled circuit)". It now quotes "Wash-in FA/FI",
and `test_the_wash_in_view_writes_its_fractions_with_subscripts` holds the
hover label to that example. A search of the three documents for "Wash-in F"
finds no other quotation.

**Generator check.** A one-off: every changed string was written in one
change, before the names had one home.
