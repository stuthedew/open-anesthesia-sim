---
id: PL-CT4K
title: Six open safety items filed on 2026-11-10 (PL-0G2P, PL-B8DL, PL-G2WC, PL-GJ1W, PL-GKG4, PL-LHCL) are not on v0.7.0's frozen list, though a safety item re-enters the gate whether or not its problem was present at the freeze
priority: P2
effort: S
status: ready
classes: defect, docs
touches: ROADMAP.md
added: 2026-11-11
payoff: v0.7.0's gate lists every safety item that must clear before its features are built
verify: grep -qE '^- PL-0G2P \(' ROADMAP.md && grep -qE '^- PL-B8DL \(' ROADMAP.md && grep -qE '^- PL-G2WC \(' ROADMAP.md && grep -qE '^- PL-GJ1W \(' ROADMAP.md && grep -qE '^- PL-GKG4 \(' ROADMAP.md && grep -qE '^- PL-LHCL \(' ROADMAP.md
---

**Problem.** Six open safety items filed on 2026-11-10 (PL-0G2P, PL-B8DL, PL-G2WC, PL-GJ1W, PL-GKG4, PL-LHCL) are not on v0.7.0's frozen list, though a safety item re-enters the gate whether or not its problem was present at the freeze

**Found 2026-11-10 while closing `PL-LMJ8`.** The documentation check prints this advisory at `ROADMAP.md` § "Debt gate: the frozen list": the frozen list places none of `PL-0G2P`, `PL-B8DL`, `PL-G2WC` (a compare run shows stale values), `PL-GJ1W` (no single statement of allowed error), `PL-GKG4` (blood flow is a bare number) and `PL-LHCL` (bare numbers in `core/`). All six are classed `safety`, and `ROADMAP.md` § "Which findings re-enter the gate" puts a safety item on the current gate whether or not its problem was present at the freeze. `origin/main` has the same gap, so `PL-LMJ8` did not cause it.

**What to do.** Add each to the frozen list's second group with the date and the reason it re-entered, as the 2026-11-09 paragraph in § "Captures after the cut" does for `PL-11Z9`, and update the group's count. Or place one in Required scope where the milestone should clear it itself. `PL-RF2S` (draw every View whole from one value) is being built as the root cause of `PL-B8DL`, `PL-0G2P` and `PL-G2WC`, and it is filed on a branch, so check whether it belongs on the list too.

**Reproduced 2026-11-11.** `grep -c` finds none of the six ids in `ROADMAP.md`.

**Why it matters.** The frozen list is the record of what must clear before v0.7.0's implementation begins. Six safety items missing from it make the gate look smaller than it is, and safety work is the work the gate exists to keep ahead of new features.

**Done when.** Each of the six is on v0.7.0's frozen list, either in the second group with the date and the reason it re-entered or in Required scope, and the group's count is updated.

**Generator check.** A one-off. The fact is which open items the current gate holds, and the documentation check already advises on missing ids, which is how this was found. No head's `misread:` states it.
