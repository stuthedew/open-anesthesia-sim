---
id: PL-0PJG
title: agent_identity_check prints 'none of them rendered disabled' from an empty measurement set, so the affirmative sentence cannot be told apart from the same sentence earned
priority: P1
effort: S
status: done
classes: defect, safety, infra
feature: qt-port
touches: tools/agent_identity_check.py, tests/unit/test_agent_identity_check.py, docs/ARCHITECTURE.md
added: 2026-09-14
closed: 2026-09-14
pr: 581
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

**What landed, 2026-09-14.** `analyze` counts every `self.X.disabled = ...`
assignment in every class of every module under `app/`. An identity set that
is non-empty while that count is zero is an error naming what was read and
what was not (`UNREAD_SPELLING`, PySide6's `setEnabled()`), so `PL-JRS3`'s
probe B - every identity control driven by the setter, no paired hide - now
fails with one problem instead of exiting 0, and a regression test holds it
there. The success line carries the measurement: on the shipped tree,
"3 disabled-state write(s) read across 11 module(s) under
src/anesthesia_sim/app/, 1 of them on identity controls and each paired with
its hide". The one fixture that had no `disabled` write anywhere - the
never-disabled identity control - keeps a `disabled` write on a control that is
not agent-coloured, with the reason in its docstring.

**Triaged twice on 2026-09-14.** A second pass (`PL-6FJ5`, `PL-66X4`) verified
the finding independently and triaged it at `P2` under `dev-tooling`; the
fields above are the project owner's (`P1`, `safety`, `qt-port`, 2026-09-14),
and the work closed on that basis. The second pass's verification and brief
follow unchanged, because a merge that keeps one of two answers is what
`PL-N1JK` recorded, and its "Done when" is compared against what landed
where the two differ.

**Verified 2026-09-14.** `tools/agent_identity_check.py:318` builds the
affirmative sentence unconditionally, and the module's own docstring at `:78`
records the failure having already happened once: it printed `... colour, none
of them rendered disabled` and exited 0 on a tree where all six controls were
absent. So the sentence is emitted from a set of size zero and from a set of
size six that all passed, and nothing in the output separates them.

**Why it matters.** This is the failure mode `CLAUDE.md` names when it says a
tool that guesses at the judgment half "is worse than no tool, because its
output looks authoritative and is not" - except here the tool is not guessing,
it is reporting a vacuous truth in the grammar of an earned one. A reader who
refactors the identity controls out of the file it reads gets a green line
saying the property holds. The property is about agent identity colour, which
is ISO 5360 identification carried into the interface, so the guarantee being
silently voided is one about a displayed clinical cue rather than about style.
`PL-V53R` is the other half of the same weakness in the same file - the surface
the check reads - and the two are worth doing in one pass.

**Done when.** The check distinguishes an empty measurement set from a measured
pass: a run that finds no identity control at all says so and does not print the
affirmative sentence, and `tests/unit/test_agent_identity_check.py` has a test
that fails if an empty set is ever reported as a pass.
