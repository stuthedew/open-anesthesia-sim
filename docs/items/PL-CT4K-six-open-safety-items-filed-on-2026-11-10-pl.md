---
id: PL-CT4K
title: Six open safety items filed on 2026-11-10 (PL-0G2P, PL-B8DL, PL-G2WC, PL-GJ1W, PL-GKG4, PL-LHCL) are not on v0.7.0's frozen list, though a safety item re-enters the gate whether or not its problem was present at the freeze
priority: P2
effort: S
status: done
classes: defect, docs
touches: ROADMAP.md, docs/items/PL-CR81-projects-threads-in-the-v0-7-0-project-run.md, src/anesthesia_sim/core/liquid_agent.py, docs/items/PL-LHCL-a-number-in-core-is-known-to-be-inside-its.md, docs/items/PL-GJ1W-nothing-states-in-one-place-how-far-a-computed.md
added: 2026-11-11
closed: 2026-11-16
pr: 2168
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

**Done 2026-11-16.** `ROADMAP.md` places seven items in v0.7.0's second
group, the entries cleared before implementation begins: the six this brief
names and `PL-RF2S`. The group's count went from 165 to 172. A dated
paragraph at the end of § "Captures after the cut" says that each joined on
2026-11-16 because it is classed `safety`, which re-enters the gate whether or
not its problem was present at the freeze. It follows the 2026-11-09
paragraph's form but sits after the 2026-11-11 paragraphs, because that
section runs in date order.

Each item's status, from `bin/docket show` that day: `PL-0G2P`, `PL-B8DL`,
`PL-G2WC`, `PL-GJ1W`, `PL-LHCL` and `PL-RF2S` are `ready`. `PL-GKG4` is `done`
(closed 2026-11-11). It is still listed, because the rule put it on the list
while it was open, and the list records entries the gate cleared as well as
open ones.

**`PL-RF2S` belongs on the list.** It is classed `safety` and is open, and
the documentation check named it in the same advisory as five of the six. It
reached `main` after this brief was written. Placing it also made a clause in
the 2026-11-11 paragraph about `PL-1FPR` false, the one saying that this list
does not hold `PL-RF2S`. That clause now says that `PL-RF2S` is itself
deferred to the next gate.

**The deferrals.** All seven carry `deferred-from: v0.7.0`, and `PL-GKG4` is
closed. For the six open ones, the field no longer conflicts with being
listed: § "Deferring to the next gate" defers a
`safety` entry only while it stays written on the frozen list. `PL-0G2P`,
`PL-B8DL`, `PL-G2WC` and `PL-RF2S` record in that field that their hazard
was checked and is not live. `PL-GJ1W` and `PL-LHCL` do not. Their field's
reason is that they were filed after the gate froze and that their design
waits on the owner. That section allows a `safety` deferral only with a
not-live record, and § "Which findings re-enter the gate" says being filed
after the freeze is no reason to defer. Their front matter was left for the
thread to correct: each needs a not-live check against the tree, or the
deferral removed.

After the change, the documentation check no longer prints the frozen-list
advisory. `bin/docket wave --no-fetch` reports 183 entries: 151 cleared and 32
open, of which 20 this gate can clear and 12 are deferred from it.

Files checked in the docs sweep: `ROADMAP.md` (§ "Which findings re-enter the
gate", § "Deferring to the next gate", the v0.7.0 frozen list and § "Captures
after the cut"), and the front matter of the seven items.
