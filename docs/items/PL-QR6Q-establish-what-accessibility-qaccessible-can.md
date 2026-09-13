---
id: PL-QR6Q
title: Establish what accessibility QAccessible can deliver, and settle ROADMAP item 20 against it
status: blocked
blocked-by: v0.5.1, PL-25KS
priority: P3
effort: M
classes: planning
feature: presentation-safety
touches: ROADMAP.md, src/anesthesia_sim/app
added: 2026-09-13
---

**Problem.** Establish what accessibility QAccessible can deliver, and settle
ROADMAP item 20 against it.

`ROADMAP.md` (Phase 2, item 20) commits to "keyboard navigation, contrast,
screen-reader support, color-vision-safe encodings". Contrast and colour-vision
encodings are ours and are covered by `PL-MMYM`, `PL-1MK1` and `PL-GVXP`.
Keyboard navigation and screen-reader support are the toolkit's, and nobody has
established what this project's toolkit exposes.

**Why it matters.** It bounds a roadmap commitment that is already written
down, and it is cheaper to bound before Phase 2 builds controls on top of it
than during. If the backend cannot deliver usable screen-reader semantics for
the readouts and the chart, the honest responses are to narrow item 20, to add a
non-visual route to the same values, or to accept the limit and say so — and all
three are decisions about a promise this project has made, not about a toolkit.
It also carries a safety edge the contrast items do not: a readout announced
without its units is `CLAUDE.md`'s "correct number with the wrong units", which
that standard calls a safety failure rather than an accessibility gap.

**Why it is this item and not `PL-F0L8`.** `PL-F0L8` asked the same question of
Flet, and was `dropped` on 2026-09-13 because `v0.5.1` replaces Flet with
PySide6 + pyqtgraph. `ROADMAP.md` § "Items this port moots or transforms" states
the reason in its own words: "After the port the question is `QAccessible`'s,
which is a different investigation against a different backend." This item is
the surviving half — the roadmap commitment, which no toolkit change retires —
re-pointed at the backend that will actually ship it.

**Why the backend answer differs, which is why this is not a re-run.** Flet
renders through Flutter, which draws to a canvas and synthesises a semantics
layer rather than emitting a native accessibility tree. Qt exposes `QAccessible`,
a native accessibility interface that bridges to the platform API (UI Automation,
AT-SPI, NSAccessibility). Those are different enough that a finding against one
says nothing about the other, which is the whole reason the Flet investigation
was not worth running.

**Approach.** Against current Qt documentation and a hands-on check of the
ported app, not from memory:

1. What the numeric readouts expose to a screen reader, and whether each is
   announced with its units and its model identity. The units half is the
   safety-critical half: a value announced without them is
   `CLAUDE.md`'s "correct number with the wrong units".
2. Whether the controls are keyboard-reachable and focus-visible in tab order,
   and what WCAG 2.2 SC 2.4.7 and 2.4.11 would require of them.
3. What `pyqtgraph`'s chart exposes, and whether a non-visual equivalent — a
   text summary, an exportable table — is the realistic answer rather than
   making the plot canvas itself accessible. The chart is the one surface where
   this is likely, and it is also where `docs/MODEL.md`'s decimation rule means
   a table is not simply the same data.

Then either narrow `ROADMAP.md` item 20 to what is achievable, or file the items
that close the gap.

**Blocked rather than ready, on the version and on the item**, which is the
`blocked-by: v0.5.1, PL-25KS` pattern `ROADMAP.md` § "Sequenced past v0.5.0"
already uses for the five defects the port carries. Both halves are needed and
the version alone is not enough: `blocked-by: <version>` resolves as soon as
that milestone is *scoped*, and `v0.5.1` is scoped already, so on the version
alone `docket check` correctly advises promoting this to `ready` — which would
put a question that cannot be asked yet in front of `bin/docket next`. `PL-25KS`
(port the dashboard to PySide6 — the readout row, the controls, the transport,
the dialogs) is the item whose completion actually makes the three questions
answerable, and it is `ready` rather than done, so the edge holds.

**Not a Gate 1 entry.** Captured 2026-09-13, after that gate was frozen, and it
is `planning`-classed rather than debt. It is neither a deferral of `PL-F0L8`
nor a renegotiation of the freeze — `PL-F0L8` is `dropped` with its reason
recorded, which is a disposition the gate's definition of done allows outright.

**Done when.** `ROADMAP.md` item 20 states what is achievable on the shipped
toolkit rather than what would be ideal, and the reasoning is recorded where a
later session finds it before re-asking.
