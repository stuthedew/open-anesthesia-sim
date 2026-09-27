---
id: PL-NC62
title: resumed_at's settings-mismatch refusal blames the control timeline whatever the cause, so a patient or agent mismatch would be misdiagnosed
priority: P2
effort: S
status: done
classes: defect, ux
feature: scenario-branching
milestone: v0.5.16
touches: src/anesthesia_sim/app/controller.py, tests/integration/test_controller.py, docs/ARCHITECTURE.md
added: 2026-09-14
closed: 2026-09-27
pr: 1188
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

## Done 2026-09-27

`SimulationController._branch_from` now refuses on
`_disagreements_with`, which lists every value the rebuilt branch holds that
the trunk did not, each as `<name> is <value> in this run and <value> on the
branch`, and names no cause. The equation settings are walked with
`dataclasses.fields`, every tissue group field by field under the group's
name, so the list covers exactly what the old whole-object equality compared.
Values are written by `repr`, so two values that differ never print alike. The
message ends by pointing at `docs/ARCHITECTURE.md` § "What a branch is, and
what it shares with its parent", which states why a branch may not differ from
its trunk.

**The second gap is closed too, decided here.** The brief named it and the
Done-when did not require it. The agent's displayed references are checked
beside the settings: the display name, the vaporizer maximum, the MAC, and
MAC-awake, which arrived after this brief was filed and is the same kind of
value. The MAC divides every MAC multiple on screen, so a branch rebuilt under
another MAC would show one concentration as two multiples beside its parent.
Checking it costs four comparisons.

**`PL-SM5V` does not reach this check, measured against the tree.** The brief
says it does, and it no longer can. `_branch_from` replays the four live
controls from the recorded timeline in litres per minute, which are the units
the compartments hold, and never recovers them from the segment's litres per
second. The division by sixty is therefore the same on both sides. The
`resumed_at` docstring says the same thing and cites `PL-SM5V`, and
`test_a_branch_inherits_its_parent_s_settings_at_the_fork` holds equality at
every keyframe. The reachable path today is a data file that changed between
the trunk's build and the branch's.

Tests in `tests/integration/test_controller.py`:
`test_a_settings_mismatch_names_the_setting_that_differs` (agent blood:gas,
and the trunk is left untouched), `test_a_patient_mismatch_names_the_tissue_group_it_is_in`
(muscle volume), and `test_a_branch_rebuilt_under_another_mac_is_refused`
(the second gap). All three fail on the previous controller; the last fails
with "DID NOT RAISE".
