---
id: PL-SZJ2
title: wave reports nothing for a released milestone row whose own frozen list still has open entries, which is PL-LN3T's case in the other subsection: a gate-only milestone released with its list open drops out of the report entirely
priority: P2
effort: M
status: done
classes: defect
feature: timeline-arrangement
milestone: v0.5.5
touches: subprojects/docket/src/docket/roadmap.py, subprojects/docket/tests/test_roadmap.py, subprojects/docket/src/docket/render.py, subprojects/docket/README.md
added: 2026-09-19
closed: 2026-09-22
pr: 906
payoff: stops gate work a release stepped past from vanishing out of every report with nothing saying so, while a correctly deferred entry such as PL-WZVZ stays silent
verify: uv run pytest subprojects/docket/tests/test_roadmap.py::test_a_released_milestone_row_with_its_frozen_list_still_open_is_reported subprojects/docket/tests/test_roadmap.py::test_a_released_frozen_list_entry_deferred_to_a_later_gate_says_nothing
---

**Problem.** wave reports nothing for a released milestone row whose own frozen list still has open entries, which is PL-LN3T's case in the other subsection: a gate-only milestone released with its list open drops out of the report entirely

**Found 2026-09-19 closing `PL-LN3T`**, and measured rather than reasoned.
`PL-LN3T` added `stale_scopes`, which reports a milestone row the version table
records as released while the section's own `Required scope` still has open ids.
A section's *other* placing structure is its frozen list, and nothing reports
the same fault there: `wave` picks its gate with
`next((s for s in train.ahead if s.records_a_gate), None)`, and `ahead` holds
unreleased sections only, so a released section's open list is not counted,
named or reported anywhere.

Reproduced against `SHIPPED_PORT_ROADMAP` with the port's `Required scope`
replaced by a frozen list holding one open entry - v0.3.0's shape, where the
whole content of the milestone is the gate. At version `0.3.6`, with the port's
own number recorded as shipped, `wave` returns `stale == ()`, reports the gate
under v0.4.0 instead, and the port's open entry appears nowhere in
`format_wave`'s output.

**Why it matters.** It is `PL-Y1L0`'s failure - the owner's placement of a
milestone reversed by a release that never touched it - in the one section shape
`PL-LN3T`'s statement cannot see. It is narrow on today's file: every scoped
milestone here also records a `Required scope`, so a release that stepped past
one would trip `stale_scopes` on that subsection first. Rows 1 and 2 are the
shape that would not - `ROADMAP.md` § "Rows 1 and 2 are the only releases whose
whole content is a frozen list" - and both have shipped.

**Done when.** Either `wave` carries a released milestone row whose own frozen
list has open entries as a `stale` statement, with a test pinning it, or the
case is recorded as deliberately not reported with the reason written down. The
design question is whether "open" here is `GateStatus.outstanding` or its
narrower `clearable`: an entry blocked outside the list is open and is not
something the shipped milestone could have closed, which is the distinction
`ScopeStatus` has no counterpart for and the reason this is not a two-line
copy of `stale_scopes`.

**Decision needed.** Two questions, and the second only if the first is yes.

1. **Should a released milestone row whose own frozen list still has open entries
   be reported at all?** Reporting it is consistent with `stale_scopes`, which
   reports the same fault in a section's *other* placing structure. Against: rows
   1 and 2 are the only sections here whose whole content is a frozen list, both
   have shipped, and every scoped milestone since also records a `Required
   scope` - so the statement may have no live subject and would be a check that
   fires never.
2. **If yes, what counts as "open"** - `GateStatus.outstanding`, or the narrower
   `clearable`? An entry blocked outside the list is outstanding and is not
   something the shipped milestone could have closed, which is the distinction
   `ScopeStatus` has no counterpart for. This is why the change is not a two-line
   copy of `stale_scopes`.

`CLAUDE.md`'s retirement test is the frame for the first: a check that fires every
run without changing a decision is a defect in the check, and one that can never
fire is a line of code claiming coverage it does not provide.

**Decided 2026-09-22, by the session that implemented it.** Apparatus-internal
and confined to one report's behaviour, so the session's call rather than the
owner's (`.claude/rules/instruction-writing.md` rule 14).

1. **Yes, report it.** It has a live subject on every future cut rather than
   none. `ROADMAP.md` § "The cadence" beat 3 makes deferring a frozen entry to a
   later gate the normal case, and nothing checked the one decidable term of a
   deferral - that it names a later gate holding the entry - once the releasing
   section had left `ReleaseTrain.ahead`. v0.6.0's own list carries `PL-Y04W`
   deferred to Gate 3 and fifteen entries blocked on v0.7.0 work, so v0.6.0's
   cut is the next moment it can fire.
2. **Open is neither `outstanding` nor `clearable`: it is an open entry that no
   section ahead places** (`ReleaseTrain.places` - the frozen list and the
   `Required scope` of every unreleased section). Measured on the real file:
   released v0.2.8 and v0.4.0 hold no open entry, and v0.5.0 holds one,
   `PL-WZVZ`, blocked outside the list and deferred onto Gate 2's by `PL-S5Q9`.
   `outstanding` reports it - a mutant ignoring placement makes `bin/docket wave`
   exit 1 on this repository's own file - over a deferral done exactly as the
   cadence asks. `clearable` is silent on it for the wrong reason: it would stay
   silent on an entry blocked outside and deferred to nowhere, the case the
   cadence names as illegitimate, and would report an unblocked entry deferred
   correctly. Placement is the cadence's own test, so it is the one used. Ids
   the released section's own `Required scope` names are `stale_scopes`'
   statement already and are passed over, as are ids the store does not hold.

Shipped as `roadmap.stale_gates`, beside `stale_scopes` and sharing its loop
over released rows (`_released_rows`); `wave` appends its statements to `stale`.
