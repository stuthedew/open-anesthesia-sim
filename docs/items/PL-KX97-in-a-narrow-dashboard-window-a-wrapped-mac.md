---
id: PL-KX97
title: In a narrow dashboard window a wrapped MAC-target row is laid out below the height its wrap needs, so its second line - where a run's standing such as 'Run 2 reached' lands - is clipped: at 700x450 each row gets 13-14 of 30 px, at 700x1000 28 of 30 (found working PL-VCF0)
priority: P2
effort: M
status: done
classes: defect, ux
feature: presentation-safety
touches: tests/integration/test_simulation_view.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-12 triage pass
added: 2026-10-11
closed: 2026-10-19
pr: 1680
payoff: in a narrow window a mark row's second line, such as Run 2 reached, is shown or scrolled to rather than silently cut off
verify: grep -q 'def test_a_wrapped_mark_row_is_never_clipped' tests/integration/test_simulation_view.py
---

**Problem.** In a narrow dashboard window a wrapped MAC-target row is laid out below the height its wrap needs, so its second line - where a run's standing such as 'Run 2 reached' lands - is clipped: at 700x450 each row gets 13-14 of 30 px, at 700x1000 28 of 30 (found working PL-VCF0)

**Measured 2026-10-11** in a cloud container (sans-serif resolves to Inter),
offscreen, `SimulationView((controller,))` with eight MAC targets whose labels
wrap, each `MarkRow.text_label`'s height compared against its
`heightForWidth` at the width it was given:

| Window | Row text width | Row height / needed |
| --- | --- | --- |
| 1400x1000 | 1080 px | 15 / 15 - no row wraps |
| 700x1000 | 461 px | 28-29 / 30 |
| 700x450 | 461 px | 13-14 / 30 |

The scratch probe lives only in that session; rebuilding it is the test this
item asks for.

**Inferred, not traced.** The listing is a `QVBoxLayout` that honours its rows'
`heightForWidth`, but the page above it reaches the `QScrollArea` through a
`QSplitter` (`inert_splitter`), and a splitter reports no height-for-width, so
the page's minimum height is worked out at its size hint rather than at the
width the rows are given. The scroll area then has no reason to scroll, and the
rows absorb the shortfall. `PL-TZNM` (the agent-accounting panel laid out below
its size hint) is the same shape - a widget given less height than it asks
for, clipped silently - and may share the cause; whether one fix covers both is
for the session that traces it.

**Time-bookmark rows** are drawn by the same `MarkListingLabel`, so they are
expected to clip the same way; that half was not measured.

**Why it matters.** A mark row's second line is often the run's standing -
`Run 2 reached` - which `PL-FPY2` gave a row of its own so it could not be read
against the wrong mark. Clipped, it is not read at all, or is overdrawn by the
row's first line, and a reader narrowing the window gets no sign anything is
missing.

**Done when.** At any window size a wrapped mark row is given at least its
`heightForWidth`, the page scrolling where the window is too short, and a
rendering test of the dashboard built as `main()` builds it, at a width where
rows wrap, finds none clipped.

**Checked 2026-10-19.** No longer reproduced: at 700 by 450 and 700 by 1000 on the Every View Workspace no mark row is clipped, and the page now holds a 1115 px minimum width, so ordinary rows no longer wrap. No change here located the fix. `test_a_wrapped_mark_row_is_never_clipped` gives a mark a name long enough to wrap and pins the row's height to its `heightForWidth`; it passes on the code before this change (the `src/` of b1240300, the head of #1675) too, so it is a pinning test rather than a regression test.
