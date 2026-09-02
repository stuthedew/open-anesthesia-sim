---
id: PL-Y4Q4
title: PL-0MLQ is safety-classed and predates the freeze, but is absent from Gate 0's frozen list, so wave reports the gate one entry short
status: untriaged
touches: ROADMAP.md
added: 2026-09-01
---

**Problem.** `PL-0MLQ` (refuse a setting outside the documented supported
input range) is classed `safety` at `P1`. `ROADMAP.md`'s "The gate is a
snapshot, not a moving target" re-enters anything classed `safety` or
`science` into the current gate "regardless of presence", and its presence
qualifies independently: the four compartment setters have never enforced
`docs/MODEL.md` § "Supported input ranges", so the problem was in the tree on
2026-08-25 when Gate 0 was frozen. It is nonetheless named nowhere in
`ROADMAP.md` — not in the frozen list under "Milestone after next: v0.4.0",
not in v0.3.0's out-of-scope list, and not among the ten review findings
deferred to Gate 1. It was captured 2026-08-30, the same day four other
findings from that review were admitted to the gate by exactly this rule
(`PL-VP7N`, `PL-SLHS`, `PL-9Y42`, `PL-NV9W`), and it was found while
implementing `PL-VP7N`, which is itself a frozen-list entry.

**Why it matters.** The frozen list is v0.3.0's whole specification — that
release "has no scope of its own to specify", and its definition of done is
that every entry on the list is `done` or `dropped`. An entry that is not on
the list is not in that definition, so v0.3.0 can ship its claim that the
ground is solid while `core/` still accepts a cardiac output of 1000 L/min,
a fresh gas flow of 500 L/min, and an alveolar ventilation of 200 L/min —
values outside the domain the splitting-error bound
($`C_{\max} = 2.29\times10^{-3}\ \mathrm{s^{-1}}`$), the displayed
resolution, and the supported step were all measured over. That is the same
argument the roadmap makes for admitting `PL-VP7N`, one axis over.

It is also invisible to the tool. `bin/docket wave` computes the gate split
by reading the recorded entries against `docs/items/`, so an unrecorded entry
cannot be counted: the gate reports clear when it is not. Recording is what
makes the mechanism work — "a gate nobody wrote down is a gate that gets
renegotiated" — and this is the failure mode that sentence describes,
arriving through omission rather than argument.

The pairing rule ("worked with the entry it completes, not after it") cannot
be satisfied here: `PL-VP7N`, the entry `PL-0MLQ` continues, shipped in
v0.2.7. It therefore stands as its own Gate 0 entry rather than joining a
branch, and that is worth stating in the list so a later reader does not read
the omission as a deliberate deferral.

**Where.** `ROADMAP.md`, "Debt gate: the frozen list" under "Milestone after
next: v0.4.0 - the teachable case" — the *Core correctness* group, beside
`PL-VP7N` and `PL-SLHS`. The paragraph beneath the list that records the four
2026-08-30 additions needs the fifth added to it with its own grounds, and the
entry and id counts in the list's header sentence move from 20/21 to 21/22.
The timeline row for step 2 (`v0.3.0 — the foundation`, sized `3 M, 17 S`)
carries a size that this changes.

**Alternative disposition.** Defer to Gate 1 and say why, which "Presence is a
presumption, not an absolute rule" permits for a presence-qualifying finding.
It does not obviously apply: the two stated reasons for deferring are that the
finding has no real connection to frozen scope, or that pulling it in recreates
the refilling-queue problem — and this one continues a frozen entry directly.
The `safety` class is the harder obstacle, since that exception is written as
not deferrable at all.

**Done when.** `ROADMAP.md` either lists `PL-0MLQ` as a Gate 0 entry with its
grounds recorded, or states in the frozen list's own text why a `safety`-classed
finding that continues `PL-VP7N` defers to Gate 1 — and the entry counts, the
step-2 size, and v0.3.0's definition of done agree with whichever was chosen.
