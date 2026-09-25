---
id: PL-FX5Q
title: Delete the claim inference and the three promotions from vcs.py, with their tests
priority: P2
effort: M
status: ready
classes: defect
feature: claim-record
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py, subprojects/docket/tests/test_vcs_silence.py
blocked-by: PL-N162
deferred-from: v0.6.0 - filed after the freeze by PL-MB2W's design round (2026-09-24), and not safety or science; generator work, which the pause on new mechanisms exists for
added: 2026-09-24
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

**Progress, 2026-09-25: the code and its tests are deleted; the prose sweep, `make check` and the pull request remain.** The claiming session stopped at the context budget, not for the work. Its commit leads with this id on `claude/pl-fx5q-ph9pnm`.

- *Deleted from `vcs.py`* (6,407 lines to 4,884): every helper the brief names, plus the four things that were left with no caller once those went. `branches_in_flight` and `precedence` had no caller outside tests after `PL-N162`, and each needed the helpers, so both went whole, with `Precedence`, `_closed_on_base`, `_preferred`, `Stake`, `_UNDATED`, `_EARLIEST` and `COMMIT_FORMAT`. `Holdings.flight` and `Holdings.order` are what the spec said the two readers would become.
- *`_queue_only_touches` had a second caller*: `_declares_queue_only`, the closure's `pr` read (`PL-YFXG`). Its reading is folded into that caller unchanged, so no helper by the name remains and `record` answers as before.
- *`_closed_at_ref` becomes the reader's `status_at`*: `claims.holdings` already reads a copy's status through its `status` closure over `_fields_at` (`PL-NST2`), so the vcs copy was deleted and nothing new was written.
- *Tests*: 86 tests and 2 helpers left `test_vcs.py`, with 9 fixtures only they used, and the shared fake `_runner` is trimmed to the eight parameters `orphaned`'s tests still pass. `test_vcs_silence.py` sweeps `claims.holdings` where it swept the two readers, holding every hold, disposition, cut, name, edit and unattributed ref to the silence rule; it passes. A coverage diff over the docket and unit suites, before and after, found no kept `vcs.py` line that lost its only test, except `_item_files`' `continue` for a path outside the queue, which its one remaining caller (`filed_with_work`, whose log is limited to the queue) cannot reach.

**Left to do, in order:**

1. Sweep the prose that describes deleted code as live. It is in `vcs.py`'s kept docstrings (`FlightReport`, `Branch`, `_annotates_only`, `_item_files`, `BranchFiles`, `files_in_flight` and about ten more lines; `git grep` the deleted names), `claims.py` (70, 379, 471, 1034), `cli.py` (210, 396), `render.py` (138, 1919, 2265, 2275), `subprojects/docket/README.md` (424, 468, 556-583 on the promotions, 1650, 2888), `tools/branch_id_check.py:22`, `.claude/hooks/docket-digest.sh:35`, and the test comments in `test_cli.py`, `test_vcs.py:1323`, `tests/unit/test_branch_id_check.py` and `tests/unit/test_docket_digest_hook.py`. Add each file to `touches`. Leave the history alone: release rows in `ROADMAP.md`, the narrative in `docs/WORKING_NOTES.md`, and the "ported from `vcs.precedence`" test docstrings.
2. Run `make check`. `vcs.py` shrank by 1,523 lines, so expect `doc_check`'s line citations from open items into `vcs.py` to fail. Repair each one as a drift fix declared in `touches`.
3. Push, then open the pull request, and let `bin/docket arm` decide arming.
