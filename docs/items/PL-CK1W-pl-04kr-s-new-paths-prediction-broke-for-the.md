---
id: PL-CK1W
title: PL-04KR's new-paths prediction broke for the week of 2026-10-12 to 10-18: 27 new apparatus paths over 107 filings is 0.25 a filing against the 0.13 ceiling, most from mechanisms added 2026-10-17
priority: P3
effort: S
status: done
classes: housekeeping
feature: defect-review-2026-10
milestone: v0.6.15
touches: docs/items/PL-CK1W-pl-04kr-s-new-paths-prediction-broke-for-the.md
added: 2026-10-19
closed: 2026-11-03
pr: 1975
payoff: the owner learns whether the burst of new apparatus on 2026-10-17 is producing defects, so the broken inflow prediction carries an explanation rather than standing unread
verify: grep -qE '^\*\*Verdict\.' docs/items/PL-CK1W-*.md
---

**Problem.** PL-04KR's new-paths prediction broke for the week of 2026-10-12 to 10-18: 27 new apparatus paths over 107 filings is 0.25 a filing against the 0.13 ceiling, most from mechanisms added 2026-10-17

**How it was measured.** A defect review on 2026-10-19 read `docs/items` with `docket.store.read_items` and placed each item with `Item.lane(workflow_paths)`. A defect is an item whose `classes` include `defect` or `safety`. An organic defect is one filed before any head's `root-cause-of:` named it and carrying no `reenters:`. The scripts lived in the session's scratchpad and are gone, so this paragraph is the method.

**Why it matters.** `PL-04KR` pre-registered four predictions about apparatus inflow. A broken one is its stated trigger to investigate. Both release checks so far (v0.5.24 and v0.5.25) read the week of 2026-10-05 to 10-11, so nothing has read this week yet. `bin/docket inflow` and `docket.inflow.missed` on 2026-10-19 return: "27 new apparatus paths over 107 filings, 0.25 a filing, above the 0.13 ceiling".

**What the new paths are.** Most were added on 2026-10-17 as owner-requested mechanisms: `tools/diff_mutation.py`, `docs/mutation-testing.md`, `docs/session-ledger.tsv`, `docs/ci-runs.tsv`, `.claude/skills/model-review`, `.claude/rules/plain-writing.md`, `.claude/rules/test-oracles.md` and `.claude/hooks/pr-body-email-guard.sh`. Eight more came from the `PL-4S6C` (fact-home check) work on 2026-10-12. Through 2026-09-20, each workflow pull request produced about one organic defect while new surface was being built.

**Done when.** The investigation is recorded here: whether defects arrive in those new areas over 2026-10-19 to 11-01, and whether the growth was intended. Then this item closes with that verdict.

**Not before 2026-11-01.** The window this reads ends that day, so a session that starts it earlier has nothing to measure.

**Checked 2026-10-20:** `bin/docket inflow` still reports the week of 2026-10-12 to 10-18 above the ceiling, now as 28 new paths at 0.26 a filing over 87 filings. Record the result under a `**Verdict.**` heading here.

**Generator check.** One-off. This item is `PL-04KR`'s own stated trigger to investigate, not a reader misreading a fact.

**Verdict.** Measured 2026-11-03 over the store on `main` at `4620917c`, with `docket.store.read_items`, `docket.inflow.apparatus_paths` and `Item.lane`, as above. The paths new that week did not draw defects faster than the rest of the recent apparatus, and the growth was built on purpose. Nothing in that week's paths points at a generator, so this item closes.

1. **The week now counts 30 new apparatus paths over 107 filings, 0.28 a filing.** That is three paths more than on 2026-10-19. Thirteen were first named on 2026-10-12: eight by the one-source-of-truth fixes (such as `tools/fact_home_check.py`, `docket/gitargv.py` and `docket/grep.py`), four by reference corpora and tests for the YAML, shell and workflow parsers, and one by the design mode's rule for a build that meets a decision. Seventeen were first named on 2026-10-17 and 10-18 by new mechanisms: mutation testing, the session ledger and CI-run record, the model review, the model-evidence table, the plain-writing and test-oracle rules, the pull-request email guard, the new-prose review, the explorer agent definition and the shortcut that skips the full checks job for an item-only pull request. `PL-04KR` § "Result" records that the owner asked for several of these.
2. **Six of the 30 paths (20%) were named by an organic defect filed from 2026-10-19 to 11-01**, seven defects in all. Of the 170 apparatus paths first named in the six weeks before (2026-09-01 to 10-11), 37 (22%) were named by an organic defect in the same window. A path counts only when a defect's `touches` names it or a file under it, because a defect naming a parent directory would otherwise count against every path below it.
3. **The seven defects are all closed.** `PL-LGDV` and `PL-MM3Q` are in `tools/fact_home_check.py` (its baseline, and matching a copy by name only). `PL-D59R` and `PL-LBNN` are in `tools/diff_mutation.py` (large test files, and weakened apparatus tests; `PL-LBNN` was dropped). `PL-3XP7` and `PL-J7YG` are in the model-review skill (its description, and its rework measure). `PL-Q508` is in the new-prose counter.
4. **The next week, 2026-10-19 to 10-25, broke the ceiling the same way**, with 34 new paths over 117 filings (0.29). Again most are files that new mechanisms set out to create: the effort trial, the owner-ask guard, the worker-run record, the hook-block count, the quote check, the blind review and the skill-start evaluation. One of them has since become a generator. `.claude/hooks/owner_ask_guard.py`, first named on 2026-10-19, refused four messages that asked for nothing on 2026-11-02 and 11-03, and `PL-ZCF9` records that as a live generator.
5. **The week after that, 2026-10-26 to 11-01, breaks it for a different reason.** It named 11 new paths over 19 filings (0.58). The new paths fell from 34 to 11, but the filings fell faster, from 117 to 19. So the ratio rose because apparatus inflow is falling, which is what `PL-04KR` expects as the apparatus converges. That is a fault in how the ceiling is stated, not a sign of growth, and it is filed as `PL-2T7X`.
