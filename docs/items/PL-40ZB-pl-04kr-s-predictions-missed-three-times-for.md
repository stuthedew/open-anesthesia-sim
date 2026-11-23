---
id: PL-40ZB
title: PL-04KR's predictions missed three times for 2026-11-02..11-08, as v0.6.17's cut reported: 40 new apparatus paths over 111 filings (0.36 a filing against the 0.13 ceiling, 11 the week before), 12 P1 workflow-lane apparatus filings whose band no rank or owner set, and 14 re-entries against 4; find what generated each
priority: P2
effort: M
status: done
classes: infra
feature: convergence-visibility
touches: docs/items, .claude/skills/docket/modes/capture.md
added: 2026-11-11
closed: 2026-11-23
pr: 2301
payoff: the work that keeps apparatus inflow from falling is found and named, so it can be stopped
verify: grep -qF '**What generated each miss.**' docs/items/PL-40ZB-pl-04kr-s-predictions-missed-three-times-for.md
not-delegable: naming a generator is judgment, and the command proves only that the verdicts were written
sweep: what generated each of the three PL-04KR misses in the week of 2026-11-02
---

**Problem.** PL-04KR's predictions missed three times for 2026-11-02..11-08, as v0.6.17's cut reported: 40 new apparatus paths over 111 filings (0.36 a filing against the 0.13 ceiling, 11 the week before), 12 P1 workflow-lane apparatus filings whose band no rank or owner set, and 14 re-entries against 4; find what generated each

**Why it matters.** `PL-04KR` pre-registered the owner's expectation that apparatus inflow falls now that the workflow is built. `CLAUDE.md` § "What this project is" says that a miss means something is generating work, and that it should be found. Three predictions missed in one week, after one miss the week before. Each miss left unexplained may be a generator that goes on filing items.

**Done when.** This brief names, for each of the three misses, what generated it: a new head recorded with `root-cause-of:`, `generator:` and `misread:`; an existing head whose fix did not hold, recorded on the members with `--reenters`; or the reason it is not a generator. The verdicts sit under a heading "**What generated each miss.**"

**Generator check.** This item is the search for generators, so it is not itself a member of one.

**Checked 2026-11-22** against `d4e8200`: still applies. The brief has no "**What generated each miss.**" heading, and no other item names a generator for the three misses of the week of 2026-11-02. `bin/docket release` still prints a broken `PL-04KR` prediction at each cut (`subprojects/docket/src/docket/cli.py`), so later weeks may have added misses of their own.

**What generated each miss.** Read 2026-11-23. The cut's counts were replayed from the tag `v0.6.17` with its own copy of `docket`, and each filing was traced to the commit that added it. The week has no unfound generator. Two causes explain most of all three misses: the copy editor, a new tool built that week at the owner's request, and a review of every guard hook that filed twenty findings with no item of its own to record it as a sweep.

1. **Twelve `P1` filings, nine on `main` today.** Ten are defects in the copy editor and its prose review, found while that tool was built and measured: `PL-22T5`, `PL-43GT`, `PL-556C`, `PL-DH17`, `PL-F0Q2`, `PL-HJFX`, `PL-HNNH`, `PL-JP8X`, `PL-TG6P` and `PL-TTBF`. `PL-P6KV` records that the owner asked for that work on 2026-11-02. Two heads recorded the cause before the cut: `PL-HGZS` (the copy editor passed over-explained text) and `PL-J1ZM` (sessions write prose that over-explains). The owner stopped `PL-J1ZM` on 2026-11-14, and #2149 removed the copy editor on 2026-11-13, so the mechanism that filed these ten no longer exists. The other two, `PL-3D2F` and `PL-R1HT`, came from the guard hook review (#1980). Each was a guard letting an ask past the state that says to send the owner nothing, a gap in a safety-floor guard, and #1984 fixed both by keying the guard on the state `bin/docket arm` records. Three of the twelve no longer count, because #2149 deleted `tests/unit/test_rejected_prose.py`, so the workflow path list no longer names it, and `PL-22T5`, `PL-556C` and `PL-F0Q2`, which name it, now read as crossing the lanes.
2. **40 new apparatus paths over 111 filings, 36 over 113 today.** 30 of the 36 come from three sources. The guard hook review and its triage (#1980, #1987) named 13. The copy editor and the prose review named 13 across six commits (#1999, #2000, #2032, #2049 and #1956). The regular-expression check that `PL-7JYV` built (#1983) named 4. Each is a new mechanism or a deliberate review, not defects arriving in new places. The next two weeks named 10 and 9.
3. **14 re-entries against 4.** Seven re-enter the owner-ask guard's reading of wording: `PL-0W6J`, `PL-Q0TK` and `PL-ZCF9` re-enter `PL-GPJ7`, `PL-VHMS` and `PL-YN60` re-enter `PL-TLPH`, `PL-3D2F` re-enters `PL-ZCF9`, and `PL-JTTD` re-enters `PL-X4MD`. Each is recorded with `reenters:`, and `PL-X4MD` closed the line on 2026-11-04 by keying the guard on recorded state. No filing has re-entered `PL-TLPH`, `PL-ZCF9` or `PL-X4MD` since `PL-JTTD`. Three re-enter `PL-61FT`, the Bash guards' reading of a command's spelling: `PL-1ZZ0`, `PL-9PPJ` and `PL-SMM1`. `PL-1ZZ0` became that line's head on 2026-11-03, `PL-95BJ` and `PL-39Y1` re-entered it on 2026-11-10 and 11-11, and the merge-hold check that `PL-39Y1` added, made required on `main` by #2123, moved that refusal to GitHub. Nothing has re-entered the line since. The other four are single lines: `PL-JP35`, `PL-LPV0`, `PL-NHQ6` and `PL-WP3Z`. Re-entries fell to 9 and then 2 in the next two weeks.

**A gap this reading found.** The guard hook review filed 20 items in one commit that leads with the findings' own ids, so no item records the review and `bin/docket inflow` counts its filings as ordinary inflow: 13 filings, 2 of the `P1` filings, 3 re-entries and 13 new paths in this week. Other reviews were run the same way: the 2026-11-10 root-cause audit (#2090), the test-suite review (#2128) and the review of the 2026-11-14 merges (#2160). The triage rule for `sweep:` reaches only a review that has an item, so this branch adds a capture step that gives every review one before its findings are filed.
