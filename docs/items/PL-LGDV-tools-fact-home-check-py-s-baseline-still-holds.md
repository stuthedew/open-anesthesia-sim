---
id: PL-LGDV
title: tools/fact_home_check.py's baseline still holds 59 second readers (49 duplicate module-level names across docket and tools such as FENCE, MARKER, API, TIMEOUT_S and ITEM_ID, 6 git readers outside docket.vcs and 4 GitHub API readers) and no open item drains it since PL-5DZ8 closed
priority: P2
effort: L
status: ready
classes: defect
feature: one-source-of-truth
touches: tools/fact_home_check.py, tools/, subprojects/docket/src/docket/
added: 2026-10-19
payoff: each apparatus constant and git or GitHub reading has one home, so two copies cannot drift into two answers
verify: grep -qF 'BASELINE: dict[str, dict[tuple[str, str], int]] = {}' tools/fact_home_check.py
---

**Problem.** tools/fact_home_check.py's baseline still holds 59 second readers (49 duplicate module-level names across docket and tools such as FENCE, MARKER, API, TIMEOUT_S and ITEM_ID, 6 git readers outside docket.vcs and 4 GitHub API readers) and no open item drains it since PL-5DZ8 closed

**Why it matters.** Each entry is a fact read or defined in two places, for example `FENCE` in both `frontmatter.py` and `markdown.py`, or a git reader outside `docket.vcs`. `tools/fact_home_check.py` refuses new ones, but the 59 recorded when it landed can still drift apart. No open item was draining them.

**Class.** Each baseline entry is a second copy, which breaks a rule this repository states, so `CLAUDE.md`'s fix-in-place condition 1 counts it as a defect whether or not the copies disagree today (project owner raised this on 2026-10-24).

**Done when.** `BASELINE` in `tools/fact_home_check.py` is empty. Each duplicate name is imported from one home, and each git or GitHub API reader goes through the module that owns that reading. This is large, so a session may split it by module as it starts, filing the parts under `one-source-of-truth`.

**Checked 2026-10-24.** `BASELINE` is not empty. It lists, among others, `FENCE` twice in `markdown.py`, `ID` in `claiming.py` and `claims.py`, and `_git` readers in `claiming.py` and `tools/branch_sweep.py`.

**Generator check.** Bookkeeping. This is the baseline the check recorded when it landed, so it is not new inflow.
