---
id: PL-9CNQ
title: A `docket gate` command, so the frozen debt list is computed rather than transcribed
priority: P2
effort: S
status: ready
classes: infra, session-cost
feature: planning-cadence
touches: subprojects/docket
added: 2026-08-25
---

**Problem.** `ROADMAP.md`'s debt gate now runs before every milestone, and the
frozen list is recorded by hand: a session reads every open item's `classes`
and `status`, applies the rule, splits the result by whether each item is in
the milestone's Required scope, and types the ids into the milestone section.
That was done for Gate 0 on 2026-08-25 and took a full pass over 48 items.

**Why it matters.** The whole of it is decidable from the files. Which items
are classed `defect`, `safety`, `science`, `refactor` or `perf`, which are at
`needs-decision`, which are still open, and which carry the milestone's
`feature` - all of it is in the frontmatter, and none of it needs judgment.
Per `CLAUDE.md`'s standing preference for deterministic tooling, work that
recurs on a cadence and has a decidable answer belongs in a command rather
than in a session's context, where it is re-derived at full price every time.
The gate is now explicitly recurring, which is exactly the condition that
makes this worth building.

**Where.** `subprojects/docket/`, alongside `milestone` and `status`.

**Scope.** `docket gate --feature <name>` prints the open debt items, split
into those carrying that feature (cleared by the milestone) and those not
(cleared before it), with effort totals. It computes the list; it does not
decide whether an item is really debt, does not write to `ROADMAP.md`, and
does not judge whether the gate should open. Recording the frozen list stays a
deliberate act, per "Recording it" - the command removes the transcription,
not the decision.

**Done when.** A session can produce the frozen list for a milestone with one
command, the output is stable for a given store, and it has a regression test
over a fixture store covering the in-scope/out-of-scope split.
