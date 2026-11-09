---
id: PL-Q0J1
title: Triage the six captures open on 2026-09-16, second pass
priority: P2
effort: S
status: done
classes: planning
feature: planning-cadence
milestone: v0.4.26
touches: docs/items
added: 2026-09-16
closed: 2026-09-16
pr: 617
not-delegable: a triage pass is proven by the store's state at the moment it ran, and that state moves - captures arrive untriaged by design - so no command run afterwards separates 'the pass happened' from 'nothing has been captured since'. `bin/docket check`, already on `make check`, is the standing proof that what the pass wrote is valid (same argument as PL-0C6W, PL-2B7B, PL-Q2PX and PL-LYX2)
---

**Problem.** Triage the six captures open on 2026-09-16, second pass

**Why it matters.** `PL-0C6W` cleared the fourteen open that morning; six more
arrived across the day, from four sessions. Untriaged items are invisible to
`bin/docket next` - they carry no band, so nothing ranks them - which means a
finding sits in the queue looking recorded while being unreachable by every
session that asks what to do next.

**What was decided, and why.**

| item | landed on | reason |
| --- | --- | --- |
| `PL-2M4X` | **yielded** | triaged concurrently on `claude/pl-syg4-pl-2m4x-triage`; see below |
| `PL-85NT` | `dropped` | superseded by `PL-99YZ` on this item's own recommendation; its measurements are cited into `PL-99YZ` rather than repeated |
| `PL-L4KX` | `P2 · S · ready`, `delegation` | the only `P2` of the six: `bin/docket verify --self` REJECTs any close-out that drops an item, and this pass drops one, so the defect fires today |
| `PL-M3YJ` | `P3 · S · ready`, `dev-tooling` | a suppression that outlives its module is reported by nothing; cost of the flag is zero while `pyqtgraph` is the only override left |
| `PL-PGZF` | `P3 · M · ready`, `chart-readout` | kept separate from `PL-CNCF` rather than folded: different functions in different modules, and `PL-CNCF` carries `docs/MODEL.md` where this carries neither |
| `PL-SYG4` | **yielded** | triaged concurrently on `claude/pl-syg4-pl-2m4x-triage`; see below |

**Banding, against the standing advisory.** `docket check` reports 135
startable `P2` items against a limit of 12 and asks for demotion, so a `P2`
here needs defending rather than assuming. Five of the six are `P3`. The
exception, `PL-L4KX`, is `CLAUDE.md`'s second compounding-friction test read
literally: a refusal fired routinely on correct work, which trains a reader to
skim the block where a real protected-path failure is printed.

**Done when.** `bin/docket check` reports zero untriaged items and zero errors,
every one of the six carries the fields `docket check` requires at its status,
and each `ready` item names a `verify:` command that was run and watched fail
for the right reason before it was written down.

## Two of the six were yielded, 2026-09-16

**`PL-2M4X` and `PL-SYG4` were triaged twice, concurrently, and this pass
yielded them.** Both were triaged here first and pushed; a second session then
triaged both on `claude/pl-syg4-pl-2m4x-triage`. `bin/docket show` names that
branch and says *"do not start ... again"* for each, which is the verdict the
`docket` skill says to read rather than reason past. This branch restored
`origin/main`'s copies of both files, so they return to `untriaged` here and
that branch's answers stand alone.

**Yielded on substance as well as on the verdict**, which is worth recording
because the two agreed anyway. On `PL-SYG4` both passes independently reached
`P3 · M · needs-decision`; they differ only in `classes` (`defect` here,
`defect, infra` there) and `feature` (`release-process` against
`release-roadmap-seam`). What that branch has that this one does not is depth -
152 added lines on `PL-SYG4`, 61 on `PL-2M4X`, and four further captures
(`PL-C6XD` among them) that came out of reading the same code. Keeping the
thinner answer and forcing a conflict would have cost the merge and gained the
store nothing.

**Why this pass could not see the collision, which is the reusable part.**
Every in-flight guard matches an id against a **commit subject**, and this
pass's commits lead with `PL-Q0J1, PL-85NT` - the ids it *closes*. The four
items it merely triaged appear nowhere in any subject, so `bin/docket flight`
and `bin/docket show` reported this branch as carrying none of them, while the
other session's commits lead with `PL-2M4X, PL-SYG4` and were visible
immediately. A triage pass therefore makes its own work invisible by following
the leading-id rule exactly as written: the rule names what a commit *closes*,
and triage closes nothing.

That is `PL-99YZ`'s mechanism - *"filing first makes you visible; it does not
make you look"* - arriving one level down, and `PL-85NT` (dropped in this same
pass as superseded by `PL-99YZ`) is the item about it. This instance is
sharper than either, because nothing was overlooked: both sessions followed the
rules and the guard still could not see one of them. Recorded here rather than
filed as a new item, since `PL-99YZ` is open, `ready`, and is where the
decision about detectors belongs.

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-4BCF`).** `ROADMAP.md`'s § "Completed: v0.5.0 - the case you can branch" carried this under § "Declined to Gate 2 on the refilling-queue ground", Gate 1's record of how it disposed of debt it did not hold. In it, "this gate", "the gate" and "the list" are Gate 1, v0.5.0's frozen list; "this milestone" is v0.5.0; "the freeze" is Gate 1's freeze on 2026-09-06; "this section" and "this subsection" are that heading's section; "the first twenty-nine" are the 2026-09-08 group that opened the section, and "the first thirty" are those with `PL-HX5C`; "today" is the day the paragraph was written; and "above" and "below" point within `ROADMAP.md` as it then stood. This item is not one the section disposed of, and the section no longer names it. Its paragraphs also dispose of entries that they count without naming: `PL-L4KX` and `PL-PGZF`.

> **Two more from the 2026-09-16 evening triage pass over the six captures open that day** (`PL-Q0J1`). The six arrived during the day from four sessions, after `PL-0C6W` cleared that morning's fourteen. Two are not debt. `PL-85NT` was dropped, and `PL-M3YJ` is `infra`, which "What counts" says explicitly is not debt. Two others, `PL-2M4X` and `PL-SYG4`, were triaged at the same time on `claude/pl-syg4-pl-2m4x-triage`. That branch disposes of them higher in this subsection, so they are not disposed of a second time here. That leaves two.
