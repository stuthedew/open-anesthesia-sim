---
id: PL-TCBJ
title: Replay a panel of specialist reviewer subagents (PK/PD, numerical solver, clinical display) on about ten merged simulator pull requests that later had a defect filed, and adopt it only if it would have caught at least three
priority: P3
effort: M
status: ready
classes: planning
feature: review-panel
touches: docs/items/PL-TCBJ-replay-a-panel-of-specialist-reviewer-subagents.md
added: 2026-10-24
payoff: whether a specialist reviewer panel would have caught real simulator defects is measured before anyone builds one
verify: grep -qE '^\*\*Result' docs/items/PL-TCBJ-*.md
---

**Problem.** Replay a panel of specialist reviewer subagents (PK/PD, numerical solver, clinical display) on about ten merged simulator pull requests that later had a defect filed, and adopt it only if it would have caught at least three

**Why it matters.** `.claude/rules/expert-review.md` names twelve fields that a review of simulator code should cover, from PK/PD modelling and numerical methods to human factors and data visualisation. It asks one session to hold all of them at once. testdouble/han's `/code-review` instead always runs two reviewers, a junior developer and a security analyst. It then adds specialists chosen by the files a change touches (`han-coding/skills/code-review/SKILL.md` in https://github.com/testdouble/han, read 2026-10-24). No evidence was found that a panel like this beats one careful reviewer, so it is tested on past work before anything is built.

**Decision** (project owner, 2026-10-24, ratified, over building the panel without a replay and over not trying it).

**Method.** Pick about ten merged simulator pull requests that later had a `defect` or `safety` item filed against the code they changed. Run the panel on each pull request's diff as it stood at merge, without telling the panel about the later defect. Count the pull requests where a panel finding names that defect. Also count the findings a reviewer would reject, because a panel that is mostly noise costs attention on every change. Run the subagents at the session's own model and effort, as `.claude/rules/apparatus-standard.md` requires.

**The bar, set before the count.** Adopt the panel only if it would have caught the later defect in at least three of the ten. Below that, a panel that runs on every simulator change finds too little to pay for its extra runs. The session proposed this bar and the owner agreed.

**Done when.** The ten pull requests and the defect items matched to them are listed here under a `**Result.**` heading, each with its result. The count is recorded against the bar. Either an item is filed to build the panel into review, or this item records why it was not adopted.

**Generator check.** Work the owner asked for, on 2026-10-24. It touches only its own brief, and no head's fact explains it.

**Protocol, fixed on 2026-10-24 before any panel ran.**

*Finding the pull requests.* The pairs come from the SZZ method, which traces a fix back to the change that introduced the lines it repaired (Śliwerski, Zimmermann and Zeller, "When do changes induce fixes?", MSR 2005, doi:10.1145/1083142.1083147). The population is every `done` item whose classes include `defect` or `safety`, and not `anticipated`, `test` or `infra`. For each one, the session took the commits on `origin/main` whose subject leads with the item's id. It then ran `git blame` at each fix's parent on the `src/anesthesia_sim/` lines that the fix removed or changed. A blamed commit enters as a candidate when it is a squash-merged pull request, is not the item's own fix, and merged before the item's file was first committed. That gave 73 candidate pull requests. One was excluded: `#588`, a 23,444-line port of twelve items, which no reviewer reads as one diff.

*Drawing the sample.* The candidates were shuffled with Python's `random.Random(20261024)`. The session walks that order and verifies each pair before it enters. A pair is verified only when the defect the item describes lives in lines that pull request added, not in lines it merely moved or touched. SZZ is known to blame refactors and moves, so this step is not optional. The first ten pull requests with at least one verified defect are the sample. The first 24 in the drawn order were `#1451`, `#1292`, `#337`, `#1414`, `#1585`, `#1481`, `#811`, `#1619`, `#1465`, `#191`, `#743`, `#1212`, `#331`, `#1413`, `#1350`, `#1365`, `#1653`, `#1370`, `#1337`, `#1453`, `#790`, `#834`, `#775` and `#768`.

*Keeping the panel blind.* Each reviewer gets two things: an export of the tree at the pull request's merge commit, made with `git archive` so it holds no later history, and that pull request's diff. It is told to read nothing outside that directory. The later defect item did not exist at that commit, because the item was filed after the merge.

*The panel.* Three general-purpose subagents review each diff, at the session's own model and effort:

1. A PK/PD and physiologic modelling reviewer: equations, units, parameter provenance, compartment and mass balance, and model applicability.
2. A numerical methods and simulation state reviewer: solver and timestep behaviour, floating-point edges, determinism, state transitions, and partial or stale state.
3. A clinical display and human factors reviewer: what a clinician or learner sees, labels, units, stale or wrong-context values, and error and halt presentation.

Each one reviews the whole diff from its own field and returns at most eight findings. Each finding names a file and symbol, the failure, and a severity of `blocking`, `should-fix` or `optional`.

*Scoring.* Before the panel runs, the session writes one sentence per verified defect saying what the defect was. A pull request counts as caught when any finding names the same faulty behaviour in the same code, so that acting on the finding would have fixed or prevented the defect. A finding that points at the right code but a different failure is a near miss. Near misses are recorded and not counted toward the bar. A separate subagent per pull request, also blind to the later defect, checks each finding against the code at merge and marks it correct, incorrect, or not checkable. Incorrect findings are the ones a reviewer would reject, and their share is the noise count.

*A control, only if the bar is met.* If the panel catches three or more, the same ten diffs go to one generalist reviewer with the same instructions and no specialty. If it catches as many, the item to build says to add one more review pass, not a panel of three. Below the bar the panel is not adopted, so the control would decide nothing and is not run.
