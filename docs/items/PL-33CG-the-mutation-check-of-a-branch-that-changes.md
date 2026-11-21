---
id: PL-33CG
title: The mutation check of a branch that changes core/ did not finish in an hour, because every core mutant also runs the 30 s generated-run test
status: untriaged
added: 2026-11-11
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
