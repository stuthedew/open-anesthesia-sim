---
id: PL-KGPR
title: Decide which of the 13 checks on the workflow's own records to retire, from PL-LY24's count
priority: P2
effort: S
status: done
classes: planning
feature: standing-weight
touches: docs/items/PL-KGPR-decide-which-of-the-13-checks-on-the-workflow-s.md, docs/items/PL-HS2T-retire-tools-branch-id-check-py-from-make-check.md, docs/items/PL-F7XT-retire-tools-pr-body-check-py-anchors-from-make.md, docs/items/PL-8F5B-retire-the-check-half-of-tools-dead-ends-py.md, docs/items/PL-3HNP-retire-tools-worker-runs-py-and-docs-worker.md
deferred-from: v0.7.0 - the checks guard the workflow's records, not the schematic, so the release does not wait on this answer
added: 2026-11-21
closed: 2026-11-21
pr: 2179
not-delegable: The work is recording the owner's answer and filing the removals; no command can prove it.
---

**Problem.** Decide which of the 13 checks on the workflow's own records to retire, from PL-LY24's count

**Why it matters.** `PL-LY24` counted, for each of the 13 checks that guard the workflow's own records, how many CI refusals caught a real mistake, and recommends keeping some and retiring others. `CLAUDE.md` § "Prefer deterministic tooling over repeated model work" retires a check that changes no decision. The retirements need the project owner's answer, because each removes a guard.

**Decision needed.** Which checks should be retired? `PL-LY24`'s brief has the count and a recommendation for each.

**Recommendation:**

1. Retire `tools/branch_id_check.py`. It caught no mistake in 12 refusals and has cost 21 items.
2. Retire `tools/pr_body_check.py --anchors`, which has never refused, and keep `docs/pr-bodies/` as a closed archive.
3. Retire the `check` half of `tools/dead_ends.py`, which has never refused.
4. Retire `tools/worker_runs.py` and `docs/worker-runs/` unless `PL-6FX6` (the first month of API-credit worker runs) goes ahead.
5. Decide the replay of `verify:` commands together with `PL-LFJZ`.
6. Keep the other eight.

**Answered 2026-11-21.** The owner agreed with all six recommendations (project owner, 2026-11-21, ratified, "Agree with recs", over keeping all 13 checks). Asked whether the dead-ends list goes too, the answer given was no: only its format check is retired, and the list still reaches each session through the start-up hook. The removals are `PL-HS2T` (the branch-id check), `PL-F7XT` (the body anchor check), `PL-8F5B` (the dead-ends format check) and `PL-3HNP` (the worker-run check). The replay of `verify:` commands is decided in `PL-LFJZ`.

**Done when.** The owner has answered, and each check to retire has an item to remove it.

**Generator check.** One-off. It is the owner's decision on `PL-LY24`'s count, and no fact was misread to cause it.
