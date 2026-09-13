---
id: PL-3LLZ
title: Four fakes in test_vcs.py each answer the same commit-paths question, and each new git read has to be taught to all of them
status: ready
priority: P3
effort: M
classes: refactor
feature: dev-tooling
touches: subprojects/docket/tests/test_vcs.py
verify: uv run pytest subprojects/docket/tests/test_vcs.py && grep -q 'def _default_run' subprojects/docket/tests/test_vcs.py
added: 2026-09-13
---

**Problem.** Four fakes in test_vcs.py each answer the same commit-paths question, and each new git read has to be taught to all of them

**Found while closing `PL-YDL6`, 2026-09-13.** Teaching the module one new git
question - the paths a commit changed - meant editing four separate fakes in
`subprojects/docket/tests/test_vcs.py`: `_runner`, `_rename_runner`,
`_closure_runner` and `_recovery_runner`. Each grew the same three-line branch
answering `diff --name-only`, and each was found by running the suite and reading
which tests broke rather than by knowing in advance which fakes were involved.

**Why it matters, and why it is not urgent.** It is upkeep cost rather than a
correctness risk: the fakes are independent by design, each shaped to the question
its own tests ask, and that independence is part of why they are readable. What it
costs is that every future read added to `vcs.py` pays the same four-way edit, and
the failure mode is a test breaking for a reason unrelated to what it tests -
which is a slow way to learn where the fakes are.

`.claude/rules/apparatus-standard.md` is the bar here: duplicated logic is
explicitly what to cut, and robustness is explicitly not. So this is a
consolidation only where it does not cost the per-fake clarity.

**Approach, undecided.** A shared default `run` that answers the questions no test
has an opinion about, with each fake overriding only what it cares about, is the
obvious shape. The risk is the opposite failure: a fake that silently answers a
question its test never considered, which is how a test comes to pass for the
wrong reason. Worth doing only if the shared half stays limited to reads whose
answer is genuinely uniform.

**Done when.** A new git read added to `vcs.py` can be answered for the whole of
`subprojects/docket/tests/test_vcs.py` in one place, with each fake still able to
override what its own tests turn on; the suite passes unchanged; and no fake
answers a question whose answer its tests never considered - which is the failure
this consolidation risks and the reason it is worth doing only for reads whose
answer is genuinely uniform.
