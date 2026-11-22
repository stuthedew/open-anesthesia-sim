---
id: PL-C11P
title: The docstring of BranchedCase.fork_points_s says fork_at rejects any instant that is not a keyframe, but fork_at accepts any whole second the trunk has reached since whole-second stepping
status: done
feature: run-computed-one-way
milestone: v0.6.21
touches: src/anesthesia_sim/app/controller.py
added: 2026-11-22
closed: 2026-11-22
pr: 2246
verify: ! grep -qF 'rejects any other instant' src/anesthesia_sim/app/controller.py
---

**Problem.** The docstring of BranchedCase.fork_points_s says fork_at rejects any instant that is not a keyframe, but fork_at accepts any whole second the trunk has reached since whole-second stepping

**Checked 2026-11-22**, by `PL-LZ54` (the check of the interface documents
after whole-second stepping). `BranchedCase.fork_points_s` in
`app/controller.py` says that `fork_at` "rejects any other instant" than the
trunk's keyframes (`PL-54V0`). `fork_at` passes its instant straight to
`SimulationController.resumed_at`, whose docstring and code accept any whole
second the trunk has reached (`PL-FST0`), and `fork_at`'s own docstring says
the same. `test_a_branch_at_any_whole_second_holds_its_trunks_states_up_to_that_second`
in `tests/integration/controller/test_controller_stored_states.py` branches
at seconds that are not keyframes. No test asserts the refusal.

**Why it matters.** A developer who trusts the docstring would add a check
that the code does not need, or rely on a refusal that does not happen.

**Done when.** The docstring says what `fork_at` accepts, and which instants
the interface passes it. `docs/ARCHITECTURE.md` § "What a branch is, and what
it shares with its parent" was corrected to the code by `PL-LZ54`.

**Done 2026-11-22**, on `claude/project-thread-v9awbd`, with `PL-LZ54`. The
docstring of `BranchedCase.fork_points_s` now says that the list is the set of
instants the interface offers to `fork_at`, and that `fork_at` itself accepts
any whole second the trunk has reached. The sentence that `fork_at` rejects any
other instant, and its reason, are gone.

Files checked: `src/anesthesia_sim/app/controller.py`,
`src/anesthesia_sim/app/dashboard_frame.py`, `docs/ARCHITECTURE.md` and
`docs/INTERFACE.md`, by `grep -rn "rejects any other instant\|is the scope of .fork_at"`.
None printed.

**Generator check.** The fact is the link between a docstring and the code
behaviour it restates, which whole-second stepping changed (`PL-FST0`). This
item is a copy that the build's own sweep missed, found by `PL-LZ54`, the
planned remainder of that sweep, so it is bookkeeping and not a re-entry.
