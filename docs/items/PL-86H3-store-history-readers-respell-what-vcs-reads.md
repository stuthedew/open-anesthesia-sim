---
id: PL-86H3
title: Store-history readers respell what vcs reads - item files at a ref (pr_title_check, verify, three in vcs), the commit that added an item (generator_check), the items an item cites (generator_check, item_reads), a queue-only commit (vcs, claims) and a change's closures (pr_record_check) - each parting on one input
priority: P3
effort: M
status: done
classes: defect
feature: one-answer
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/verify.py, subprojects/docket/src/docket/claims.py, subprojects/docket/src/docket/claiming.py, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/store.py, tools/pr_title_check.py, tools/generator_check.py, tools/item_reads.py, tools/pr_record_check.py, tools/branch_id_check.py, tools/branch_sweep.py, tools/pr_body_check.py, tools/doc_check.py, tools/fact_home_check.py, subprojects/docket/tests/test_vcs.py, subprojects/docket/tests/test_claims.py, tests/unit/test_generator_check.py, tests/unit/test_pr_title_check.py, tests/unit/test_pr_record_check.py, tests/unit/test_branch_id_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; filed and classed by PL-5DZ8's closing sweep, 2026-10-12
added: 2026-10-12
closed: 2026-10-18
pr: 1534
payoff: what the store held, and when, reads the same to docket and the tools that audit it
verify: grep -q 'def test_a_shallow_clone_credits_no_commit_with_filing' tests/unit/test_generator_check.py
---

**Problem.** Store-history readers respell what vcs reads - item files at a ref (pr_title_check, verify, three in vcs), the commit that added an item (generator_check), the items an item cites (generator_check, item_reads), a queue-only commit (vcs, claims) and a change's closures (pr_record_check) - each parting on one input

- Item files at a ref: `pr_title_check.closed_items_at` beside `vcs._item_blobs` and `_items_at`, `vcs._item_paths_on` and `verify._store_at`. A file `PL-AAAA-x.md` declaring `id: PL-BBBB` is keyed `PL-BBBB` by pr_title_check and `PL-AAAA` by `_items_at`; a nested `docs/items/sub/` file is missed by `_item_paths_on` alone.
- The commit that added an item: `generator_check.creation_parents` beside `vcs.filed_with_work`. In a shallow clone vcs declines and generator_check credits the boundary commit with filing every older item.
- The items an item cites: `generator_check.citations` reads the whole file and `item_reads.citations` the body only; an id named only in `root-cause-of:` parts them.
- A queue-only commit: `vcs._annotates_only` beside `claims.in_queue` and `work_outside_queue`. A `ROADMAP.md`-only commit counts as merge evidence in vcs and as queue-only in claims. `PL-0JGZ` named this the third spelling and left it to `PL-GJPD`, which was dropped.
- A change's closures: `vcs.closed_by` and `_done_before` beside `pr_record_check.closures`; an item dropped at the base and done at the head is closed here to vcs and not to the check.
- A `--raw -z` record: `vcs._raw_writes` beside `claims._history`'s inline parse; they agree.

**Why it matters.** Each copy is held to the others by nothing, so the first input they part on is answered one way by docket and another by the hook or check a session trusts at that moment; every pair below was read at both sites by the sweep, and the parting input is the sweep's reading, to re-confirm at start.

**Done when.** Each reader asks `docket.vcs` (or one new export), and a test pins each parting input.

**Generator check.** A member of `PL-5DZ8`, filed by that head's closing sweep on 2026-10-12 and named in its `root-cause-of:`. The fact is the head's: which spelling of a repeated predicate is the answer, when tools, hooks and docket each spell it. It is neither a post-close instance nor a new generator.

**Built 2026-10-18 (`#1534`).** Each fact now has one reader, and a test pins the input the two copies parted on.

- Item files at a ref: `vcs._item_blobs` is the one listing, and `_items_at` is its path half. `_item_paths_on` is gone, and `claims`, `claiming`, `verify._store_at`, `tools/pr_title_check.py` and `tools/branch_id_check.py` read `_items_at`. A file counts only where it sits directly in the store, because `store.read_items` reads no subdirectory. The recursive listing had counted `docs/items/sub/` files.
- The commit that added an item: `vcs.item_additions`, read by `filed_with_work` and `generator_check.creation_parents`. It declines in a shallow clone, so the check no longer credits the boundary commit with every older filing.
- The items an item cites: `docket.store.cited_ids`, which reads the whole file. Both tools read it, so an id named only in `root-cause-of:` counts for both.
- A queue-only commit: `RECORDS`, `queue_records` and `in_queue` moved from `claims` to `vcs`, and `vcs._annotates_only` asks `in_queue`. A `ROADMAP.md`-only commit is no longer merge evidence to `landed_whole` or `orphaned`. `orphaned` and `landed_whole` take a `Config` in place of `items_dir`. `branch_state` passes none, so its reading uses the default `Config`, which names no notes file.
- A change's closures: `vcs.landed_closure` is the test of whether a tree already holds a closure. `closed_by`, `closures_on_base` and `tools/pr_record_check.py` read it, so an item the base holds `dropped` and the branch marks `done` owes a number to the check as it does to `bin/docket record`.

Decided in the build (the session's call, recorded here). `pr_title_check.closed_items_at` keys each item by the id its front matter declares, not by the id its filename leads with, because a title and a `pr:` record name the declared id. A file whose name leads with another id is what `docket check`'s slug advisory reports. `arming.py`'s docstring still names `claims.in_queue`, which still resolves because `claims` imports it. Editing `arming.py` would hold this pull request for the owner's read, so that rename is left.
