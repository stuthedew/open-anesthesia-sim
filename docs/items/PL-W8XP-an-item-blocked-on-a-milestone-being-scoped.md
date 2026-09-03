---
id: PL-W8XP
title: An item blocked on a milestone being scoped cannot say so: blocked-by only names items
status: untriaged
added: 2026-09-03
---

**Problem.** An item blocked on a milestone being scoped cannot say so: blocked-by only names items

**Why it matters.**

**Where.**

**Done when.**

**Problem.** `blocked-by:` takes queue-item ids. An item whose real dependency
is *a milestone being scoped* therefore has no honest state. `PL-B9PY`
(decompose `SimulationView` so two runs can be rendered at once) is the worked
example: its brief says it is "blocked on two things" — `PL-WB0X`, and v0.5.0
being scoped — and only the first was representable. When `PL-WB0X` closed on
2026-09-03 the store offered three states and all three were wrong:

- `blocked` with `blocked-by: PL-WB0X` — false once that item is `done`, and
  `docket check` then raises "every blocker has closed; it is ready to
  promote" in every session from now until v0.5.0 is scoped;
- `blocked` with the field emptied — a hard error, "marked blocked but names
  no blocking item";
- `ready` — invites a session to start a refactor against a target shape
  nobody has decided, which that item's own brief forbids.

It was settled as `needs-decision` with a **Decision needed.** line naming the
scoping round. That is accurate for this item and it is a workaround: the
dependency is on a milestone, and the store records it as a decision because
that is the only shape available.

**Why it matters.** The first bullet is the failure mode `CLAUDE.md` names —
an advisory firing every run that nobody can act on trains a session to skim
the output where a real one also appears. Two items already sit at Gate 1
against unscoped milestones, and `ROADMAP.md`'s Phase 3 places more, so this
recurs rather than being a one-off.

**Approach (proposed, not decided).** Let `blocked-by:` name a milestone as
well as an item — `blocked-by: v0.5.0` — and have `docket check` resolve it
against `ROADMAP.md`'s milestone table, which `tools/doc_check.py` and
`docket.roadmap` already parse. A milestone is "closed" for this purpose once
it has a scoped section, which is the condition the briefs actually state.
The alternative, a `blocked-on-milestone:` field beside the existing one,
keeps the id parsing simple at the cost of two fields meaning one thing.

**Found.** Closing `PL-WB0X` (split `simulation_view.py`), 2026-09-03, which
was `PL-B9PY`'s only representable blocker.
