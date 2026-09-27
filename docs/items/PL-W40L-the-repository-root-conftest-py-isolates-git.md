---
id: PL-W40L
title: The repository-root conftest.py isolates git for the docket and hook tests but sits on the product side of workflow_paths by omission, so an item touching it and the tests it serves is crossing
priority: P3
effort: S
status: done
classes: defect, infra
feature: parallel-sessions
touches: docket.toml, tests/unit/test_workflow_paths_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science
added: 2026-09-27
closed: 2026-09-27
pr: 1199
payoff: a change to how the test process is configured is offered to the apparatus lane rather than set aside by both
verify: grep -q 'def test_the_root_conftest_lands_with_the_apparatus_it_configures' tests/unit/test_workflow_paths_check.py
---

**Problem.** The repository-root conftest.py isolates git for the docket and hook tests but sits on the product side of workflow_paths by omission, so an item touching it and the tests it serves is crossing

**Evidence, 2026-09-27.** `conftest.py` at the repository root sets
`GIT_CONFIG_GLOBAL` and `GIT_CONFIG_SYSTEM` to `/dev/null` so that the tests
which build scratch repositories with real git - `subprojects/docket/tests/`
and the `.claude/hooks/` tests under `tests/unit/` - read none of the
developer's git configuration (`PL-YRYR`). Both of those are apparatus.
`docket.toml`'s `workflow_paths` does not list it, so it is on the product side
by omission, and `PL-YRYR` itself - `conftest.py`,
`subprojects/docket/tests/test_git_isolation.py`, `test_cli.py`,
`test_verify.py` and `subprojects/docket/README.md` - was `crossing` and
offered to neither lane.

It sits outside `tests/`, so `tools/workflow_paths_check.py` never reads it,
and `PL-12P8` has since made a support module's side the list's declaration
wherever its imports cannot decide it. This file's declaration is the default
nobody chose.

**Re-confirmed on starting, 2026-09-27: the problem holds, and the capture's
reason was half of it.** The file holds a second rule the capture did not
mention. Since `PL-0MLZ` (#1168, merged that morning) it turns bytecode writing
off for every pytest run, so that a source restored after a mutation is the one
that runs. That rule does change what the simulator's tests do - it keeps a
mutation test of `src/` honest - so the capture's reason, that "a git setting
changes nothing the simulator's tests do", no longer covers the file. The
placement holds on the fact the lane actually reads: what an item touching the
file touches beside it. Both rules are process configuration for the test
runner, and both have siblings already listed. The `Makefile` exports the same
bytecode variable to its own recipes, and `tests/unit/test_bytecode_guard.py`,
which holds this file to it, is in `workflow_paths`.

Reproduced through `Item.lane` against the list as `PL-12P8` leaves it: exactly
two items in the store declare the root `conftest.py`, and both read `crossing`
with every other path they touch on the apparatus side.

- `PL-YRYR`: `subprojects/docket/tests/test_git_isolation.py`, `test_cli.py`,
  `test_verify.py`, `subprojects/docket/README.md`.
- `PL-0MLZ`: `Makefile`, `docket.toml`, `tests/unit/test_bytecode_guard.py`,
  an item file.

With `"conftest.py"` listed, both read `workflow`. No item has ever declared the
file beside a simulator path, which is the count that would have made the
listing wrong.

**Why it matters.** A `crossing` item is ranked by neither `docket next
workflow` nor `docket next product`: each lists it as set aside for a session
that can hold both halves, which apparatus work never needs. Every change to
how the test process is configured - the two above, and the next - would be
held back that way.

**Recommendation, as worked.** List `"conftest.py"` in `workflow_paths`. The
prefix comparison, `docket.model.is_under`, matches it at the repository root
only, so `tests/conftest.py` stays on the simulator's side. Give both rules as
the reason in a paragraph beside `PL-12P8`'s, and pin the placement through
`Item.lane` with the two recorded shapes, the way
`test_the_owners_own_notes_are_apparatus_like_the_workers` pins
`docs/maintainer.md`: nothing derives a declared entry, so a tidy that drops it
is silent.

**Done when.** An item touching the root `conftest.py` and the apparatus it
configures reads `workflow`, `tests/conftest.py` still reads with the
simulator's tests, and a test in `tests/unit/test_workflow_paths_check.py` fails
if the entry is dropped.

**Generator check.** The fact misread is which half of the project a path
belongs to where `workflow_paths` is silent about it, which every reader takes
for the simulator's side. No head's `misread:` stated it, and this is not a
one-off: `PL-JBZK` and `PL-GVNS` are omissions of the same kind, `PL-12P8` the
check deciding a support module's half wrongly, and `PL-1KTV` and `PL-21RC` two
carriers of the partition disagreeing. Recorded as the head `PL-8ZGY`, with the
store's silent instances measured there: 22 items crossed on
`docs/resident-instructions.md` alone.
