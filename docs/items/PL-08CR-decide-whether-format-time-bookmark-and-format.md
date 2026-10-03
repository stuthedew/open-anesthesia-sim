---
id: PL-08CR
title: Decide whether format_time_bookmark and format_mac_target survive now that bookmark_panel builds every drawn row from the _stated_ helpers
priority: P3
effort: S
status: needs-decision
classes: refactor
touches: src/anesthesia_sim/app/dashboard_frame.py, tests/unit/test_dashboard_frame.py
added: 2026-09-20
payoff: the marks panel has one public entry point, or a recorded reason why it has three
---

**Problem.** Decide whether format_time_bookmark and format_mac_target survive now that bookmark_panel builds every drawn row from the _stated_ helpers

**Decision needed.** Do `format_time_bookmark` and `format_mac_target` stay,
now that no production path calls either?

**Why it matters.** `PL-LHBY` made `bookmark_panel` build every drawn row from
`_stated_time_bookmark` / `_stated_mac_target` plus `_standing_clauses`,
because a row whose displayed runs disagree carries one clause per run and
there is no single standing to hand the old wrappers. Proved by the
adversarial review of that change: replacing each wrapper's body with a
constant fails only tests that call it directly — six unit tests, zero
integration tests, zero panel tests. Nothing in `src/` reaches either.

They are not stranded, though, and that is what makes this a decision rather
than a deletion. Both still delegate to the live `_stated_*` helpers and index
the live `MARK_STANDING_TEXT`, which production does use through the agreement
branch, so the six tests on them — including
`test_a_mark_the_clock_has_gone_past_is_worded_apart_from_one_the_run_halted_on`
(`PL-3K9B`, "passed" against "reached") and
`test_the_two_unreachable_outcomes_are_worded_apart` — are pinning real
wording guarantees through a real code path. Deleting the wrappers means
deciding where those guarantees live instead.

**Recommendation: delete them, and repoint the six tests at `bookmark_panel`
with a single run.** One public entry point for the panel is the shape the
module already has everywhere else, the `_stated_*` helpers now carry the
rationale that used to sit on the wrappers, and a test that goes through
`bookmark_panel` pins the guarantee on the path a reader actually meets
rather than on a sibling of it. The cost is about thirty lines of test churn
and nothing else. The case against is that the wrappers are a convenient
single-row renderer for future callers — but there are none today, and
`CLAUDE.md`'s bar is what a reader of `src/` can maintain without
explanation, which two public functions with no production consumer work
against.

`PL-LHBY` left them in place and corrected their docstrings instead, which
had gone false — they still described drawing a row — so nothing in the tree
is currently misleading. This is the tidy-up that decision deferred.

**Done when.** Either both functions are gone and the six tests assert the
same guarantees through `bookmark_panel`, or they are kept with a recorded
reason naming what calls them.

## Design round 2026-10-03: re-checked against the tree

Nothing in `src/` calls either wrapper. `grep -rn "format_time_bookmark\|format_mac_target" src/` finds the two definitions, `src/anesthesia_sim/app/dashboard_frame.py:1467` and `:1514`, two docstring mentions, and nothing else. `tests/unit/test_dashboard_frame.py` reaches them from **eight** test functions (the brief said six; two have joined since), every one pinning a wording guarantee that `bookmark_panel` draws through the same `_stated_*` helpers and `MARK_STANDING_TEXT`.

**Recommendation: delete both wrappers and repoint the eight tests at `bookmark_panel` with a single run** - the recommendation above, unchanged, with the count corrected. It is the plain call under `CLAUDE.md`'s bar for `src/`: two public functions with no production consumer are what a reader has to be told about, and the guarantees they pin survive on the path a reader actually meets. Cost: about forty lines of test churn in `tests/unit/test_dashboard_frame.py`, no behaviour change, nothing in `docs/MODEL.md`. The alternative, keeping them as a single-row renderer for a future caller, has had no caller since `PL-LHBY` and buys nothing today.

For the build thread: each of the eight tests names one guarantee; keep every test's name and assertion and change only what it calls, so the record of what is pinned does not move with the refactor.
