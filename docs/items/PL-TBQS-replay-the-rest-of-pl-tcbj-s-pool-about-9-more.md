---
id: PL-TBQS
title: Replay the rest of PL-TCBJ's pool, about 9 more merged simulator pull requests, with one-generalist, three-generalist and specialist-panel arms on every pull request and scored per defect, to choose between a panel and generalist review passes
priority: P3
effort: L
status: ready
classes: planning
feature: review-panel
touches: docs/items/PL-TBQS-replay-the-rest-of-pl-tcbj-s-pool-about-9-more.md, docs/items/PL-TDV9-add-one-more-blind-generalist-review-pass-on.md
added: 2026-10-24
payoff: the choice between a specialist reviewer panel and generalist review passes rests on about 19 pull requests and an equal-cost comparison, not on ten
verify: grep -qE '^\*\*Result' docs/items/PL-TBQS-replay-the-rest-of-pl-tcbj-s-pool-about-9-more.md
---

**Problem.** Replay the rest of PL-TCBJ's pool, about 9 more merged simulator pull requests, with one-generalist, three-generalist and specialist-panel arms on every pull request and scored per defect, to choose between a panel and generalist review passes

**Why it matters.** `PL-TCBJ` (the first replay of a specialist reviewer panel) could not tell the panel from one generalist reviewer. The panel caught the later-filed defect in 4 of 10 merged pull requests and the generalist in 5. Only 3 pull requests were caught by one arm and not the other. The panel also ran three reviews to the generalist's one, so more draws could explain its catches as well as specialism could. The project owner asked for a larger test before choosing, and `PL-TDV9` (one more blind generalist review pass) is held until this one reports.

