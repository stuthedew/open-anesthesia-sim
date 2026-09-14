---
id: PL-0PJG
title: agent_identity_check prints 'none of them rendered disabled' from an empty measurement set, so the affirmative sentence cannot be told apart from the same sentence earned
priority: P1
effort: S
status: ready
classes: defect, safety, infra
feature: qt-port
touches: tools/agent_identity_check.py, tests/unit/test_agent_identity_check.py, docs/ARCHITECTURE.md
added: 2026-09-14
verify: uv run pytest tests/unit/test_agent_identity_check.py && grep -q 'def test_an_identity_set_with_no_disabled_write_read_anywhere_is_an_error' tests/unit/test_agent_identity_check.py
---

**Problem.** agent_identity_check prints 'none of them rendered disabled' from an empty measurement set, so the affirmative sentence cannot be told apart from the same sentence earned

**Why it matters.** This check guards ISO 5360 agent colour - that no control
carrying the agent's identity is rendered in Material's disabled grey (project
owner, 2026-09-08; `PL-61WW` is what it cost once). `PL-JRS3`'s probe B
measured the failure on 2026-09-14: on a tree where all six identity controls
are driven by `setEnabled()` with no paired hide, `property_writes` read no
`disabled` assignment at all, the pairing loop ran zero times, and the tool
printed

    agent-identity: 6 control(s) carry the agent colour, none of them rendered disabled

and exited 0. The sentence is an affirmative claim about a tree the check did
not measure, and a reader has no way to tell it from the same sentence earned.
That is worse than silence: `CLAUDE.md`'s first compounding-friction test is a
check passing while the guarantee it stands for is void, and this one passes
*and says so*. The tool already refuses an identity set that comes back empty,
on the stated principle that a coverage set which can silently go empty is
worse than no check; the measurement set rule 1 reads has the same property
and no guard.

**Done when.** A tree whose identity set is non-empty but in which no
`self.<control>.disabled = ...` assignment is read in any module under
`src/anesthesia_sim/app/` is an error that names the spelling the check reads
and the one it does not (PySide6's `setEnabled()`), so the port trips it on
its first commit rather than passing through it. The success line carries the
measurement it rests on - how many disabled-state writes were read, across how
many modules, how many of them on identity controls - so the affirmative
sentence cannot be printed from nothing. A regression test reproduces probe B
and asserts the error. A tree that genuinely disables nothing anywhere trips
the same error, deliberately: the check cannot tell that tree from one it
cannot read, and saying so is the honest answer.
