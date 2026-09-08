---
id: PL-HX5C
title: Both in-flight guards passed and two sessions still implemented PL-W8XP independently: the second never renamed and its branch was named after a different item, so neither the ref read nor the session read could see it
priority: P2
effort: S
status: needs-decision
classes: infra, session-cost
feature: parallel-sessions
touches: .claude/skills/docket/SKILL.md
added: 2026-09-08
---

**Problem.** Both in-flight guards passed and two sessions still implemented PL-W8XP independently: the second never renamed and its branch was named after a different item, so neither the ref read nor the session read could see it

**Why it matters.** The docket skill's "Mode: start an item" already documents
this window and judges the trade worth taking: "a session picking a different
item because one looked busy costs almost nothing against a queue this size,
while two sessions on one item costs a session and a merge conflict"
(`PL-PRHN`). This is the first recorded instance of the cost side actually
being paid, and it was paid in full — a complete duplicate implementation of
`PL-W8XP`, converging on the same design independently, discarded at the merge.
So the trade is not wrong; the estimate of how often the guards fail is.

**What happened, because the sequence is the finding.** On 2026-09-08 this
session opened on `PL-W8XP` and ran both guards before starting:

- `git fetch origin && bin/docket show PL-W8XP` — clean. Correct at the time:
  the other session had committed nothing naming the item yet, and the skill
  already says a fetched `show` answers only for what has been *pushed*.
- `list_sessions` (`mine: true`) — six live sessions, none titled `PL-W8XP`
  and none carrying it in `external_metadata.current_branches`.

The other session was `session_01URTE7tyDVsky2dfJaDVXpY`, titled
"Simulation_view.py refactoring" on branch
`claude/simulation-view-refactor-4h8f3m`. It shipped `#478` — `PL-W8XP,
PL-MKFG` — roughly an hour later. Both guards answered correctly and both
answered about something else, because **every cover this project has is
keyed on a name the second session never wrote**: the title check needs the
rename, the branch-name cover needs the branch created for the item, and the
ref read needs a commit. That session was legitimately working `PL-B9PY`
first, took `PL-W8XP` as the thing `PL-B9PY` was waiting on, and its title and
branch went on naming the item it started with.

The skill already measures the rename rule at about three sessions in four and
says finding nothing there means nothing. This adds the case that is worse
than "not renamed": a session correctly named after item A that picks up item
B mid-session, where the name is not merely missing but actively wrong.

**Where.** `.claude/skills/docket/SKILL.md`, "Mode: start an item" — the
session-list read and the branch-name cover. Possibly also
`subprojects/docket/src/docket/vcs.py`, if the answer turns out to be a check
rather than an instruction.

**Decision needed.** Whether anything cheap actually closes this, or whether
the honest answer is to record the instance and leave the window open. Three
candidates, and none is obviously right:

- **Rename on picking up a second item**, not only on starting the first. One
  line in the skill, costs nothing, and fails exactly the way the existing
  rename rule already fails — it is an instruction, and this one would have
  needed a session to notice it was changing items.
- **Push a claim commit before implementing**, which the skill already asks
  for ("push the first commit as soon as there is one"). The other session
  did not, because it was mid-way through `PL-B9PY`'s work. Tightening this
  to "before writing any code for a newly picked-up item" is enforceable by
  nothing.
- **Accept it and improve the recovery instead.** The merge is where this was
  caught, and it was caught cleanly — the conflict was loud, the duplicate was
  obvious on inspection, and the loser's unique work (`PL-3Y96`) was
  separable. That may be the whole of what is available.

**Done when.** Either the skill carries a rule that would have caught this
sequence, or this item is `dropped` with the reasoning recorded so the next
session to pay the cost does not re-open the question from scratch.

**Found.** Building `PL-W8XP` on 2026-09-08 and discovering at the push that
`#478` had merged an equivalent implementation.