**Decision** (project owner, 2026-10-24, ratified, over choosing on `PL-TCBJ`'s ten pull requests, over running the rest of the pool with one generalist only, and over planting seeded defects to grow the sample past the pool).

**What this test can show, stated before it runs.** The pool holds about 18 or 19 pull requests, so the sample cannot grow past that without changing what is measured. At that size, an exact paired test detects an arm that wins 3 of every 4 discordant pull requests only about 9% of the time (`PL-TDV9` has the calculation). Scoring each key defect adds resolution, but defects in one pull request are not independent: `#578` and `#775` alone hold 10 of `PL-TCBJ`'s 20. So no p-value is computed on the defect counts. The bar below is a decision rule fixed in advance, not a significance test. That is acceptable here because the choice is cheap to reverse: a review pass can be added, removed or replaced on any later pull request.

**Protocol, fixed on 2026-10-24 before any review in this item runs.**

*The pool.* The pool is `PL-TCBJ`'s 73 candidate pull requests, less `#588`, in the order that `random.Random(20261024)` drew them. Candidates 1 to 39 are already examined and gave the 10 in `PL-TCBJ`'s answer key. Before using any later candidate, re-derive the candidate list with the SZZ procedure that `PL-TCBJ`'s protocol describes, and check that its first 24 match the order recorded there. If they do not match, stop and report rather than walk a different list.

*Verifying the new pairs.* Walk candidates 40 to 73 in that order and verify each pair as `PL-TCBJ` did: a pull request enters only when the defect its item describes lives in lines that pull request added. Every verified pull request enters, with no cap. Write one sentence per verified defect and commit those sentences to this item before any reviewer's output for that pull request is read.

*The arms.* Every pull request in the sample has four arms, all using "The reviewer brief, as run" in `PL-TCBJ`, unchanged, at the session's own model and effort:

1. **G1**, one generalist run. For `PL-TCBJ`'s ten, this is its clean control run, reused as recorded in its Result table. Each new pull request gets a fresh run.
2. **G2** and **G3**, two more generalist runs, each started fresh.
3. **Panel**, the three specialists (PK/PD, numerics and state, clinical display). For `PL-TCBJ`'s ten, this is its panel, reused as recorded. Each new pull request gets a fresh panel.

That is 2 new runs on each of the ten and 6 on each new pull request, about 74 in all. The three-generalist arm (G1, G2 and G3 together) costs the same as the panel. Each run gets its own directory holding only the tree at the merge commit, the diff and the brief, because `PL-TCBJ`'s first control was discarded after a reviewer read another arm's findings.

*Checking.* One blind checker per pull request marks each new finding correct, incorrect or not checkable against the code at merge, as in `PL-TCBJ`. This now includes the generalist findings, which `PL-TCBJ` did not check.

*Scoring.* `PL-TCBJ`'s own findings may still be readable in the transcript of the session that ran it (`session_01JQuNZNYNK5kqZyBxjguXe6`, read with `list_events`), because its reviewers returned their findings as their final replies. If they are, score them again with the new ones, so one scorer scores every arm. If they are not, reuse `PL-TCBJ`'s Result table for its ten. Score each finding against the key with its arm hidden: pool the findings for a pull request under random labels, score them, then unmask the labels. A pull request counts as caught by an arm when any of that arm's findings names its key defect, as `PL-TCBJ` defined it. A key defect counts as named by an arm when at least one run in that arm names it. Near misses are recorded and not counted.

**The bar, fixed before the count.** The decision is made on key defects named across the whole sample:

- Build the panel only if it names at least 3 more key defects than the three-generalist arm.
- Otherwise build generalist passes. Build one pass, as `PL-TDV9` describes. Build a second pass only if G2 and G3 together name at least 3 key defects that G1 missed.

Also report, without letting them change the decision: per-pull-request catches for each arm, the panel against G1 alone, what G2 and G3 each add to G1 on their own, and each arm's share of incorrect findings.

**Cost.** About 74 reviews at 150,000 to 300,000 subagent tokens each, so 11 to 22 million tokens, plus verifying up to 34 candidates and one checker per pull request. It runs as a multi-agent workflow, which needs the owner's explicit go-ahead because it is far larger than the default of fewer than 10 agents.

**Done when.** A `**Result.**` heading here lists every pull request in the sample with each arm's catches, the key defects each arm named, and the bar applied. `PL-TDV9`'s brief then records which build the bar chose, or an item is filed to build the panel and `PL-TDV9` is dropped with the reason.

**Limitations known in advance.** If `PL-TCBJ`'s findings cannot be recovered, its G1 and panel results on its ten were scored by a different session with the arm visible, so their scoring differs from the new runs'. Each run is one draw, and a second run of the same reviewer could find different things. The sample is still limited to defects that SZZ can trace to a diff.

**Generator check.** Work the owner asked for, on 2026-10-24. It touches only its own brief, and no head's fact explains it.

**Stage 1, 2026-10-24: the candidate order reproduces.** The brief's prose did not pin the SZZ procedure down closely enough to re-derive the order. Read literally, it gave 85 candidates, and with every id before the colon counted as a fix it gave 132. So `PL-TCBJ`'s own scripts were recovered verbatim from its session's transcript (`session_01JQuNZNYNK5kqZyBxjguXe6`) and run again here, against `origin/main` at `2f0101bb7` (`#1722`), the head that session read. The recovered procedure differs from the prose in five ways:

- A commit counts as a fix when the item's id appears anywhere before the subject's first colon.
- Only the top 4 blamed commits per item are kept.
- A commit that is not an item's most-blamed one needs at least 2 blamed lines.
- An item classed `test` or `infra` is dropped at the candidate step, and a blamed commit whose subject names the item is not a candidate.
- A pull request of more than 6,000 changed lines, counting every path, is dropped before the shuffle. That is the rule that removed `#588`.

The run gave 73 candidates, dropped `#588`, and shuffled 72. All 72 positions match the order the recovered transcript printed (1 to 44) and the recovered shuffle (45 to 72), and the first 24 match the order recorded in `PL-TCBJ`. The pool therefore ends at position 72, not 73. Positions 40 to 72 are `#308`, `#1428`, `#1448`, `#430`, `#1622`, `#283`, `#561`, `#1592`, `#288`, `#421`, `#488`, `#516`, `#376`, `#399`, `#1361`, `#784`, `#665`, `#568`, `#618`, `#1480`, `#1328`, `#316`, `#671`, `#556`, `#1191`, `#1188`, `#319`, `#306`, `#539`, `#263`, `#805`, `#311` and `#512`. Together they carry 104 pull-request and item pairs to verify.
