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

1. **Before the switch**, only the fixes every product session would meet at once: PL-KX73 (claim refuses the harness's own branch shape), PL-1X56 (an unpushed claim exits 0), PL-ZLJ9 (a late claim displaces a confirmed one) and PL-KR69 (a `git mv` carries a protected core file out of the audit unseen). The three heads this test recorded - PL-GPJ7 (hard gates recognising by wording), PL-XBV4 (read commands answering from different moments), PL-PVW2 (one predicate, several spellings) - are worked through part 2's alternation instead of holding the switch, and PL-VF3C (the multi-session harness as a regression suite) rides with PL-XBV4, whose done-when already names it. *Revised twice on 2026-09-25: the first version left out the claim defects; the second moved the heads into part 2 once the owner proposed working a root cause right after the product item.*
2. **While the owner declares product focus** - one dated line the owner sets in `CLAUDE.md` § "What this project is" and removes when focus returns, resident because a session must know it before its first pick - the pick **alternates**. After a product item, the next item is the top startable root cause: plain `bin/docket next`'s top when it is in the generator tier. If there is none, it is `bin/docket next product`'s top. After a root cause, the next item is `bin/docket next product`'s top. The session that finishes an item knows which it finished, so it writes the next item's ready-to-paste prompt as its handoff. Mid-item, an apparatus finding stops the session only when it **blocks** it: a hard gate refusing correct work, a state answer that would lose or duplicate work, or a gap in a safety-floor guard. Capture is unchanged: raising the capture bar was refuted (PL-LKGL, 67% of what it would suppress was real). This reopens the 2026-09-21 ranking (ratified) in one respect only: a product item alternates with root causes instead of waiting behind all of them. The measurement above is the ordinary evidence a ratified decision reopens on.
3. **A root cause found during a product session** - the owner's proposal, 2026-09-25: finish the current product item, then fix the root cause right after. The session finishes its product item, unless the root cause meets part 2's blocking test. It records the root cause as now (`root-cause-of:`, `generator:`), and its handoff names the root cause as the next item. That is part 2's alternation, applied from the moment the root cause is found. It is the second of the two endings `CLAUDE.md` allows, a ready-to-paste prompt, with the next pick decided rather than left open. The same holds for an `impairs-generators:` defect. That a root cause is "pulled, not queued" (2026-09-17), and that a generator-machinery defect binds the same endings (2026-09-19), are the owner's own decisions and stand unchanged. *Revised 2026-09-25: an earlier version had such a head take neither ending, which would have reopened those two decisions.*

**Why alternate, and why every root cause rather than only the one just found.** Measured over the store, 2026-09-25:
- **Where root causes are found.** Of the 38 recorded generator heads, 37 were recorded under a workflow item and 1 under a mixed one. None was recorded during product work, going by the item each recording commit was filed under.
- **They chain.** 11 of the 38 were recorded while another head was being worked.
- **They do not sit on scheduling.** The 31 closed heads went from recorded to closed in a median of 1 day, never more than 2.
- **They sit on decisions.** Of the 4 older open heads, 3 wait on the owner's decision (PL-B8HZ, PL-HMZZ, PL-QHCW) and 1 on its last open blocker (PL-FX5Q).

What follows from the numbers:
- A rule keyed to "found during this product item" would almost never fire, while the live heads sat through product focus.
- Draining every root cause in a row runs workflow sessions back to back whenever one fix turns up the next. Alternating bounds both waits: a root cause waits at most one product item for each root cause ahead of it, and product work never waits more than one item. A strict product-only lane would be a strict priority queue, which starves whatever sits below it. Bounding the wait is the standard remedy for starvation in scheduling, and Google SRE caps operational work at 50% of an engineer's time for the same reason: left unchecked, it expands to fill all of it.
- No pick rule starts a head that waits on a decision; only the decision does.

**The number that would change it.** The alternation is wrong if startable root causes arrive faster than one per product item: the count of startable live heads should fall over two weeks of product focus, and if it rises, the root-cause share goes up. Part 2's blocking test is wrong if deferred apparatus defects bite product sessions more often than about 1 per 10 product items, which is the rate measured above (7 per 72). Two weeks after the pivot, count items whose brief says they were hit during product work, against simulator items closed.

**Why it matters.** Without part 3, `bin/docket next` without a lane and the generator ending keep returning product sessions to the apparatus; the Joint Commission's alarm-safety alert (Sentinel Event Alert 50, 2013) is the clinical form of the same finding - 85-99% of alarm signals need no intervention, and the ones that do are lost among them.

**Done when.** The owner has answered each part; for each yes, the text lands in `CLAUDE.md` and `.claude/skills/docket/SKILL.md`, recorded as specified or ratified per `CLAUDE.md`. Parts 2 and 3 are workflow rules written while the generator pause holds, so the owner's yes is what lifts it for them (PL-6Q9L), and the session writing them says so.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` on `claude/upbeat-heisenberg-27vafn`.
