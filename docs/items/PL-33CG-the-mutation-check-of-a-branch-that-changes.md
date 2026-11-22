---
id: PL-33CG
title: The mutation check of a branch that changes core/ did not finish in an hour, because every core mutant also runs the 30 s generated-run test
priority: P2
effort: S
status: ready
classes: session-cost
feature: tests-detect-wrong-values
touches: pyproject.toml, tests/unit/test_generated_runs.py, .claude/skills/docket/modes/close-out.md
added: 2026-11-11
payoff: A branch that changes the simulation core can read its full mutation verdict before it closes, instead of checking only the mutants its session picks.
---

**Problem.** The mutation check of a branch that changes core/ did not finish in an hour, because every core mutant also runs the 30 s generated-run test

**What happened.** On 2026-11-11 `make mutate` ran on the branch of `PL-GJ1W`
part (b), which adds `core/rounding.py` and changes the import of a constant
in nine other simulator modules. The run was stopped at a one-hour limit after
157 mutants, about 23 s for each. mutmut runs against a mutant the unit tests
that reach its function, and `tests/unit/test_generated_runs.py` reaches most
of `core/` and takes about 30 s. `.claude/skills/docket/modes/close-out.md`
gives five to eight minutes for a typical branch and 36 minutes for the
largest batch measured, 340 mutants on 2026-10-24, before that test existed.

**What it cost.** The session could not read the tool's verdict for the
branch. It read the 12 survivors recorded so far with `mutmut results`, fixed
the five in the new module, and ran mutmut on that module alone
(`mutmut run "anesthesia_sim.core.rounding.x_*"`, 35 mutants, all caught).
The mutants of the other changed functions were not run.

**Not decided here.** Whether the generated test is left out of mutation runs,
given a shorter form for them, or kept at this cost. Leaving it out loses the
only test that steps drawn runs. Found while building `PL-GJ1W` part (b).

**Checked 2026-11-22**, at `d4e8200c`. The cost is still there. `tests/unit/test_generated_runs.py` still sets `EXAMPLES = 100`, and the `--deselect` list in `pyproject.toml`'s `[tool.mutmut]` table does not name it, so every mutant of a function it reaches still runs it in full. The test was added on 2026-11-10 by #2100 (`PL-GJ1W`), after the measurements that `.claude/skills/docket/modes/close-out.md` gives.

**Why it matters.** Every branch that changes `core/` must read the mutation tool's verdict before it closes, and that verdict now takes longer than a session can wait. A session that cannot read it does what this one did: it checks only the mutants it chooses, and the rest of the changed code goes without the check that the tests detect a change to it. The cost is paid again on every such branch.

**Done when.** A mutation run of a branch that changes several `core/` modules finishes in about the time `close-out.md` gives for a typical branch, and the run's record says how the generated-run test takes part: left out with its reason, run in a shorter form, or kept with the measured cost. The choice is the session's, because it rests on a measurement of how many mutants the generated test kills that no other unit test kills.

**Generator check.** The misread fact is what a mutation run costs per mutant: mutmut runs every unit test that reaches a mutated function, so one slow unit test multiplies the run by the number of mutants it reaches. No head's `misread:` line states it. `PL-SGBT` (mutants rerun one at a time) and `PL-R8HY` (the slow first step) share the feature but not this mechanism, so this is a one-off.
