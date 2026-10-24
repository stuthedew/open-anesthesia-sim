---
id: PL-TCBJ
title: Replay a panel of specialist reviewer subagents (PK/PD, numerical solver, clinical display) on about ten merged simulator pull requests that later had a defect filed, and adopt it only if it would have caught at least three
priority: P3
effort: M
status: ready
classes: planning
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
