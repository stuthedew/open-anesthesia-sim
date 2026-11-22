---
id: PL-10BC
title: Read each mention of docs/MODEL.md that names no section, and re-point the ones that mean a requirement PL-CTXZ moved to docs/INTERFACE.md (640 mentions of the path remain in src/ and tests/ on 2026-11-11, with and without a section)
priority: P2
effort: M
status: done
classes: defect, docs
feature: model-md-structure
milestone: v0.6.20
touches: src/anesthesia_sim/app, src/anesthesia_sim/core, src/anesthesia_sim/data/workspaces/__init__.py, src/anesthesia_sim/data/agents/isoflurane.json, src/anesthesia_sim/data/agents/sevoflurane.json, tests, tools/contrast_check.py, docs/ARCHITECTURE.md, docs/machine-abstraction.md
deferred-from: v0.7.0 - a new problem: these mentions became wrong when #2109 (6446f927, 2026-11-13, PL-CTXZ) moved the interface sections out of docs/MODEL.md after the freeze, and PL-CTXZ is closed, so there is no open entry to pair it with
added: 2026-11-11
closed: 2026-11-22
pr: 2235
payoff: A contributor who follows a docstring to the specification it names finds the interface requirement it means, instead of a document that no longer states it.
verify: ! grep -qF 'MODEL.md` requires some Views' src/anesthesia_sim/app/view_registry.py
---

**Problem.** Read each mention of docs/MODEL.md that names no section, and re-point the ones that mean a requirement PL-CTXZ moved to docs/INTERFACE.md (640 mentions of the path remain in src/ and tests/ on 2026-11-11, with and without a section)

**Found 2026-11-14**, in a review of the night's merges: these mentions name `docs/MODEL.md` for text that is now only in `docs/INTERFACE.md`. `git blame` dates each before #2109, so the move missed them. The document check does not see them, because it reads no `#` comment, no possessive form such as "`docs/MODEL.md`'s unconditional set", and no bare § whose document is named on the line before.

1. `docs/machine-abstraction.md:50`: § "Runtime controls" moved; § "Parameter provenance" did not.
2. `src/anesthesia_sim/app/formatting.py:461` (a comment): § "F_A/F_I as a displayed ratio".
3. `src/anesthesia_sim/app/preferences.py:151-153`: § "A cost at the reader's price".
4. `tests/unit/test_agent_cost.py:360-362` and `:456-458`: § "A cost at the reader's price".
5. `tests/integration/test_controller.py:3549-3552`: § "Halting on a marked crossing".
6. "`docs/MODEL.md`'s unconditional set" at `src/anesthesia_sim/app/unconditional_set.py:1`, `tests/unit/test_unconditional_set.py:1` and `docs/ARCHITECTURE.md:119`. `docs/MODEL.md` no longer mentions the set; it is in `docs/INTERFACE.md` § "Minimum displayed outputs".
7. The per-substance tier at `src/anesthesia_sim/app/run_view.py:521` and `src/anesthesia_sim/app/unconditional_set.py:214`, in the same section.
8. `tests/unit/test_chart_frame.py:1399`: "`docs/MODEL.md`'s measured table" is `docs/INTERFACE.md` § "What a chart library prints instead, measured".
9. `tests/reference/test_coupled_dynamics.py:1895`, an assertion message: "re-derive the measured figures in docs/MODEL.md". The figures are cited only in `docs/INTERFACE.md`.

The line numbers are from `e278a80`.

**Checked 2026-11-21**, by `PL-5FMC` (the check of `docs/INTERFACE.md` against the code), at `2452b9b4e`. These mentions of `docs/MODEL.md` mean a requirement that is now in `docs/INTERFACE.md`: the module docstring and two more places in `app/unconditional_set.py`; `required_reachable` and `required_kinds` in `app/view_registry.py`; `app/area_layout.py`; three places in `app/preferences.py` (§ "A cost at the reader's price"); `tests/unit/test_agent_cost.py`; `app/theme.py`; `tools/contrast_check.py`; `app/stylesheets.py`; the comment above `COMPARTMENT_TRACES` in `app/chart_frame.py`; and `DisplayState` in `core/run_definition.py`.

**Checked again 2026-11-22**, at `d4e8200c`. The fault is still there. `grep -n 'MODEL.md' src/anesthesia_sim/app/unconditional_set.py` still prints the module docstring's "`docs/MODEL.md`'s unconditional set", and `grep -c -i 'unconditional set' docs/MODEL.md` prints 0. The comment above the F_A/F_I axis limits in `app/formatting.py` still names `docs/MODEL.md` for the section on F_A/F_I as a displayed ratio, which is now a heading of `docs/INTERFACE.md` only. `src/` and `tests/` hold 610 mentions of `docs/MODEL.md` in 111 files, and 443 of those lines carry no section mark.

**Why it matters.** `docs/MODEL.md` and `docs/INTERFACE.md` are the two specifications a contributor reads before changing the code. A docstring that sends them to `docs/MODEL.md` for an interface requirement sends them to a document that no longer states it. They may then conclude that the requirement is gone, and remove a value that every Workspace must keep on screen, or change how a cost is priced, without seeing the rule that forbids it. The document check cannot catch these mentions, because it does not read `#` comments, possessive forms, or a § whose document is named on the line before.

**Done when.** Every mention of `docs/MODEL.md` in `src/`, `tests/`, `tools/contrast_check.py`, `docs/ARCHITECTURE.md` and `docs/machine-abstraction.md` that means a requirement now stated in `docs/INTERFACE.md` names `docs/INTERFACE.md` instead, with the section that states it. Each mention that still means `docs/MODEL.md` is left as it is.

