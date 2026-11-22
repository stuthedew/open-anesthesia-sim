---
id: PL-Y33V
title: docs/MODEL.md gives sevoflurane fat and muscle time constants as about 42 h and 135 min in three chapters, but § 'Alveolar gas' tabulates 46 h and 172 min, and only § 'The first 24 hours...' says these are two kinds of time constant; each figure should say which kind it is (copy editor structure read, 2026-11-05)
priority: P2
effort: S
status: done
classes: defect, docs
feature: model-md-structure
touches: docs/MODEL.md, docs/INTERFACE.md, docs/VERIFICATION.md
deferred-from: v0.7.0 - not present at the freeze (817a4d88): the conflicting modal time constants came with 9ed29de4 (#1909)
added: 2026-11-05
closed: 2026-11-22
payoff: a reader meeting 42 h in one chapter and 46 h in another learns that both are right and which kind each is, and can check the run-length argument against the table
verify: grep -qF 'isolated time constant of about 42 h' docs/INTERFACE.md
recurrences: 2026-11-21 PL-HQQZ withdrawn 2026-11-21 PL-RMNP
---

**Problem.** docs/MODEL.md gives sevoflurane fat and muscle time constants as about 42 h and 135 min in three chapters, but § 'Alveolar gas' tabulates 46 h and 172 min, and only § 'The first 24 hours...' says these are two kinds of time constant; each figure should say which kind it is (copy editor structure read, 2026-11-05)

**Checked 2026-11-09:** On cfd4a4b6, three places give sevoflurane's muscle and fat time constants as about 135 min and 42 h, without saying which kind. They are § "Supported run length" ("Why 24 hours ..."), § "Interface boundary" (the playback-rate paragraph) and § "The chart's time base". The table in § "Alveolar gas" gives the whole system's slowest terms at the default flows as 10 300 s and 167 000 s, which are 172 min and 46.4 h. Both sets are correct. The first set is each tissue's own time constant, volume times tissue:blood coefficient over blood flow (§ "Tissue uptake and return"). From the reference adult's data that is 33 L x (2.4/0.65) / (0.18 x 5 L/min) = 135 min for muscle, and 14.5 L x (34/0.65) / (0.06 x 5 L/min) = 2 528 min = 42.1 h for fat. The second set is the coupled system's time constants, which are longer because tissue uptake also has to fill the blood and gas phases. No displayed value is computed from either figure. They are used only to argue the run-length limit and the chart widths.

**Why it matters.** A clinician who compares the two sets sees two figures for one tissue, 42 h and 46 h, and cannot tell which the simulator runs on, or whether one is an error. A developer who checks the 24-hour run-length argument ("about 0.6 of the time constant") against the table gets 0.52 instead. The conclusion survives, but the reader cannot confirm it.

**Done when.** Each of the three places that give 135 min and 42 h calls them the tissue's own time constant and points to the equation in `docs/MODEL.md` § "Tissue groups". § "Time constants" or one of those places says in one sentence that the coupled system's slowest terms, 172 min and 46 h at the default flows, are longer for the reason above.

**Generator check.** One-off: a finding from the `docs/MODEL.md` structure-read sweep. Two kinds of time constant are given under one name. No head's `misread:` states that fact.

**Checked 2026-11-09 against the tree at the freeze (`PL-GW0P`).** Not present. At 817a4d88, `docs/MODEL.md` gave 135 min and 42 h, but not the coupled system's 10 300 s and 167 000 s. Those came with `9ed29de4` (#1909, modal time constants), which created the unlabelled pair. The deferral stays with that reason.

**Checked 2026-11-22** against `d4e8200`: still applies, but the three places have moved. `PL-CTXZ` (#2109) moved them to `docs/INTERFACE.md`: § "Supported run length" ("about 42 h"), § "Interface boundary" ("about 135 min" and "about 42 h") and § "The chart's time base" ("about 135 min" and "about 42 h"). None of the three says which kind of time constant it gives. In `docs/MODEL.md`, § "Alveolar gas" still gives the slowest term as 47 000 s to 187 000 s with no sentence that relates it to the tissue's own figure. § "The first 24 hours of elimination against the published mean curves" already calls the 135 min figure the group's "isolated time constant" and explains why the model's term is longer, so the fix can use that name and point there. The equation the done condition points to is still in `docs/MODEL.md` § "Tissue groups".

**Built 2026-11-22**, on a branch that carries `PL-48MX` (the clinician's `docs/MODEL.md`) and the sorting of the other three documents by reader. `grep -n -E '42 h|135 min|46 h|172 min|isolated time constant' docs/MODEL.md docs/INTERFACE.md docs/VERIFICATION.md docs/PARAMETERS.md README.md` found the three unlabelled places in `docs/INTERFACE.md`, as the check above said: § "Why the limit is set where it is" (the run-length argument), § "What the reader chooses: traces, window and playback rate" (the playback-rate paragraph) and § "The chart's time base". `docs/MODEL.md` § "Time constants" now holds the table that § "Alveolar gas" held, and the explanation of why the model's term is longer is in `docs/VERIFICATION.md` § "The first 24 hours of elimination against the published mean curves", which calls 135 min the group's "isolated time constant". The tests use the same name.

Both sets of figures are right, and no figure changed. The isolated figures follow from the reference adult's data: 33 L x (2.4/0.65) / 0.9 L/min = 135.4 min for muscle, and 14.5 L x (34/0.65) / 0.3 L/min = 2 528 min = 42.1 h for fat. The coupled figures are pinned in `MODAL_TIME_CONSTANTS_S` in `tests/reference/test_coupled_dynamics.py`: 10 344 s = 172 min and 166 740 s = 46.3 h for sevoflurane at the default flows.

What changed:

1. `docs/MODEL.md` § "Tissue groups" names $`\tau_i`$ the group's isolated time constant, says what it means (the time constant the group would have if the arterial concentration stayed fixed), and points to § "Time constants".
2. `docs/MODEL.md` § "Time constants" gains a bullet that gives sevoflurane's two slowest terms at the default flows, about 172 minutes and 46 hours, against isolated time constants of 135 minutes and 42 hours, and says why the terms are longer. The reason is the one `docs/VERIFICATION.md` records for the open circuit (the lungs do not exhale all of a group's return, and the rest goes round again), with the circuit's rebreathing added. That addition rests on the figures: the open-circuit muscle term is 155 min and the circle's is 172 min. Four `derived:` markers tie 135 minutes and 42 hours to their inputs. The brief's wording of the reason, that uptake also has to fill the blood and gas phases, was not used, because no record in the tree states it.
3. Each of the three places in `docs/INTERFACE.md` now calls its figure sevoflurane's isolated time constant and points to `docs/MODEL.md` § "Tissue groups". The run-length paragraph now says that 24 hours is about 0.6 of the isolated time constant, and that the model's slowest term is somewhat longer, so 24 hours is a smaller fraction of it, with a pointer to § "Time constants".
4. `docs/VERIFICATION.md` § "The first 24 hours of elimination against the published mean curves" points its definition of the isolated time constant to `docs/MODEL.md` § "Tissue groups".

One place was left as it was. `docs/MODEL.md` § "Intertissue diffusion: the missing fourth compartment" says "The muscle group equilibrates in 85 to 135 minutes". Those are the isolated time constants of the three agents, and "equilibrates in" is loose for a time constant. `test_the_muscle_group_equilibrates_in_the_minutes_printed` in `tests/reference/test_known_limitations_figures.py` reads that sentence, so rewording it means changing the test, which is outside a documentation item.

**Documents checked.** `docs/MODEL.md` § "Tissue groups", § "Time constants" and § "Intertissue diffusion: the missing fourth compartment"; `docs/INTERFACE.md` § "Why the limit is set where it is", § "What the reader chooses: traces, window and playback rate", and § "The chart's time base"; `docs/VERIFICATION.md` § "The first 24 hours of elimination against the published mean curves"; `docs/PARAMETERS.md` (its one mention, the 85 to 135 minutes, names the test above and is still true); `README.md` (no time constant).
