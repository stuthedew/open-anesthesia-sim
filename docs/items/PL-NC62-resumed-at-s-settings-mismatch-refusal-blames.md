---
id: PL-NC62
title: resumed_at's settings-mismatch refusal blames the control timeline whatever the cause, so a patient or agent mismatch would be misdiagnosed
status: untriaged
added: 2026-09-14
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
