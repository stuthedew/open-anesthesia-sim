---
id: PL-H1GH
title: "Cut the v0.4.7 release: the supported run length, the tolerance gate, and traces you can tell apart"
priority: P2
effort: S
status: done
classes: planning
feature: release-process
milestone: v0.4.8
touches: ROADMAP.md, pyproject.toml, uv.lock, docs/releases, docs/items/
added: 2026-09-07
closed: 2026-09-07
pr: 425
verify: grep -q '^version = "0.4.7"' pyproject.toml && test -f docs/releases/v0.4.7.md && grep -qF '## Current baseline: v0.4.7' ROADMAP.md && grep -qF '| v0.4.7 | Completed / current baseline |' ROADMAP.md
---

**Problem.** Ten items finished since v0.4.6 with no release carrying them, and
`ROADMAP.md`'s `v0.4.x` row says patches are cut as work accumulates. The cut
itself takes a commit of its own, so it is filed rather than done unfiled
(`CLAUDE.md`, housekeeping nobody filed).

**Why now rather than earlier.** This was offered twice and declined once on
its own merits. When it was first raised the only releasable item was
`PL-5VR1`, the item that cut v0.4.6 — a release whose whole content is the
bookkeeping of the previous release crosses no boundary and is not worth a
number. What changed is that nine more merged, three of them safety- or
science-classed, and the reason given for holding (four sessions still in
flight) was spent when all four of their pull requests landed.

