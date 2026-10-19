---
id: PL-5N95
title: Record the forkserver whole-tree mutation baseline that make mutate ARGS=--all measures in docs/mutation-testing.md, beside the 2026-10-17 fork-mode audit baseline, so the two modes and the 33-file and import-rule test selections can be compared
priority: P3
effort: M
status: done
classes: infra
feature: test-effectiveness-measurement
milestone: v0.5.31
touches: docs/mutation-testing.md
deferred-from: v0.6.0 - captured after the freeze, and not safety or science
added: 2026-10-17
closed: 2026-10-19
pr: 1601
payoff: a later mutation kill rate has a baseline in its own mode to be compared against, so a drop is not mistaken for the change of mode
verify: grep -qE '^### .*forkserver' docs/mutation-testing.md
---

**Problem.** Record the forkserver whole-tree mutation baseline that make mutate ARGS=--all measures in docs/mutation-testing.md, beside the 2026-10-17 fork-mode audit baseline, so the two modes and the 33-file and import-rule test selections can be compared

**Why it matters.** `docs/mutation-testing.md` § "Baselines" holds one
measurement, the 2026-10-17 audit in fork mode over 33 hand-listed test files.
`make mutate ARGS=--all` now runs in forkserver mode and selects tests by the
import rule, and the same file says that mode reported about 49 mutants as
surviving that fork mode killed. Until a whole-tree forkserver run is recorded,
a later kill rate has nothing in its own mode to be compared against, so a drop
cannot be told apart from the change of mode.

**Done when.** § "Baselines" holds a second table from one `make mutate
ARGS=--all` run in forkserver mode, with its commit, mutant counts and per-module
kill rates, and says how it differs from the fork-mode table. The run took about
75 minutes for 1,058 of 2,498 mutants on 2026-10-17, so it needs a session that
can wait about three hours.

**In progress 2026-10-18 on `#1601`.** The run started at 20:22 UTC in a
separate worktree at `d7c1d74c` (`make mutate ARGS=--all`, forkserver mode,
45 simulator test files under `tests/unit/`). Next step: when it finishes, add
the second table under § "Baselines" in `docs/mutation-testing.md` with its
commit, mutant counts and per-module kill rates, say how it differs from the
fork-mode table, then close this item on `#1601`.

**Done 2026-10-19 on #1601.** `docs/mutation-testing.md` § "Baselines" now
holds the forkserver whole-tree table at `d7c1d74c`: 2,489 mutants, all
tested, 2,237 killed, 235 survived, 15 timed out and 2 killed by a signal,
about 90%. Each module row also gives the fork-mode rate, and the section says
how the process mode, the test selection and the code differ between the two.
A container restart stopped the run at 2,435 mutants, and `mutmut run` in the
same `mutants/` directory finished the last 54.

