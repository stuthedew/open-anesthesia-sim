---
id: PL-T441
title: The git reads behind a printed count resolve the store from config.items_dir rather than the tracked directory, so docket check --items pointed at a store elsewhere silently finds no closures
priority: P2
effort: S
status: ready
classes: defect
feature: count-input-addressing
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py
added: 2026-09-20
payoff: docket check --items pointed at a store elsewhere stops reporting a clean provenance record for a store it never read
verify: grep -q 'def test_counts_resolve_the_store_from_the_tracked_directory' subprojects/docket/tests/test_cli.py
recurrences: 2026-09-22 PL-WF3X
---

**Problem.** `cli._complete_report` hands `closures_on_base` and
`records_on_base` `items_dir=config.items_dir`, and both resolve that path
from the repository root. Where `--items` points at a store the loaded config
does not name - the config being read from beside the store, which is
deliberate - every `git show` misses, so no closure is `landed`, no `pr` is
owed, and the command reports a clean provenance record for a store it never
read. `cli._tracked` already computes the store's real path relative to the
repository root and is what `_flight` and `_stranded` use; the reads behind a
count do not.

Observed 2026-09-20 while working `PL-VKGJ` (the digest under-reporting the
grooming debt): a scratch clone with its queue at `work/items` reported zero
closure advisories from both `check` and `digest`, and the same clone with the
queue at `work/docs/items` reported one. The fixture written for `PL-VKGJ`
carries the constraint in a comment for that reason.

**Why it matters.** Silent-wrong-answer shape: exit zero, a plausible count,
and nothing saying the provenance question went unasked. It only fires for a
caller who typed `--items`, which is the documented way to point at a store.

**Neighbour.** `PL-K5PW` (config resolved from `docs/` rather than the repo
root) and `PL-P757` (`_tracked` deriving the root wrong for a nested store)
are the same surface reached two other ways, and both declare
`subprojects/docket/src/docket/cli.py`. They keep their own `feature:` groups,
which name real completions; whoever starts one should read the other two.

**Done when.** The git reads behind a printed count resolve the store the same
way `_flight` and `_stranded` do — through `cli._tracked`, which computes the
store's real path relative to the repository root — so `docket check --items`
and `docket digest --items` pointed at a store the loaded config does not name
report the same closures a run from beside that store reports. A test pins it by
driving both commands against a clone whose queue is somewhere other than
`docs/items` and asserting the closure count is non-zero.
