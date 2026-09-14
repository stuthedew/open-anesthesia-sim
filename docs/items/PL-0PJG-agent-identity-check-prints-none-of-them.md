---
id: PL-0PJG
title: agent_identity_check prints 'none of them rendered disabled' from an empty measurement set, so the affirmative sentence cannot be told apart from the same sentence earned
priority: P2
effort: S
status: ready
classes: defect
feature: dev-tooling
touches: tools/agent_identity_check.py, tests/unit/test_agent_identity_check.py
added: 2026-09-14
verify: uv run pytest tests/unit/test_agent_identity_check.py && grep -q 'def test_an_empty_identity_set_is_not_a_pass' tests/unit/test_agent_identity_check.py
---


**Problem.** agent_identity_check prints 'none of them rendered disabled' from an empty measurement set, so the affirmative sentence cannot be told apart from the same sentence earned

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
