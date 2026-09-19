---
id: PL-SZJ2
title: wave reports nothing for a released milestone row whose own frozen list still has open entries, which is PL-LN3T's case in the other subsection: a gate-only milestone released with its list open drops out of the report entirely
status: untriaged
feature: timeline-arrangement
added: 2026-09-19
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
