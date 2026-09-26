---
id: PL-FX5Q
title: Delete the claim inference and the three promotions from vcs.py, with their tests
priority: P2
effort: M
status: done
classes: defect
feature: claim-record
milestone: v0.5.12
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py, subprojects/docket/tests/test_vcs_silence.py, subprojects/docket/src/docket/claims.py, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/checks.py, subprojects/docket/README.md, subprojects/docket/tests/test_cli.py, tools/branch_id_check.py, .claude/hooks/docket-digest.sh, tests/unit/test_branch_id_check.py, tests/unit/test_docket_digest_hook.py, docs/items/PL-MB2W-who-holds-an-item-is-derived-by-every-reader.md, docs/items/PL-SVRW-roadmap-py-spells-the-leading-id-grammar-a.md, docs/items/PL-HMZZ-which-pull-request-carried-a-closed-item-s-work.md
blocked-by: PL-N162
deferred-from: v0.6.0 - filed after the freeze by PL-MB2W's design round (2026-09-24), and not safety or science; generator work, which the pause on new mechanisms exists for
added: 2026-09-24
closed: 2026-09-25
pr: 1016
payoff: part of the claim record that ends PL-MB2W's generator: one recorded fact decides who holds an item
verify: ! grep -qE '^(def (credit_claims|_queue_only_touches|_queue_only_work|_deciding_on_base|_modified_by|_own_edit_claims|_claimed_again_since|_taken_on_base|_head_carries)\b|class Carrier\b)' subprojects/docket/src/docket/vcs.py
---

**Problem.** Delete the claim inference and the three promotions from vcs.py, with their tests

**Part of `PL-MB2W`'s design** (who holds an item is recorded as a claim; design round of 2026-09-24, in `PL-MB2W` under "Design round, 2026-09-24"). Read that section's spec before starting: this brief names only this item's slice of it.

Delete the claim use of `_annotates_only`; `_Walk`'s claim fields and `credit_claims`; `_queue_only_touches` and `_queue_only_work`; `_deciding_on_base`, `_modified_by` and `_own_edit_claims`; `_claimed_again_since` and `_taken_on_base`; `Carrier`, `_head_carries` and precedence's re-walk; and the tests that pin them. `_closed_at_ref` becomes the reader's `status_at`. Kept: the landing machinery, `leading_ids`, `editing`, `unattributed`, and the unread/unbounded guards.

**Why it matters.** `PL-MB2W` is a live generator: twenty items were each a new shape of work that some reader misread, because who holds an item is inferred from commit subjects, touched paths and ref age. This item is one slice of replacing that inference with a recorded claim, and the generator stops producing members only once the slices through `PL-DDYD` land.

**Done when.**

- None of the named helpers remain in `vcs.py`, and no test pins them; `make check` passes.

**Build order.** After `PL-N162`.

**Progress, 2026-09-25: the code and its tests are deleted.** The claiming session stopped once at the context budget, for length rather than for the work, and finished after a compaction. Its commits lead with this id on `claude/pl-fx5q-ph9pnm`.

- *Deleted from `vcs.py`* (6,407 lines to 4,884): every helper the brief names, plus the four things that were left with no caller once those went. `branches_in_flight` and `precedence` had no caller outside tests after `PL-N162`, and each needed the helpers, so both went whole, with `Precedence`, `_closed_on_base`, `_preferred`, `Stake`, `_UNDATED`, `_EARLIEST` and `COMMIT_FORMAT`. `Holdings.flight` and `Holdings.order` are what the spec said the two readers would become.
- *`_queue_only_touches` had a second caller*: `_declares_queue_only`, the closure's `pr` read (`PL-YFXG`). Its reading is folded into that caller unchanged, so no helper by the name remains and `record` answers as before.
- *`_closed_at_ref` becomes the reader's `status_at`*: `claims.holdings` already reads a copy's status through its `status` closure over `_fields_at` (`PL-NST2`), so the vcs copy was deleted and nothing new was written.
- *Tests*: 86 tests and 2 helpers left `test_vcs.py`, with 9 fixtures only they used, and the shared fake `_runner` is trimmed to the eight parameters `orphaned`'s tests still pass. `test_vcs_silence.py` sweeps `claims.holdings` where it swept the two readers, holding every hold, disposition, cut, name, edit and unattributed ref to the silence rule; it passes. A coverage diff over the docket and unit suites, before and after, found no kept `vcs.py` line that lost its only test, except `_item_files`' `continue` for a path outside the queue, which its one remaining caller (`filed_with_work`, whose log is limited to the queue) cannot reach.

**The prose sweep, 2026-09-25.** Every sentence that described a deleted helper as live now says what reads the fact instead, or says in the past tense that the helper did. The rule applied: a present-tense description of deleted code is wrong and was rewritten; a past-tense account of what it once did is history and was left, as were the release notes, the pull request bodies, `ROADMAP.md`, `docs/WORKING_NOTES.md` and the "ported from `vcs.precedence`" test docstrings.

- *Two arguments had to move rather than go.* `_unmerged_commits` held the case for why a walk must stop at the base and never at the end of a truncated history, and the limit `PL-W1LN` accepted. Both are in `claims._history` now, the walk that inherited the guard. `Carrier.mine` held the reason a checkout's own work is found by `HEAD` containment rather than by name; `BranchCut` and the README state it in place.
- *`_item_files` went too.* Its docstring argued only for the deleted walk's file-edit mark, which `claims._touched` and `claims._editing` read for themselves, and its one caller, `filed_with_work`, discarded the path it returned. The caller reads `ITEM_FILE_RE` directly, as six other readers in `vcs.py` do, with the same prefix test, so no answer changes.
- *The README's three promotion paragraphs* are one paragraph in the past tense, naming `PL-7790`, `PL-VYSP` and `PL-8FJK` for the measurements. The rest of that section still describes the inference as the reading; `PL-MB2W`'s close-out writes its claims section.
