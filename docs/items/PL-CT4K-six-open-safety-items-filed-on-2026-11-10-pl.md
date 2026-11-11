---
id: PL-CT4K
title: Six open safety items filed on 2026-11-10 (PL-0G2P, PL-B8DL, PL-G2WC, PL-GJ1W, PL-GKG4, PL-LHCL) are not on v0.7.0's frozen list, though a safety item re-enters the gate whether or not its problem was present at the freeze
status: untriaged
added: 2026-11-11
---

**Problem.** Six open safety items filed on 2026-11-10 (PL-0G2P, PL-B8DL, PL-G2WC, PL-GJ1W, PL-GKG4, PL-LHCL) are not on v0.7.0's frozen list, though a safety item re-enters the gate whether or not its problem was present at the freeze

**Found 2026-11-10 while closing `PL-LMJ8`.** The documentation check prints this advisory at `ROADMAP.md` § "Debt gate: the frozen list": the frozen list places none of `PL-0G2P`, `PL-B8DL`, `PL-G2WC` (a compare run shows stale values), `PL-GJ1W` (no single statement of allowed error), `PL-GKG4` (blood flow is a bare number) and `PL-LHCL` (bare numbers in `core/`). All six are classed `safety`, and `ROADMAP.md` § "Which findings re-enter the gate" puts a safety item on the current gate whether or not its problem was present at the freeze. `origin/main` has the same gap, so `PL-LMJ8` did not cause it.

**What to do.** Add each to the frozen list's second group with the date and the reason it re-entered, as the 2026-11-09 paragraph in § "Captures after the cut" does for `PL-11Z9`, and update the group's count. Or place one in Required scope where the milestone should clear it itself. `PL-RF2S` (draw every View whole from one value) is being built as the root cause of `PL-B8DL`, `PL-0G2P` and `PL-G2WC`, and it is filed on a branch, so check whether it belongs on the list too.
