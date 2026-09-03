---
id: PL-W8XP
title: An item blocked on a milestone being scoped cannot say so: blocked-by only names items
priority: P2
effort: S
status: ready
classes: infra
feature: dev-tooling
touches: subprojects/docket/src/docket/model.py, subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/roadmap.py, subprojects/docket/tests, subprojects/docket/README.md
verify: uv run pytest subprojects/docket/tests/test_checks.py && grep -q 'def test_blocked_by_may_name_a_milestone' subprojects/docket/tests/test_checks.py
added: 2026-09-03
---

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
recurs rather than being a one-off. The workaround has a second cost: a
`needs-decision` status is debt by `docket.toml`'s `debt_classes` rule, so
every item parked this way is counted into the next gate as though somebody
could resolve it, when the only thing that resolves it is the scoping round
itself.

**Where.** `subprojects/docket/src/docket/model.py` (the `blocked_by` field and
its parsing), `checks.py` (the blocked-item checks, including "every blocker
has closed"), `roadmap.py` (which already parses the milestone table),
`subprojects/docket/README.md` (the item format).

**Approach.** Let `blocked-by:` name a milestone as well as an item —
`blocked-by: v0.5.0` — and have `docket check` resolve it against
`ROADMAP.md`'s milestone table, which `tools/doc_check.py` and
`docket.roadmap` already parse. A milestone counts as closed for this purpose
once it has a scoped section, which is the condition the briefs actually
state. The alternative considered and rejected was a `blocked-on-milestone:`
field beside the existing one: it keeps the id parsing simple, at the cost of
two fields meaning one thing and every reader of `blocked-by:` having to know
about the second. One field with two kinds of entry is the smaller vocabulary.

Classed `infra` rather than `defect` deliberately: nothing currently
misreports, because the workaround above is honest as far as it goes. This is
a missing representation rather than a live defect, so it is not gate debt.

**Done when.** `blocked-by:` accepts a milestone version alongside item ids;
`docket check` resolves it against `ROADMAP.md` and neither raises the
"every blocker has closed" advisory nor a hard error while the milestone is
unscoped; `PL-B9PY` is moved off its `needs-decision` workaround onto
`blocked-by: v0.5.0`; and `subprojects/docket/README.md` documents the two
kinds of entry.

**Found.** Closing `PL-WB0X` (split `simulation_view.py`), 2026-09-03, which
was `PL-B9PY`'s only representable blocker.
