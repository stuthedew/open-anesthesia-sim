---
id: PL-NH53
title: docs/MODEL.md restates the supported run length in prose (§ Supported simulation step; § The first 24 hours of elimination against the published mean curves) and check_prose_provenance holds a prose figure to the data files only, so a change to MAXIMUM_ELAPSED_SIMULATION_TIME_S leaves those sentences wrong: hold a prose figure to a named constant in src/ with a marker, as the data-file figures are
priority: P3
effort: S
status: blocked
classes: docs
feature: one-home-for-constants
touches: tools/doc_check.py, tests/unit/test_doc_check.py, docs/MODEL.md
blocked-by: PL-R417
added: 2026-10-03
payoff: the specification's supported run length cannot drift from the simulator's, so docs/MODEL.md never tells a reader that a run length the simulator refuses is supported, or the reverse
verify: grep -q 'def test_a_prose_figure_is_held_to_the_constant_its_marker_names' tests/unit/test_doc_check.py
---

**Problem.** docs/MODEL.md restates the supported run length in prose (§ Supported simulation step; § The first 24 hours of elimination against the published mean curves) and check_prose_provenance holds a prose figure to the data files only, so a change to MAXIMUM_ELAPSED_SIMULATION_TIME_S leaves those sentences wrong: hold a prose figure to a named constant in src/ with a marker, as the data-file figures are

**Why it matters.** `check_prose_provenance` in `tools/doc_check.py` holds a `docs/MODEL.md` prose figure to the data file it came from through a `provenance:` or `derived:` marker, and 70 such markers stand in the document on 2026-10-03. The supported run length is not a data-file value: it is `MAXIMUM_ELAPSED_SIMULATION_TIME_S` in `core/supported_ranges.py`, and the document states it in prose under § "Supported simulation step" (as the 86 400 s a step floor is measured against, and the 86 400 000 steps a run holds at that floor) and under § "The first 24 hours of elimination against the published mean curves" (as the 24 hours "the supported run length" allows), with no marker on any of those sentences. PL-T5J5 found eight tests holding the same number as text and PL-40SJ counts the code copies; these are the prose copies, and a reader who trusts the specification's number for a run the simulator no longer supports is the failure the check's own docstring names.

**Reproduced 2026-10-04** on `main` at `48787726`: with `MAXIMUM_ELAPSED_SIMULATION_TIME_S` set to `172_800.0` (48 h) in `core/supported_ranges.py`, `python3 tools/doc_check.py check` exits 0, while both sections still state 86 400 s and 24 hours.

**Shape.** A third marker kind beside `provenance:` and `derived:` that names a module-level constant under `src/anesthesia_sim/` by its dotted path, read with `ast` as `tools/contrast_check.py` reads the colour constants, and held to the figure in the sentence above it as a `provenance:` marker is; the sentences above then carry one. Standard library only, inside the existing check. It does not decide whether the specification or the constant is the number's home: both state it, and the marker makes the two unable to drift from either side, which is what the data-file markers already do. A new check, so it is held by the generator pause in `CLAUDE.md` § "What this project is", which the owner declined to lift for it (decided below).

**Done when.** `check_prose_provenance` reads a marker naming a module-level constant under `src/anesthesia_sim/` by its dotted path, and holds the figure in the sentence above it to that constant's value; every sentence in the two sections that states the supported run length, or a figure computed from it, carries one; with `MAXIMUM_ELAPSED_SIMULATION_TIME_S` moved, `python3 tools/doc_check.py check` fails naming the sentence; and a test in `tests/unit/test_doc_check.py` named `test_a_prose_figure_is_held_to_the_constant_its_marker_names` pins it.

**Generator check.** An instance of PL-40SJ's fact - the value of a named constant, read from its one definition rather than typed again at the use - in prose rather than code, which PL-40SJ's tool deliberately leaves to this family. Not a new head. PL-40SJ's `root-cause-of:` carries this id, added at triage on 2026-10-04, since PL-40SJ closed without it.

[superseded 2026-10-03: PL-40SJ closed that day, in #1326, and the pause it held did not end with it; the hold below replaces this]
**Decided 2026-10-03: waits for PL-40SJ** (project owner, 2026-10-03, ratified, over lifting the apparatus pause for this item and PL-0Z0F while PL-40SJ carries `generator: live`). Built once the head has closed, against its tool's baseline; `blocked-by:` already records it.

**Held by the generator pause** (triage, 2026-10-04). PL-40SJ's tool and baseline are on `main`, so that half of the wait is over. The pause is not: on `main` at `4ab001b8`, `bin/docket generators` marks `PL-R417` (readers that take one physical line for a whole statement) still generating, and its build is open in #1332. The owner asked for this item's promotion on the two steps the offer named, a `verify:` command and no other live head; the first is done above and the second failed, so `blocked-by:` now names `PL-R417`, keeping the decision above to wait out the pause rather than lift it. `PL-R417`'s `touches` include `tools/doc_check.py` as well, so the wait also keeps this change to `check_prose_provenance` off a file another branch is editing. Before promoting, check that `bin/docket generators` marks no head "still generating", rather than this list; building it sooner is the owner's call, made by asking (`PL-6Q9L`).
