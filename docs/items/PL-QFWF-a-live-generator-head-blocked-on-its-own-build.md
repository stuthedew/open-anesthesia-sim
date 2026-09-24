---
id: PL-QFWF
title: A live generator head blocked on its own build items leaves docket next's generator tier, and nothing ranks the blockers: PL-MB2W's first build item PL-3FYK dropped to an ordinary P2 among 149 the moment the design round blocked the head on it
priority: P2
effort: S
status: done
classes: defect
feature: claim-record
milestone: v0.5.10
touches: subprojects/docket/src/docket/plan.py, subprojects/docket/tests/test_plan.py, subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py, subprojects/docket/README.md
deferred-from: v0.6.0 - filed after the freeze by PL-MB2W's design round (2026-09-24), and not safety or science; generator-machinery defect
added: 2026-09-24
closed: 2026-09-24
pr: 982
payoff: a decomposed generator fix keeps the generator tier's rank instead of sinking into its band
verify: grep -q 'def test_a_blocked_generator_head_ranks_its_open_blockers_in_the_generator_tier' subprojects/docket/tests/test_plan.py
impairs-generators: the ranking behind docket next (plan.py) drops a blocked generator head from the generator tier and ranks its blockers in their own band, so a live generator whose fix was decomposed is ranked by nothing
---

**Problem.** A live generator head blocked on its own build items leaves docket next's generator tier, and nothing ranks the blockers: PL-MB2W's first build item PL-3FYK dropped to an ordinary P2 among 149 the moment the design round blocked the head on it

Observed 2026-09-24 by `PL-MB2W`'s design round. The round filed nine build items under `feature: claim-record` and set the head to `blocked` on the first eight, because `status: ready` may not declare an open blocker. `docket next` filters on `status != "blocked"` before the generator tier is applied, so the head left the tier. Its blockers carry no `generator:` or `root-cause-of:` of their own, so they rank in the P2 band. A decomposed generator fix therefore ranks below where the undecomposed head did, which punishes a design round for doing its job.

**Why it matters.** The tier exists so that a generator is paid down before the sessions it taxes. Here the drop is silent: nothing in `next` or `check` says a live head has gone unranked.

**Done when.**

- The open blockers of a blocked head carrying `generator: live` rank in the generator tier, below `P0`, with a line naming the head they unblock.
- A test pins the case of a head blocked on its own build items.

