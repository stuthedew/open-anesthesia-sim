---
id: PL-P233
title: docs/maintainer.md states PL-SQTR's interim review rule: read a pull request that changes the simulator paths before arming it, until PL-K6B2's tiered arm lands
priority: P2
effort: S
status: done
classes: docs
feature: review-hold
milestone: v0.5.12
touches: docs/maintainer.md
added: 2026-09-25
closed: 2026-09-25
pr: 1027
payoff: until the tiered arm lands, a pull request that changes the simulator is read before it is armed, so a simulator change cannot reach main on green CI alone
verify: grep -qF '## Read a simulator change before you arm it' docs/maintainer.md
---

**Problem.** `PL-SQTR`'s third answer (project owner, 2026-09-25, ratified, over leaving the review hold as it stands) is an interim rule: read a pull request that changes `src/`, `tests/` outside `subprojects/`, `docs/MODEL.md`, `src/anesthesia_sim/data/` or `README.md` before arming it, until `PL-K6B2` builds an arm that holds only what needs a read. It belongs where the owner looks when arming, `docs/maintainer.md`.

**Why it matters.** `bin/docket arm` holds every pull request that changes anything outside `docs/items/`. On 2026-09-25 the owner confirmed those holds were being clicked through, so a simulator change could reach `main` unread. The owner's read is the guard for the paths the safety-critical standard covers. Until `PL-K6B2` narrows the hold, this section is the only thing that tells the owner which holds need a real read.

**Filed after the edit.** The section was written in #1027 with no item to claim. `PL-SQTR`, whose answer it is, became `blocked` by `PL-CBDX` and `PL-K6B2` in the same commit, and `bin/docket claim` refuses a blocked item ("which releases a claim as soon as it is written; set its status first"). CI's branch-id check then refused the branch on 2026-09-25 (`checks` job 108281894829: "this branch claims nothing"). This item gives the edit an id to claim, per `CLAUDE.md`'s housekeeping rule. The first-edit hook that would have asked before the edit never saw it, because the edit went through Bash (`PL-RXFK`).

**Done when.** `docs/maintainer.md` carries § "Read a simulator change before you arm it", naming the paths, the owner's decision, and `PL-K6B2` as what ends it. The verify fails on `origin/main` at 688827c1 (exit 1) and passes on this branch (exit 0), checked 2026-09-25. `PL-K6B2`'s build replaces the section.
