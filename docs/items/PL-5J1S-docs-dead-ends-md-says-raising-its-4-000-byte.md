---
id: PL-5J1S
title: docs/dead-ends.md says raising its 4,000-byte budget is never right, but gives no rule for when every entry is still live and already one line: say what a session does then (bring the owner the per-turn cost of raising it, or move a group of entries to a path-scoped rule that fires where those approaches get proposed), and say how a session ranks entries before dropping one (chance it is re-proposed without reading the refutation, times the cost if it is)
status: untriaged
feature: dead-ends-budget
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
