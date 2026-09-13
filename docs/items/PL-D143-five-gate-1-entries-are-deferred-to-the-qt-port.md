---
id: PL-D143
title: Five Gate 1 entries are deferred to the Qt port at v0.5.1 by owner decision but still count as open gate debt, so the gate that v0.5.0 waits on cannot close until after v0.5.1
priority: P2
effort: S
status: done
classes: defect, planning
milestone: v0.4.16
touches: docs/items/, ROADMAP.md
added: 2026-09-13
closed: 2026-09-13
pr: 512
verify: bin/docket check && [ "$(grep -l '^blocked-by: v0.5.1' docs/items/PL-3355-*.md docs/items/PL-Q4VH-*.md docs/items/PL-THXF-*.md docs/items/PL-TG60-*.md docs/items/PL-W8DQ-*.md | wc -l)" = 5 ]
---

**Problem.** Five open Gate 1 entries carry an identical blockquote, added by
the project owner on 2026-09-10:

```text
  This fix rides the Qt port (v0.5.1), not Flet. ROADMAP.md's v0.5.1 section
  names this item under "Fixes this port carries": the defect lives in code
  that milestone rewrites from scratch, so fixing it on Flet means writing the
  same lines twice.
```

They are `PL-3355` (readouts wrap their value onto a second line), `PL-Q4VH`
(the percent axis is labelled at a different interval from the gridlines it
rules), `PL-THXF` (the legend swatch is solid for a dashed trace), `PL-TG60`
(six decimals of an exhaust integral), and `PL-W8DQ` (the slider active tracks
miss the non-text contrast minimum). `PL-005` carries it too and is not a gate
entry.

All five are `status: ready` with no `blocked-by`, so `bin/docket next` offers
them and `bin/docket gate` counts them as open debt.

**Why it matters, and it is a plan contradiction rather than a queue tidiness
one.** `ROADMAP.md`'s debt gate says recorded debt is cleared **before** the
milestone it gates begins - Gate 1 before v0.5.0. These five cannot be cleared
before v0.5.0, because the decision is that they are fixed during v0.5.1, which
is after it. As written the gate cannot reach zero until a release that comes
after the release it is gating, and the beat `bin/docket wave` prints - "clear
the gate" - is asking for something the plan forbids.

It also costs a session directly. These five are the most coherent-looking
batch left in the gate: same feature, same file, all `ready`, all `S`. A
session clearing the gate picks them, and only finds the deferral by opening
the files - which is the good case. The bad case is not opening them.

**Decision needed.** Which of three, and it is the project owner's:

1. **`status: blocked`, `blocked-by: v0.5.1`.** The `docket` skill already
   names this shape for a milestone not yet scoped: it stops `next` offering
   them and stops `gate` counting them as resolvable debt. v0.5.1 is scoped
   and takes a section, so the checker's version rule is satisfied. This is
   the recommendation.
2. **Drop them from Gate 1 into a Gate 2 list**, on the ground that the frozen
   list should hold only what the milestone it gates can clear.
3. **Leave them**, and accept that Gate 1's count will not reach zero - which
   means saying so in `ROADMAP.md`, because otherwise every session reads the
   beat as achievable.

**Found** 2026-09-13, while picking a Gate 1 batch: all five were selected as
the batch before their files were read, and the deferral is only in the file.

**Done when.** The five entries carry a status that agrees with the decision -
`blocked` with `blocked-by: v0.5.1` under option 1, moved out of the frozen
list under option 2, or left as they are with `ROADMAP.md` saying plainly that
Gate 1 does not reach zero before v0.5.0 under option 3 - and `bin/docket gate`
and `bin/docket next` both report something a session can act on without
opening the five files to find out.

**Answered 2026-09-13: option 1** (project owner). The five entries are
`status: blocked`, and each carries a line under the owner's 2026-09-10 note
saying so. `bin/docket next` no longer offers them.

**The blocker is the port item, not the version, and the first attempt had it
wrong.** Written as `blocked-by: v0.5.1` it raised "v0.5.1 is scoped and every
other blocker has closed; it is ready to promote" on all five, every run - a
permanently-firing advisory, which `CLAUDE.md` calls a defect in the check
rather than a thing to live with. The store is right and the disposition was
wrong: `blocked-by: <version>` means *waiting for a milestone to be scoped*,
and `docket check` promotes such an item the moment that section carries its
four subsections. v0.5.1's already does.

So each is blocked on the port item that rewrites the code its defect lives in,
which is the edge that is actually true:

```text
  PL-3355  readouts wrap                  -> PL-25KS  port the dashboard
  PL-TG60  six decimals of the integral   -> PL-25KS  port the dashboard
  PL-Q4VH  percent axis vs gridlines      -> PL-G59B  port the chart
  PL-THXF  legend swatch vs dash pattern  -> PL-G59B  port the chart
  PL-W8DQ  slider track contrast          -> PL-L9RD  re-express theme.py for Qt
```

Caught by `docket check --verify`, which CI runs and `make check` does not.

**What this does not do, stated so the next session does not expect it.**
`bin/docket gate` counts a `blocked` item as open debt - `PL-GS3R` and
`PL-8PS6` are already in the list on that footing - so Gate 1 still reads 75
open rather than 70. The contradiction this item named is therefore narrowed
rather than removed: a session clearing the gate can no longer *pick* these
five, which was the concrete harm, but the gate's own count still cannot reach
zero before v0.5.1. Whether the frozen list should shed them is option 2 and
was not taken; if the count itself becomes misleading, that is the item to
reopen.
