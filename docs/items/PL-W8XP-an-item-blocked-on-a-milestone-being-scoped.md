---
id: PL-W8XP
title: An item blocked on a milestone being scoped cannot say so: blocked-by only names items
priority: P2
effort: S
status: done
classes: infra
feature: dev-tooling
milestone: v0.4.11
touches: subprojects/docket/src/docket/model.py, subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/roadmap.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests, subprojects/docket/README.md
added: 2026-09-03
closed: 2026-09-08
pr: 478
verify: uv run pytest subprojects/docket/tests/test_checks.py && grep -q 'def test_blocked_by_may_name_a_milestone' subprojects/docket/tests/test_checks.py
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
unscoped; and `subprojects/docket/README.md` documents the two kinds of entry.

**A fourth clause was dropped rather than met: "`PL-B9PY` is moved off its
`needs-decision` workaround onto `blocked-by: v0.5.0`".** It was written on
2026-09-03 and overtaken on 2026-09-06, when v0.5.0 was scoped. Writing
`blocked-by: v0.5.0` onto `PL-B9PY` now would resolve as cleared on the first
`docket check`, which is `ready` said in two steps; and `PL-B9PY` was promoted
to `ready` outright the same session this landed, under `PL-MKFG`. The
representation is what this item owed, and the worked example that motivated it
had stopped needing it — which is a good outcome for that item and leaves this
one with no live user.

**Shipped with no live user, deliberately.** No open item currently waits on an
unscoped milestone: `PL-B9PY` is `ready`, and the two others this brief counted
at Gate 1 have since closed or dropped (`PL-XYRN` done, `PL-X9R0` dropped).
That is not an argument for having deferred it. v0.6.0 and v0.7.0 both sit on
the timeline unscoped, so the next item placed against either has the field
waiting rather than the three wrong states this brief opens with; and the cost
of the mechanism is paid once, while the cost of the workaround is paid by
every session that reads a `needs-decision` it cannot resolve.

**Found.** Closing `PL-WB0X` (split `simulation_view.py`), 2026-09-03, which
was `PL-B9PY`'s only representable blocker.

**How it was built.** `Item.blocking_milestones` matches `^v\d+\.\d+\.\d+$`
positively and `Item.blocking_items` is *everything else* — a fail-closed
partition, so an entry of neither shape stays an item entry and is refused by
name in `checks.py` rather than falling out of both halves and being ignored.
The raw `blocked_by` is untouched, so `render_item` round-trips a milestone
entry; a test asserts that, because a partition that dropped it would silently
unblock the item on the next write. `roadmap.milestone_states` reads the
timeline *and* the sections for `known` — a milestone is placed long before it
has a section, which is the interval this field exists to cover — and clears a
milestone that is scoped **or** completed. The second half is not redundant:
`ROADMAP.md`'s own v0.2.8 and v0.3.0 sections answer `is_scoped` False, v0.2.8
because the file says its frozen list *is* its content, so a structural test
alone would leave a blocker naming either permanently unresolved and silent.

`analyze` takes the states as a parameter rather than reading `ROADMAP.md`
itself, per its own docstring: inputs that cannot be read from the store are
passed in, and `cli.py`'s `_milestones` declines exactly as `_plan` does, so a
bare checkout gets its queue validated and a `declined` line naming the items
it could not judge. `cli.py` was added to `touches` during the work: without it
`analyze` would receive `None` forever and the feature would decline in every
session.

Verified end to end against the real store as well as by unit test — a scratch
item at `blocked-by: v0.6.0` gives 0 errors and no advisory, at `v0.5.0` raises
"v0.5.0 is scoped and every other blocker has closed", and at `v9.9.9` is an
error naming the version.
