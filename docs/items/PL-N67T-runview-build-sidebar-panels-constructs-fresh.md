---
id: PL-N67T
title: RunView.build_sidebar_panels constructs fresh panels on every call and reparents the run's live labels into them, so a second call silently strips the accounting and control-change panels out of the sidebar
status: untriaged
feature: sidebar-panel-rebuild
added: 2026-09-21
---

**Problem.** RunView.build_sidebar_panels constructs fresh panels on every call and reparents the run's live labels into them, so a second call silently strips the accounting and control-change panels out of the sidebar

**Measured 2026-09-21** while implementing `PL-C3GS`, against a shown
`SimulationView` over one run. After a second `run.build_sidebar_panels()`:
`run._agent_accounting_status_text.parent()` is a different widget, the new
panel's own `parent()` is `None`, `view.isAncestorOf(panel)` is `False`, and
`run._agent_accounting_status_text.isVisible()` is `False`. So the call does
not merely waste two frames - it moves the run's live labels into an orphan
and leaves the sidebar on screen empty of them.

**Why it matters.** The method reads as a getter and every other `build_*`
call site treats it as one. `SimulationView._place_run` calls it once, so the
running application is unaffected today; what it costs is a caller who cannot
see from the name that calling it twice dismantles the display, which is how
`PL-JS0X`'s vacuous assertions arrived.

**Fix, not yet decided.** Either return the panels built at construction, or
raise on a second call. The first makes the name honest; the second makes the
misuse loud. Both are cheap; which is right depends on whether a panel is ever
meant to be rebuilt for a relaid-out area (`.claude/rules/ui-areas.md`).
