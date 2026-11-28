---
id: PL-GRC6
title: The vessel-rich compartment is named 'Vessel-rich' in the chart's legend, its hover and the mark editor, and 'Vessel-rich group' in its readout, because READOUT_PANELS in app/dashboard_frame.py holds a second copy of each compartment's name and gloss
priority: P2
effort: S
status: done
classes: defect
feature: one-source-of-truth
touches: src/anesthesia_sim/app/run_series.py, src/anesthesia_sim/app/chart_frame.py, src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/bookmarks.py, docs/INTERFACE.md, docs/ARCHITECTURE.md, README.md, assets/screenshots/dashboard.png, tests/integration/approved_interface_strings.json, tests/integration/simulation_view/test_simulation_view_bookmarks.py, tests/integration/simulation_view/test_simulation_view_charts.py, tests/integration/simulation_view/test_simulation_view_whole_interface.py, tests/integration/test_qt_chart.py, tests/unit/test_bookmarks.py, tests/unit/test_chart_frame.py, tests/unit/test_dashboard_frame.py
deferred-from: v0.7.0 - filed after the freeze, not safety or science, and no user sees a wrong value from it: the two names are one compartment's; the gate is otherwise clear and the release waits on the owner test drive, so it is deferred rather than holding the release (triage 2026-11-28)
added: 2026-11-27
closed: 2026-11-28
pr: 2351
payoff: a user sees each compartment under one name, the field's own, in its readout, the chart's key and hover, the schematic and the mark editor
tests: tests/unit/test_dashboard_frame.py::test_each_readout_names_its_compartment_as_the_chart_s_key_does
---

**Problem.** The vessel-rich compartment is named 'Vessel-rich' in the chart's legend, its hover and the mark editor, and 'Vessel-rich group' in its readout, because READOUT_PANELS in app/dashboard_frame.py holds a second copy of each compartment's name and gloss

**Why it matters.** A user who reads "Vessel-rich group" in the readout and
"Vessel-rich" in the chart's key can wonder whether they are two compartments.
One name everywhere, the one the field's own texts use, removes the question,
and one record of each name means no later label can drift from it.

**Where.** `run_series.COMPARTMENT_NAMES` is the one record of each compartment's on-screen name since `PL-5867`, and `chart_frame.COMPARTMENT_TRACES` reads its labels from it. `dashboard_frame.READOUT_PANELS` still writes each name out again, with each gloss ("inspired", "end-tidal-equivalent"), which `COMPARTMENT_TRACES` also holds. The two copies agree except for one compartment: the readout says "Vessel-rich group" and the legend, the hover, the mark editor and a refused mark's notice say "Vessel-rich".

**Source.** NUREG-0700 Rev. 3 (O'Hara, Brookhaven National Laboratory for the U.S. Nuclear Regulatory Commission, July 2020; full text from https://www.osti.gov/servlets/purl/1644018, read 2026-11-27), guideline 1.3.3-4, p. 1-39: "Labels should be worded consistently, so that the same item is given the same label whenever it appears."

**What to decide.** Which of the two names the compartment carries everywhere. The choice is wording, so it is decided from a source, and the item records which.

**Done when.** `READOUT_PANELS` reads each name and gloss from the one record, every place names the vessel-rich compartment the same way, and the approved interface strings record any changed label.

**Found by** `PL-5867` on 2026-11-27, while finding the one place that names a compartment.

**Decided 2026-11-28** (project owner, 2026-11-28). The thread first
recommended "Vessel-rich", to match the bare "Muscle" and "Fat", and asked
whether the readout should say it. The owner answered "Agree with best
practice and industry nomenclature". The field's own texts name the
compartment the vessel-rich group. The Gas Man Workbook, p. 21
(https://gasmanweb.com/Workbook.pdf, read 2026-11-28), says "the
vessel-rich group (VRG) containing the brain, heart, and other well-perfused
organs; muscle (MUS), and finally fat (FAT)". OpenAnesthesia's page on uptake
and distribution
(https://www.openanesthesia.org/keywords/inhaled-anesthetic-agents-mechanism-of-action-uptake-and-distribution/,
read 2026-11-28) lists "Vessel-rich group", "Muscle" and "Fat". So every place
says "Vessel-rich group", and "Muscle" and "Fat" stay as they are.

**Fix.** `run_series.COMPARTMENT_GLOSSES` now holds each compartment's gloss
beside `COMPARTMENT_NAMES`. A `TraceStyle` and a `ReadoutPanel` hold only
their compartment, and read the name and the gloss from the two records, so
neither can be built with another name. The legend, the hover, the readout,
the schematic's names, the mark editor and a refused mark's notice now all say
"Vessel-rich group". The legend's check box reads "Draw the Vessel-rich group
compartment on the chart" to a screen reader. The MAC-awake band's legend entry
said "read against vessel-rich trace" from a copy of its own, and now reads the
name from `COMPARTMENT_NAMES`, in lower case inside its phrase: "read against
vessel-rich group trace". The 1 MAC line's entry reads "alveolar" the same way,
and its words do not change. The README's screenshot is retaken, because its
legend showed the old name.

**Generator check.** A second copy of a compartment's on-screen name, the
mechanism `PL-5867` removed from the mark refusals. This fix ends it for
compartment names and glosses rather than adding an instance: a trace and a
readout panel now hold only their compartment, so neither can be built with a
copy. A first search of `src/` for each name as a whole quoted string missed
the band's legend, which held "vessel-rich" inside a longer string. A search
for each name in lower case inside any string, run after that, finds the two
records, docstrings and comments only.

**Tests.** `test_each_readout_names_its_compartment_as_the_chart_s_key_does` in
`tests/unit/test_dashboard_frame.py` checks that each compartment's readout and
trace carry one name and one gloss, that the vessel-rich compartment's name
is "Vessel-rich group", and that the 1 MAC line's and the MAC-awake band's
legend entries name their compartments the same way. Run against `origin/main` before the fix (b6aab762),
with `QT_QPA_PLATFORM=offscreen PYTHONPATH=<main's src> python -m pytest -q
"tests/unit/test_dashboard_frame.py::test_each_readout_names_its_compartment_as_the_chart_s_key_does"`,
it failed with `assert ('Vessel-rich group', None) == ('Vessel-rich', None)`.
The tests that print a compartment's name, in the chart's key and
hover, the mark editor and the mark refusals, now expect "Vessel-rich group",
and the approved wording list records the changed legend line and check-box
name. They pass under the container's font and under DejaVu Sans.

**Documents checked.** `docs/INTERFACE.md`: the line-style table and the
contrast table name the compartment "Vessel-rich group" now. Its prose that
says "the vessel-rich trace" describes the line rather than quoting its label,
and its parameter rows ("Vessel-rich tissue:gas") name a stored coefficient,
so both stay. `docs/ARCHITECTURE.md` § "Where new code belongs" said a
compartment's trace entry holds its legend words and gloss, and now says they
are read from `run_series.COMPARTMENT_NAMES` and `run_series.COMPARTMENT_GLOSSES`.
`docs/MODEL.md`, `docs/PARAMETERS.md` and `docs/VERIFICATION.md` name the
compartment only in the names of stored parameters, which are not on-screen
labels, so none changes. `README.md` already says "vessel-rich group", in
the screenshot's description and in its diagram of the model.
