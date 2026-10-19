---
id: PL-CK1W
title: PL-04KR's new-paths prediction broke for the week of 2026-10-12 to 10-18: 27 new apparatus paths over 107 filings is 0.25 a filing against the 0.13 ceiling, most from mechanisms added 2026-10-17
status: untriaged
feature: defect-review-2026-10
added: 2026-10-19
---

**Problem.** PL-04KR's new-paths prediction broke for the week of 2026-10-12 to 10-18: 27 new apparatus paths over 107 filings is 0.25 a filing against the 0.13 ceiling, most from mechanisms added 2026-10-17

**How it was measured.** A defect review on 2026-10-19 read `docs/items` with `docket.store.read_items` and placed each item with `Item.lane(workflow_paths)`. A defect is an item whose `classes` include `defect` or `safety`. An organic defect is one filed before any head's `root-cause-of:` named it and carrying no `reenters:`. The scripts lived in the session's scratchpad and are gone, so this paragraph is the method.

**Why it matters.** `PL-04KR` pre-registered four predictions about apparatus inflow. A broken one is its stated trigger to investigate. Both release checks so far (v0.5.24 and v0.5.25) read the week of 2026-10-05 to 10-11, so nothing has read this week yet. `bin/docket inflow` and `docket.inflow.missed` on 2026-10-19 return: "27 new apparatus paths over 107 filings, 0.25 a filing, above the 0.13 ceiling".

**What the new paths are.** Most were added on 2026-10-17 as owner-requested mechanisms: `tools/diff_mutation.py`, `docs/mutation-testing.md`, `docs/session-ledger.tsv`, `docs/ci-runs.tsv`, `.claude/skills/model-review`, `.claude/rules/plain-writing.md`, `.claude/rules/test-oracles.md` and `.claude/hooks/pr-body-email-guard.sh`. Eight more came from the `PL-4S6C` (fact-home check) work on 2026-10-12. Through 2026-09-20, each workflow pull request produced about one organic defect while new surface was being built.

**Done when.** The investigation is recorded here: whether defects arrive in those new areas over 2026-10-19 to 11-01, and whether the growth was intended. Then this item closes with that verdict.
