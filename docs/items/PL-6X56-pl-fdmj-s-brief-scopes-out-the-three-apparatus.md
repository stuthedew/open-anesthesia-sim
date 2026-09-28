---
id: PL-6X56
title: PL-FDMJ's brief scopes out the three apparatus tests workflow_paths listed on 2026-09-05, and the list holds 35 now, so worked as written it holds 32 apparatus tests to the simulator's bar
priority: P2
effort: S
status: ready
classes: housekeeping
feature: apparatus-test-bar
touches: docs/items
added: 2026-09-27
payoff: keeps PL-FDMJ from cutting 32 apparatus tests' prose to the simulator's bar when it is worked
verify: ! grep -qF 'less the three files above' docs/items/PL-FDMJ-*.md
---

**Problem.** PL-FDMJ's brief scopes out the three apparatus tests workflow_paths listed on 2026-09-05, and the list holds 35 now, so worked as written it holds 32 apparatus tests to the simulator's bar

**Evidence, 2026-09-27, at `553522c6`.** `PL-FDMJ` (ready) says "**Three
files are out of scope**" - `test_contrast_check.py`, `test_doc_check.py` and
`test_import_boundary_check.py`, as "named in `docket.toml`'s
`workflow_paths`" - and its **Where** is "`tests/`, less the three files
above". `workflow_paths` has named 35 `tests/unit/` files since
`PL-JBZK`'s fix. A session working `PL-FDMJ` as written would cut 32 apparatus
tests' comments and docstrings to the simulator's bar, which
`.claude/rules/apparatus-standard.md` exists to refuse.

**The repair.** Rewrite the scope as a rule rather than a list: out of scope
is every `tests/` file under `workflow_paths`, with the command that prints
them. A list would drift again the next time `tools/` gains a test.
`.claude/rules/citation-drift.md` would have this repaired in place by
whichever session next commits under `PL-FDMJ`. It is filed because the
session that found it held no item to ride.

**Generator check.** An instance of `PL-G424`'s fact in a live brief, which
`.claude/rules/citation-drift.md` has the next session under `PL-FDMJ` repair in
place; filed because the session that found it held no item to ride.