**What it carries.** `PL-Y5WR` (the supported run length and its halt),
`PL-ZVS7` (the control-resolution tolerance gate), `PL-GVXP` (chart traces
separated by line style, held to 3:1 in four vision models), `PL-3YZW`,
`PL-8ZJQ` and `PL-BD94` (the venous pool's first source and its rename),
`PL-KX9N` (shallow-clone provenance in `docket record`), `PL-QPJZ`
(`bin/docket trend`), `PL-LYX2` (the 2026-09-06 triage pass) and `PL-5VR1`
(the v0.4.6 cut).

**One thing this cut did that the procedure does not name.** The first
`make release` produced notes in which five of the ten items carried no pull
request number, because they had merged without one being recorded and the
notes are generated from the store. Rather than hand-edit generated notes, the
cut was reverted in the working tree, `bin/docket record` was run to write all
five, and the release was cut again. That is the skill's own rule — let the
`record` write ride a commit you are already making — applied to the one commit
in the project that is always available to it. Recorded here because the next
cut will meet the same condition whenever items merge faster than commits are
made against `main`.

**Done when.** `make release VERSION=0.4.7` has run, `ROADMAP.md` carries the
version-table row and the moved baseline, `make check` passes, and the tag is
outstanding with the owner.

**Closed 2026-09-07.** Cut with `make release VERSION=0.4.7`; version-table row
and `## Current baseline: v0.4.7` written; every item in the notes carries its
pull-request number. The tag is the project owner's to push and is outstanding
until they confirm it.

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.4.7 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item. The row's first sentence, which stays in the table, reads: "**Three claims the model made without defending, and the first stored parameter to leave the Gas Man set.**" In the quote, § "Supported simulation step" is `docs/MODEL.md`'s.

> Each of the three had been asserted in prose and enforced by nothing, and each turned out to be wrong or unenforced in a way only the enforcement could show. **The run length was a memory limit wearing a modelling limit's clothes.** A 30-day cap was set on 2026-08-25 to size a concentration history that no longer exists, was carried forward as though it described the model, and was enforced nowhere at all: nothing in `core/` or `app/` bounded elapsed simulated time, so a run could reach day 45 of a 30-day cap and go on displaying two-decimal concentrations. It is now **24 hours**, and the number moved *down* by more than an order of magnitude because the question changed: the item proposed the fat group's ~42 h time constant as a scale to take multiples of, which inverts the relationship - many multiples of the slowest mode is precisely the regime `docs/MODEL.md` § "Published wash-in and elimination validation test" already refuses to validate over, having rejected the Yasuda papers' own multi-day elimination curves because over days the missing metabolism is no longer negligible and neither is the fat group's flow. What binds a run length is what the model omits, so the fat time constant is a floor and not a multiplier. Sevoflurane is the binding agent at 2% to 5% of the absorbed dose, beginning within minutes rather than late (Kharasch 1995, marked tier 2 in both the code and the specification, because 24 hours is a declared envelope argued against the omission and not a figure computed from a metabolic rate). Enforcement is an integer step-count comparison derived once per step size, so the boundary falls at the same step on every machine and deterministic replay holds across it; the interval is closed like the four flow ranges, a run completing exactly 864 000 steps of 0.1 s to land on 86 400.0 s before the next is refused. And reaching it is **not a failure**: `SimulationDomainLimitError` subclasses the execution branch so a caller that knows only the base classes still stops the run, while `app/` reads the specific type to say "Stopped - supported run length reached" in place of a failure banner describing a rollback that did not happen. Telling a learner the simulator broke when it stopped exactly where the specification says it must spends the one signal the interface has for a real fault. **The control-resolution tolerance was three published numbers no test computed.** § "Supported simulation step" publishes the displacements the step bound *is* since `PL-X9KD` retired its accuracy derivation, and `grep` for them across the suite returned one unrelated comment: a change to an equation, a partition coefficient, the reference adult's volumes or the supported envelope would have moved them silently while both documents kept asserting the old figures. `tests/reference/test_control_resolution.py` now drives each manoeuvre twice from an empty system in lockstep, differing only in when the control change lands, and every published figure reproduced - 6.66e-3, 5.03e-2 and 1.43e-1 pp at 1x, and 1.43e-1, 6.95e-1, 2.51, 5.83 and 1.04e1 pp down the per-rate column - with the gate mutation-checked rather than assumed, a 0.2 s step, a 2 L/min wider ventilation envelope, an 0.42 to 0.50 desflurane blood:gas and a 2.5 to 2.8 L alveolar volume each failing it. **It found a defect on its first run**: the specification read "the case opening is two orders milder at every rate" where it is 21x milder at 1x and 6.9x at 300x, the binding manoeuvre's displacement saturating while the case opening's stays nearly linear in the delay, so a reader budgeting an ordinary dial change at 60x would have inferred about 0.06 pp against a true 0.375 pp. **The six chart traces were separable only to normal vision.** Contrast composes along a bounded axis, so no palette of six clears 3:1 pairwise and the fix could never have been a re-pick; the traces now carry line style as a second channel, and `tools/contrast_check.py` gained the Brettel 1997 projection with a hard floor holding every trace to 3:1 against the panel in four vision models. That floor immediately found what no normal-vision check could see - `MUSCLE_COLOR` at 3.19:1 as displayed and **2.98:1** simulated for deuteranopia - and corrected the specification's own dichromacy claim about the ISO 5360 agent colours from "1.1-1.4" to a measured 1.06 to 1.48. **And the venous pool got a source, which it had never had.** `venous_blood_volume_l` = 1.0 L entered at v0.1.0 under a Workbook citation belonging to its neighbours; the Workbook's Blood row reads 5.00 L and no 1.0 L figure appears in it anywhere. Davis and Mapleson 1981 states, for models of inhaled anaesthetics specifically, that the two venous pools may be combined into one of **1222 ml**, 23.6% of their standard man's 5189 ml blood volume - the same object as this model's single well-stirred venous pool - and that value is adopted on the project owner's decision, the first parameter in `reference_adult.json` to carry a source other than Gas Man. It is tier 2 and stays unadopted-as-measurement: the Appendix derives the pool from ICRP (1975) blood distribution to reproduce circulation times rather than measuring it. The competing hypothesis was tested and failed - `PL-8ZJQ` had suspected 1.0 L was an arterial compartment under a venous name, on Lerou and Booij's arterial fraction of 0.2, and Davis and Mapleson's own arterial pool for an inhaled-anaesthetic model is 799 ml at 15.4%, so the coincidence does not survive the primary source. The key is renamed `venous_pool_volume_l` in the same change, because it names a mixing volume and read as the physiologic venous blood volume. **This is the first release since v0.4.4 in which a displayed number moves, and the only one in which a stored parameter does.** The mixed-venous time constant V_v/Q goes from 12.0 s to 14.7 s at the stored 5.0 L/min, visible on the mixed-venous trace through the first minute of every simulation; the 30-minute F_A/F_I wash-in distances are unchanged to two decimal places, the pool being long equilibrated by then, and the 5-minute F_A/F_A0 elimination ratios move 0.11 to 0.13 published SD *further* from their cohort means - the same direction the module already attributes to this model's rebreathing circuit rather than to tissue return. No equation, numerical method or solver step moved. Three apparatus items close beside them: `bin/docket record` had written pull-request numbers a shallow clone could not verify, `bin/docket trend` makes the workflow-to-product balance a command rather than a session's derivation, and thirty-one captures from one day were triaged into the queue. Ten items, one of which is the v0.4.6 cut itself.
