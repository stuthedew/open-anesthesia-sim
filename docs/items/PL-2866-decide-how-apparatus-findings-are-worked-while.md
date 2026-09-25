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

**Recommendation:** fourth pass, 2026-09-25. It follows two things the owner said in this sitting: that root causes have been prioritized by hand, not by the queue; and that the Projects trial (PL-NZC0) is the context. The trial is the automatic mechanism this item was reaching for: a coordinator starts root-cause threads itself, in two serial streams, and the owner answers design questions and presses Merge it. So this plan uses the trial rather than building a competing scheduler.

1. **No separate batch before the switch.** Its four fixes ride the trial's Stream B, which works the same files:
   - PL-KR69 (a `git mv` carries a protected core file past `verify --self`'s check) goes after PL-J16N. Both are git's rename detection read as a changed-file list.
   - PL-KX73, PL-1X56 and PL-ZLJ9 go before the PL-MB2W close-out. They are defects in the claim record PL-MB2W built, and a separate session would collide with Stream B in `claims.py`, `claiming.py` and `vcs.py`.
   - The owner can switch to product focus at once.
2. **During product focus**, declared by one dated line in `CLAUDE.md` § "What this project is":
   - Product sessions pick from `bin/docket next product`.
   - An apparatus finding stops a product session only when it **blocks** it: a hard gate refusing correct work, a state answer that would lose or duplicate work, or a gap in a safety-floor guard.
   - Capture is unchanged (PL-LKGL).
   - **Root causes are worked by the Projects coordinator in parallel**, not interleaved into the owner's sessions. A pick rule that ends in a pasted prompt leaves the owner as the scheduler, which is what they asked to stop being.
   - If the trial fails its own bar (PL-NZC0: more than 1.5 owner touches per closed item, or more than 1.0 captures per item worked), the fallback is to build the pick into `bin/docket next`. After a product item, `next` offers the top startable root cause; after a root cause, a product item. The digest's top line is then the pick and nobody chooses.
3. **A root cause found during a product session:** the session finishes its product item unless the root cause blocks it, records the root cause, and ends with the ready-to-paste prompt. That is the second of the two endings `CLAUDE.md` allows; "pulled, not queued" (2026-09-17) stands. During the trial, the root cause waits for the coordinator's list: the trial's instructions keep new heads out of scope, so it waits until the owner adds it to the Goal line or the trial ends. At the end, the owner decides whether the protocol becomes a docket skill mode.

The three heads this test recorded (PL-GPJ7, PL-XBV4, PL-PVW2) are outside the trial's scope. They are the natural second batch if the trial passes.

**What the numbers do and do not show.** Measured over the store, 2026-09-25:
- 37 of the 38 recorded generator heads were recorded under a workflow item and 1 under a mixed one; none during product work.
- 11 were recorded while another head was being worked.
- The 31 closed heads went from recorded to closed in a median of 1 day, never more than 2. **That measures the owner's hand-prioritizing, not the queue** (owner, 2026-09-25). An earlier pass read it as "root causes do not wait on scheduling", which is withdrawn.
- Of the 4 older open heads, 3 wait on the owner's decision (PL-B8HZ, PL-HMZZ, PL-QHCW); the trial's design threads put those decisions. 1 waits on its last open blocker (PL-FX5Q, Stream B's first item).

**The number that would change it.** For the scheduling choice, the trial's own bar in PL-NZC0. For part 2's blocking test: it is wrong if deferred apparatus defects bite product sessions more often than about 1 per 10 product items, the rate measured above (7 per 72). Two weeks after the switch, count items captured under product items against simulator items closed.

**Why it matters.** Without part 3, `bin/docket next` without a lane and the generator ending keep returning product sessions to the apparatus; the Joint Commission's alarm-safety alert (Sentinel Event Alert 50, 2013) is the clinical form of the same finding - 85-99% of alarm signals need no intervention, and the ones that do are lost among them.

**Done when.** The owner has answered each part; for each yes, the text lands in `CLAUDE.md` and `.claude/skills/docket/SKILL.md`, recorded as specified or ratified per `CLAUDE.md`. Parts 2 and 3 are workflow rules written while the generator pause holds, so the owner's yes is what lifts it for them (PL-6Q9L), and the session writing them says so.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz`.

**Decision** (project owner, 2026-09-25, ratified, over a separate fix batch before the switch, working each root cause in the owner's own session right after the product item, and holding the generator ending for heads found during product work): yes to all three parts of the fourth-pass recommendation above. Parts 2 and 3 are workflow rules written while the generator pause holds, and this yes lifts it for them (`PL-6Q9L`). Still to do: the text in `CLAUDE.md` and `.claude/skills/docket/SKILL.md`, each recorded as ratified. The title still describes the first pass's part 3, which held the generator ending; retitle it at close-out.
