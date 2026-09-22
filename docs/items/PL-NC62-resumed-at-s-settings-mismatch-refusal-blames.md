---
id: PL-NC62
title: resumed_at's settings-mismatch refusal blames the control timeline whatever the cause, so a patient or agent mismatch would be misdiagnosed
priority: P2
effort: S
status: ready
classes: defect, ux
feature: scenario-branching
touches: src/anesthesia_sim/app/controller.py, tests/integration/test_controller.py
added: 2026-09-14
verify: grep -q 'def test_a_settings_mismatch_names_the_setting_that_differs' tests/integration/test_controller.py && uv run pytest tests/integration/test_controller.py
---

**Problem.** resumed_at's settings-mismatch refusal blames the control timeline whatever the cause, so a patient or agent mismatch would be misdiagnosed

`src/anesthesia_sim/app/controller.py`'s `resumed_at` rebuilds the branch
through the ordinary constructor and then checks the settings it ends up with
against the ones the trunk's own stretch carries, refusing if they differ. The
check is right and is what stops a branch solving equations its parent never
did. The message is not:

> the settings replayed for a branch at {t} s are not the ones this run was
> computed under there, so the branch would solve equations its parent never
> did; the recorded timeline does not reproduce its own segments

The last clause names one cause. The rebuild also re-reads the agent, patient
and machine JSON from disk, so a data file edited between the trunk being built
and the branch being taken would fail this same check with the timeline
blameless — and so would a future patient selection that did not travel with
the fork. `CLAUDE.md`'s safety-critical standard asks a refusal to name what
was refused; `core/supported_ranges.py` is the shape. State the disagreement —
which settings differ, and by how much — and leave the cause to the reader.

**A second, narrower gap beside it.** Three agent-derived values the branch
re-reads sit outside the guard entirely, because they are not part of
`UptakeEquationSettings`: `agent_mac_percent` — the divisor of every MAC-multiple
the interface displays — `agent_display_name`, and
`max_delivered_concentration_percent`. They agree today because the branch
re-reads the same file under the same agent id; nothing asserts it.

Found while working `PL-TFX5`.

**Verified 2026-09-14.** `app/controller.py:960-966`. The comparison is
`replayed != resume_point.segment.settings` - a single equality over the whole
`UptakeEquationSettings` object - and the message is fixed text ending "the
recorded timeline does not reproduce its own segments". Any field can trip it;
only one cause is ever named.

**Why it matters, and it is not only a wording problem.** The message states a
diagnosis rather than an observation, and it states the one diagnosis the
reader can least act on. A patient or agent mismatch reaching this comparison
would be reported as a timeline defect, sending whoever debugs it into the
control-input record - the one part of the system that is working.
`CLAUDE.md`'s standard treats a misleading message a reader acts on as part of
presentation correctness, and `.claude/rules/expert-review.md` asks for
interfaces that prevent an error rather than mis-explain it after.

**`PL-SM5V` is how this fires in practice, and the two should be read
together.** That item measures 7 of 101 cardiac outputs failing to round-trip
through the L/min-to-L/s conversion. `UptakeEquationSettings` is frozen and
compared by value, so a replayed settings object that differs from the recorded
one in the last bits of `cardiac_output_l_s` is unequal here - and the learner
is told their recorded timeline does not reproduce its own segments, when what
actually happened is a float conversion. That is a real path to a wrong,
confident explanation of a correct run.

**Done when.** The refusal names the field or fields that differ and their two
values, rather than attributing every mismatch to the control timeline - so a
patient, agent or flow difference reads as itself. `tests/integration/` covers
a mismatch in a field other than the timeline's own.
