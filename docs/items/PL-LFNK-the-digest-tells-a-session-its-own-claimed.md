---
id: PL-LFNK
title: The digest tells a session its own claimed capture has 'no copy here to start from' while show says it is in flight on this branch, because Hold.on_base and vcs.stranded answer 'is this item only on a branch' two ways (render.py:512 vs :535)
priority: P3
effort: S
status: done
classes: defect, infra
feature: one-answer
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py, subprojects/docket/README.md, docs/items/PL-PVW2-predicates-the-apparatus-asks-repeatedly-which.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; triaged 2026-09-25 with the one-snapshot batch
added: 2026-09-25
closed: 2026-09-26
pr: 1081
payoff: the session-start digest stops telling a session its own claimed capture has no copy here, so the first thing it reads agrees with show and stranded
verify: grep -q 'def test_digest_counts_this_branch_as_here' subprojects/docket/tests/test_cli.py
---

**Problem.** The digest tells a session its own claimed capture has 'no copy here to start from' while show says it is in flight on this branch, because Hold.on_base and vcs.stranded answer 'is this item only on a branch' two ways (render.py:512 vs :535)

Reproduced in a scratch branch holding its own claimed capture: digest `Filed on a branch, not yet on origin/main: PL-DRRG, PL-ZZZZ - no copy here to start from`; `show PL-ZZZZ` `IN FLIGHT on this branch ... this session's own work`; `stranded` lists only PL-DRRG. Live, the digest named PL-DRRG on two consecutive lines.

**Why it matters.** Two answers to one question at session start.

**Done when.** One predicate for 'only on a branch'; the digest names the session's own branch as here.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` (PL-P0FP).

Reproduced 2026-09-25 against 46954a81 (the cited lines are now render.py:511-515 and :527-535), in a scratch clone whose branch holds its own claimed capture `PL-WF3C`: the digest said `Filed on a branch, not yet on origin/main: PL-WF3C - no copy here to start from`, `show PL-WF3C` said `IN FLIGHT on this branch (claude/scratch-lfnk) - PL-WF3C is this session's own work`, and `stranded --no-fetch` listed nothing.

**Generator check.** PL-PVW2's fact, which spelling of a repeated predicate is the answer, here for "is this item only on a branch": the digest's line spells it as the default branch lacking the file (`on_base`), `stranded` as the file missing from this checkout. Not a freshness misread, so it is removed from PL-XBV4's `root-cause-of` and moved to feature `one-answer`, whose head PL-PVW2 is triaged in another pass.

**Built 2026-09-26, in #1081.** `vcs.only_on_a_branch` is the one spelling: an item is only on a branch where the default branch lacks it and so does this checkout's store, the answer `stranded` already gave through `known_ids`. The digest's filed line, `flight`'s `filed there` and `stranded` all ask it now. The digest names a hold on the checked-out branch `this branch` in its in-flight line, and leaves off its stranded line an id the filed line already named. `Hold.on_base` stays the base's half of the fact, so `claims.py` needed no change and `touches` names the files the fix reached instead.
