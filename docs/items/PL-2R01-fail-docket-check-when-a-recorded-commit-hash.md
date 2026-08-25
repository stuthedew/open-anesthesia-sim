---
id: PL-2R01
title: Fail docket check when a recorded commit hash is unreachable
status: dropped
feature: dev-tooling
touches: subprojects/docket/src/docket/checks.py
added: 2026-08-25
closed: 2026-08-25
reason: duplicate of PL-68XK, which already scopes this check and carries PL-JL24's reachability constraint; PL-68XK has adopted this item's stricter stance - an error where git can answer rather than an advisory
---

**Problem.** Closed items record a `commit:` hash. Nothing verifies the hash
still resolves, so a rebased or dropped branch can leave an item pointing at
nothing — which happened in PL-68XK and PL-JL24.

**Why it matters.** The hash is how a closed item's work is traced. One that
does not resolve is a provenance record that looks complete and is not.

**Where.** `subprojects/docket/src/docket/checks.py` (`_check_references`).

**Notes.** From PL-B043's decision that these findings are invariants rather
than queue items. `_check_references` already holds item cross-references;
this is the same function doing the same job for commit references. Currently
0 of 32 recorded hashes are unreachable, so this is a regression guard keeping
a clean condition clean, not a backlog to work through.

**Done when.** `bin/docket check` errors on a recorded hash git cannot resolve.
