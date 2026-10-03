---
id: PL-NH53
title: docs/MODEL.md restates the supported run length in prose (§ Supported simulation step; § The first 24 hours of elimination against the published mean curves) and check_prose_provenance holds a prose figure to the data files only, so a change to MAXIMUM_ELAPSED_SIMULATION_TIME_S leaves those sentences wrong: hold a prose figure to a named constant in src/ with a marker, as the data-file figures are
status: untriaged
feature: one-home-for-constants
added: 2026-10-03
---

**Problem.** docs/MODEL.md restates the supported run length in prose (§ Supported simulation step; § The first 24 hours of elimination against the published mean curves) and check_prose_provenance holds a prose figure to the data files only, so a change to MAXIMUM_ELAPSED_SIMULATION_TIME_S leaves those sentences wrong: hold a prose figure to a named constant in src/ with a marker, as the data-file figures are

**Why it matters.** `check_prose_provenance` in `tools/doc_check.py` holds a `docs/MODEL.md` prose figure to the data file it came from through a `provenance:` or `derived:` marker, and 70 such markers stand in the document on 2026-10-03. The supported run length is not a data-file value: it is `MAXIMUM_ELAPSED_SIMULATION_TIME_S` in `core/supported_ranges.py`, and the document states it in prose under § "Supported simulation step" (as the 86 400 s a step floor is measured against, and the 86 400 000 steps a run holds at that floor) and under § "The first 24 hours of elimination against the published mean curves" (as the 24 hours "the supported run length" allows), with no marker on any of those sentences. PL-T5J5 found eight tests holding the same number as text and PL-40SJ counts the code copies; these are the prose copies, and a reader who trusts the specification's number for a run the simulator no longer supports is the failure the check's own docstring names.

**Shape.** A third marker kind beside `provenance:` and `derived:` that names a module-level constant under `src/anesthesia_sim/` by its dotted path, read with `ast` as `tools/contrast_check.py` reads the colour constants, and held to the figure in the sentence above it as a `provenance:` marker is; the sentences above then carry one. Standard library only, inside the existing check. It does not decide whether the specification or the constant is the number's home: both state it, and the marker makes the two unable to drift from either side, which is what the data-file markers already do. A new check, so under `CLAUDE.md` § "What this project is" it waits for the pause PL-40SJ holds, or the owner's lift.

**Generator check.** An instance of PL-40SJ's fact - the value of a named constant, read from its one definition rather than typed again at the use - in prose rather than code, which PL-40SJ's tool deliberately leaves to this family. Not a new head. PL-40SJ's `root-cause-of:` should carry this id; its file is in flight on another branch, so that line is left to the session holding it.
