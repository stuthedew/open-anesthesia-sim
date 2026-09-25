---
id: PL-2866
title: Decide how apparatus findings are worked while the owner's focus is product: capture all of them as now, but let a product session stop only for one that blocks it, and hold the generator ending for apparatus heads found in product sessions
status: untriaged
feature: workflow-stress-2026-09
touches: CLAUDE.md, .claude/skills/docket/SKILL.md
added: 2026-09-25
---

**Problem.** Decide how apparatus findings are worked while the owner's focus is product: capture all of them as now, but let a product session stop only for one that blocks it, and hold the generator ending for apparatus heads found in product sessions

The generator tier ranks a live apparatus head above a `safety` P1 product item (project owner, 2026-09-21, ratified, over keeping the count for both), and a session that identifies one must fix it or end its reply with a prompt that does. That was decided on the premise that inflow comes from standing causes. The 2026-09-25 stress test (PL-P0FP) measured what the loop actually runs on:

Measured over the store on origin/main, 2026-09-15..25, by the inflow scripts in the evidence archive:

- **Inflow is at its peak, not declining.** 169 apparatus defects filed in the 7 days to 09-24, against 72 in the 7 days to 09-12; the open apparatus backlog has held at 164-176 since 09-16, net zero only because closures rose to match. 20 of 35 recorded generators are drained.
- **Discovery is internal.** Of 226 apparatus defects, 193 (85%) were found while working another apparatus item, 12 (5%) by main going red, 7 (3%) during product work - against 72 simulator items closed in the same window, about 1 apparatus defect per 10 product items.
- **Fixing spawns.** 0.66 new apparatus items per apparatus item closed (0.78 for 09-15..19, 0.59 for 09-20..25).
- **Mechanism classes.** Distributed-state inference 26%, heuristic text recognition 14% plus `verify:`-as-proof 8%, two definitions of one predicate 14%, statement drift 7.5%, output/UX 6.6%, git plumbing 5.8%, other 17%. 41 of 226 had a close second class.
- **Hot files.** README 54 defect items, cli.py 50, vcs.py 45, render.py 37, verify.py 36 (its diff-text integrity checks alone: 19 items in 10 days), doc_check.py 28.

Inflow tracks how much apparatus work is done as much as how many causes stand: the apparatus finds its own defects while being worked, and every one found becomes the next session's work. A ratified decision reopens on ordinary evidence; this is the measurement.

**Decision needed.** Whether to adopt parts 1-3 below, each separately.

**Recommendation:** in three parts, in order.

1. **Before the pivot**, fix the three heads this test recorded - PL-GPJ7 (hard gates recognising by wording), PL-XBV4 (read commands answering from different moments), PL-PVW2 (one predicate, several spellings) - and PL-KR69 (a `git mv` carries a protected core file out of the audit unseen), and land PL-VF3C (the multi-session harness as a regression suite), so the defects that would reach a product session are found by CI rather than by that session.
2. **While the owner declares product focus**, product sessions start from `bin/docket next product`, which exists and already serves the product lane cleanly. Capture is unchanged: raising the capture bar was refuted (PL-LKGL, 67% of what it would suppress was real). An apparatus finding stops a product session only when it **blocks** that session - a hard gate refusing correct work, a state answer that would lose or duplicate work, or a gap in a safety-floor guard. Anything else is captured and the session carries on.
3. **A generator head identified during product focus** is recorded (`root-cause-of:`, `generator:`) but takes neither ending until focus returns to the workflow; `CLAUDE.md`'s generator bullet and the docket skill carry that exception.

**The number that would change it.** Part 2 is wrong if deferred apparatus defects bite product sessions more often than about 1 per 10 product items, which is the rate measured above (7 per 72). Two weeks after the pivot, count items whose brief says they were hit during product work, against simulator items closed.

**Why it matters.** Without part 3, `bin/docket next` without a lane and the generator ending keep returning product sessions to the apparatus; the Joint Commission's alarm-safety alert (Sentinel Event Alert 50, 2013) is the clinical form of the same finding - 85-99% of alarm signals need no intervention, and the ones that do are lost among them.

**Done when.** The owner has answered each part; for each yes, the text lands in `CLAUDE.md` and `.claude/skills/docket/SKILL.md`, recorded as specified or ratified per `CLAUDE.md`.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` on `claude/upbeat-heisenberg-27vafn`.