**Generator check.** The misread fact is which document holds a section after `PL-CTXZ` (moving the interface sections out of `docs/MODEL.md`) moved it. No head's `misread:` line states it. The same fact was misread by `PL-CVTG` (done: items whose `touches` named the old document) and by `PL-GC7Z` (open: a comment citing a `docs/MODEL.md` note with no section mark). The mechanism the three share is that a citation written as a comment, a possessive or a bare § is invisible to the document check, so a move of a section strands it silently. That is a candidate generator, because `PL-48MX` and `PL-SY7G` (the later stages of splitting the two documents) will move more sections. It is reported to the coordinator rather than recorded here, since no open item yet holds the fix to the check.

**Done 2026-11-22.** Every mention of `docs/MODEL.md` in the five places the brief names was read against the four documents as this branch has them. Each one that meant a statement now in another document names that document and the section that states it, in the form `docs/INTERFACE.md` § "Heading". Comments, docstrings, assertion messages and document prose changed. No code, value or test logic did. The 34 mentions in five tests under `tests/reference/` are split out as `PL-KNHK`, because an edit to an existing line there waits for the owner's read; that commit is saved as a patch that `PL-KNHK` names.

1. **To `docs/INTERFACE.md`, 40 mentions.** They cover the unconditional set and its tiers, the reachable views, naming the run in a comparison, the stop at the supported run length, the hover readout, the price form, the trace and agent colours, and the minimum displayed outputs. They are in `src/anesthesia_sim/app/` (21), `src/anesthesia_sim/data/workspaces/__init__.py`, 14 places in `tests/unit/` and `tests/integration/`, three comments in `tools/contrast_check.py` and one paragraph of `docs/ARCHITECTURE.md`.
2. **To `docs/VERIFICATION.md`, 12 mentions.** They cover the zero-flow tests, the reproducibility guarantee, the hazard table, the mass-balance halt, the release gate and the parameter-recovery test that cites Lerou and Booij.
3. **To `docs/PARAMETERS.md`, 4 mentions.** Each names the provenance table, in `core/parameters.py`, `core/circuit.py` and `docs/machine-abstraction.md`.
4. **Split, 3 mentions.** The opening of `docs/ARCHITECTURE.md` now sends each topic to its own document, and so does its rule for a new compartment. The module docstring of `tests/unit/test_dashboard_frame.py` names the two documents that cite its tests.
5. **Left on `docs/MODEL.md`, with the section added or put in the readable form, 20 mentions.** These are the equations, the symbols, the breathing circuit and the absorption limitation, in `core/` and its unit tests, `docs/ARCHITECTURE.md` and `docs/machine-abstraction.md`.
6. **`tests/reference/`, 34 mentions, in a separate last commit.** Two assertion messages in `test_coupled_dynamics.py` now name `docs/INTERFACE.md` § "Supported input ranges" and § "Displayed precision". Twenty move to, or add, `docs/VERIFICATION.md`, mostly § "The first 24 hours of elimination against the published mean curves" and § "Desflurane's residual, and why the parameter file was not changed". Twelve stay on `docs/MODEL.md` with their section added. If that commit is dropped, these 34 mentions stay as they were.

**Left as they are.** These mentions still mean `docs/MODEL.md`, or are not a citation:

- the refusal messages in `core/patient.py`, `core/blood.py`, `core/blood_flow.py` and `core/validation.py`, and the unit tests that match them. They name a section that `docs/MODEL.md` still has, and changing them would change what the program prints;
- sentences that record what `docs/MODEL.md` said at the time, such as `tests/unit/test_supported_ranges.py`'s opening and `tests/unit/test_parameters.py`'s account of `PL-H1JH`;
- the fixtures of the tests of the workflow's own tools, such as `tests/unit/test_doc_check.py`, which use the path as data;
- the `sources` notes in `src/anesthesia_sim/data/`, which are stored strings and not comments. Three of them point at the wrong section, as the next paragraph says.

**Found and not fixed.** The `sources` notes of `data/agents/sevoflurane.json`, `isoflurane.json` and `desflurane.json` say that `docs/MODEL.md` "Known limitations" carries the 22% displacement of a cross-agent comparison at 1 MAC. `docs/MODEL.md` states it under § "MAC multiples", and `docs/PARAMETERS.md` § "The stored MAC" gives the evidence. In the same way, `data/patients/reference_adult.json` says that `docs/MODEL.md`'s "Known limitations" says that the cardiac-output relation is not a measured cardiac output. `docs/MODEL.md` says it under § "The reference adult".

*Data-file notes, 2026-11-22.* The four notes above were re-pointed by PL-48MX in #2222 (dfbf18f9). Two more notes, in `data/agents/sevoflurane.json` and `isoflurane.json`, said that `docs/MODEL.md` requires the MAC-awake band to be read against the vessel-rich trace. That requirement is in `docs/INTERFACE.md` § "MAC-awake as a chart reference", and both notes now name it. The `_run_name` docstring in `app/simulation_view.py`, which #2229 rewrote, keeps its pointer to `docs/INTERFACE.md` § "Naming the run in a comparison".

**Documents checked.** Every heading cited by the branch was compared, character for character, with the headings of `docs/MODEL.md`, `docs/INTERFACE.md`, `docs/VERIFICATION.md` and `docs/PARAMETERS.md`. `grep -rn 'MODEL.md' src tests tools/contrast_check.py docs/ARCHITECTURE.md docs/machine-abstraction.md` was read line by line.
