---
id: PL-5J1S
title: docs/dead-ends.md says raising its 4,000-byte budget is never right, but gives no rule for when every entry is still live and already one line: say what a session does then (bring the owner the per-turn cost of raising it, or move a group of entries to a path-scoped rule that fires where those approaches get proposed), and say how a session ranks entries before dropping one (chance it is re-proposed without reading the refutation, times the cost if it is)
priority: P3
effort: S
status: needs-decision
classes: docs, infra
feature: dead-ends-budget
touches: docs/dead-ends.md, tools/dead_ends.py, tests/unit/test_dead_ends.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-19 triage pass
added: 2026-10-19
---

**Problem.** docs/dead-ends.md says raising its 4,000-byte budget is never right, but gives no rule for when every entry is still live and already one line: say what a session does then (bring the owner the per-turn cost of raising it, or move a group of entries to a path-scoped rule that fires where those approaches get proposed), and say how a session ranks entries before dropping one (chance it is re-proposed without reading the refutation, times the cost if it is)

**The owner's two goals, 2026-10-19 (project owner, 2026-10-19).**
1. A lesson learned the hard way must not be unlearned later, so that the
   unwanted behavior comes back.
2. An entry that came up once, months ago, must not keep its place while a
   new and more useful lesson is left out.

**Recommended design, for when the generator pause lifts.** Nothing is
deleted outright. An entry only moves to a cheaper place, and the move is
allowed only where that place still stops the approach at the moment a
session would propose it.

- **Removing an entry needs a named catcher.** When an entry leaves
  `docs/dead-ends.md`, its id must appear in one of three places: a check
  that refuses the approach, a path-scoped rule under `.claude/rules/` that
  loads where the approach would be built, or a docstring in the code that a
  session must read to build it. `tools/dead_ends.py` can enforce this by
  comparing the file against `origin/main`. Any id that disappears must turn
  up in one of those places, or the check fails. This serves goal 1, and it
  is a deterministic check rather than a judgment.
- **The resident list keeps the entries that are proposed before any read.**
  These are approaches a session suggests in a reply, at a design round,
  before opening a file. The cheaper-subagent-model entry is the example. An
  entry about the item store is proposed only by someone editing
  `subprojects/docket/`, so a rule scoped to that path catches it just as
  well. At the budget, the entry that a path-scoped rule could catch moves
  first, whatever its age. A new entry is never refused for lack of room.
  This serves goal 2.
- **Age is not the test.** An old entry that still guards a live temptation
  stays. An entry goes when its design question no longer exists, for
  example when the code it refers to was removed.
- **If every entry is needed before any read, and each is one line, the
  session brings the owner the budget question.** It states the cost: about
  1 token per 4 bytes on every turn of every session. The current rule that
  raising the budget is never right is replaced by that question.

**Why it matters.** `docs/dead-ends.md` is the list of refuted approaches
that the session-start digest prints on every turn, so a session sees the
refutation at the moment it would re-propose the approach. Its rule says
raising the 4,000-byte budget "is the one repair that is never right", and
its other repairs both remove an entry. Once every entry is still live and
already one line, the rule leaves a session only one move: drop a lesson
that is still needed, which is the owner's first goal broken.

**Measured 2026-10-19.** `python3 tools/dead_ends.py emit` printed 3,176
bytes over 13 entries on `main` at `1e5cb9bd`, 79% of the byte budget, and
`python3 tools/dead_ends.py check` exited 0. The case is close but not here
yet.

**Decision needed.** Which rule replaces "never raise the budget": the
**Recommended** design above (an entry leaves the list only for a named
place that still catches it, checked by `tools/dead_ends.py`; at the budget
the entry a path-scoped rule could catch moves first; when every entry must
stay resident, the session brings the owner the per-turn cost of raising the
budget), or the title's ranking of entries by the chance of re-proposal times
its cost. **Recommendation: the design above.** It enforces the first goal
with a check rather than a judgment, and it meets the second without asking a
session to estimate a probability it has no data for. It is the owner's call
because it changes when a refuted approach stops being shown to every
session, which is a rule about how the project keeps what it has learned.

**Done when.** `docs/dead-ends.md` states the chosen rule for the case where
every entry is live and one line, and replaces the sentence calling a raised
budget "never right". If the recommended design is chosen,
`tools/dead_ends.py check` fails when an id leaves the list without appearing
in a check, a path-scoped rule or a docstring, and
`tests/unit/test_dead_ends.py` covers that refusal.

**Generator check.** A one-off, raised by the owner. The gap is one missing
case in one document's rule, and no head's `misread:` states which refuted
approaches stay resident.
