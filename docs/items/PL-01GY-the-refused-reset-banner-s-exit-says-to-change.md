---
id: PL-01GY
title: The refused-Reset banner's exit says to change the setting the refusal names, and a tissue-flow mismatch names the cardiac output, which since PL-HQF5 repairs nothing because a new output scales every flow by the same factor; the mismatch is now reachable only by a perfusion fraction written past its guard
priority: P2
effort: S
status: done
classes: defect
feature: cardiac-output-write-consistency
touches: src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/run_view.py, tests/integration/test_simulation_view.py, tests/unit/test_dashboard_frame.py, docs/MODEL.md, docs/ARCHITECTURE.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science: no learner can reach the banner it corrects
added: 2026-10-18
closed: 2026-10-18
pr: 1572
payoff: a Reset the core refuses tells the reader the one way out that works, rather than a dial that cannot repair it
verify: grep -q 'def test_a_refused_reset_names_no_setting_and_sends_the_reader_to_restart' tests/integration/test_simulation_view.py
---

**Problem.** The refused-Reset banner's exit says to change the setting the refusal names, and a tissue-flow mismatch names the cardiac output, which since PL-HQF5 repairs nothing because a new output scales every flow by the same factor; the mismatch is now reachable only by a perfusion fraction written past its guard

The rationale comment above `REFUSED_RESET_REPAIR_TEXT` in
`src/anesthesia_sim/app/dashboard_frame.py`, and the `refused_reset_exit`
docstring, still say the named setting's dial rebuilds the record. Change
them with the banner text.

**Why it matters.** The banner's last sentence is the one instruction a
stopped run gives its reader. After `PL-HQF5` and `PL-Z0HN`,
`SimulationController.reset()` can be refused only on tissue flows that do not
sum to the cardiac output. Every flow is now formed from the output, so a new
output scales them all by one factor and the sum still disagrees. The only way
to build that record is to write a perfusion fraction past its guard, which no
shipped code does. So the banner sends the reader to a dial that cannot help,
on a state that only a fault in the simulator can produce. The run view's
docstrings and `docs/MODEL.md` (§ "Reset behavior" and the halt row of its
display-defect table) say the same thing.

**Decided here, 2026-10-18.** The exit names no setting. It says that no
setting can repair the refusal, because only a fault causes it, and names the
one way out open on every run: close and reopen the application. A new case
was considered and refused again, for the reason `PL-TFX5` gave: a branch has
no agent selector, and a comparison hides the trunk's. The constant is renamed
`REFUSED_RESET_WAY_OUT_TEXT`, since it no longer names a repair. An accepted
setting still lifts the exit, because a setting is accepted only once the
record builds again, and then Reset takes. No learner can reach this banner,
so the wording is not the owner's question under rule 14's test.

**Done when.** The refused-Reset exit names no setting and tells the reader to
close and reopen the application. A test pins that sentence from a literal,
and shows that moving the cardiac output dial on the refused run leaves the
exit standing and Reset still refused. The comment, the docstrings and
`docs/MODEL.md` describe the new exit.

**Regression proof, 2026-10-18** (`.claude/rules/test-oracles.md` rule 6). With
`src/` stashed back to `#1537`'s head `3ba26dcf` and the test's import pointed
at the old `REFUSED_RESET_REPAIR_TEXT`, `uv run pytest
tests/integration/test_simulation_view.py -k names_no_setting_and_sends` fails
with `AssertionError: assert False`: the banner ends "Reset was refused for
this reason. Change the setting it names, then Reset." where the test expects
the new sentence.
