---
id: PL-30P6
title: ACCENT is used as text and fails WCAG AA in both places it appears
priority: P2
effort: S
status: needs-decision
classes: defect, ux
feature: presentation-safety
touches: src/anesthesia_sim/app/theme.py, src/anesthesia_sim/app/simulation_view.py, tools/contrast_check.py, tests/unit/test_simulation_view.py, docs/MODEL.md
added: 2026-09-02
---

**Problem.** `ACCENT` (`#18A999`) is used as a *text* colour in two places, and
fails WCAG 2.2 SC 1.4.3 in both:

- the run-status text when the run is active - the word "Running"
  (`app/simulation_view.py:681`), on the page background: **2.72:1**;
- the agent-accounting status when conservation holds - the word "Valid"
  (`:730`), on a panel: **2.93:1**.

Against a 4.5:1 minimum, and both are below even the 3:1 large-text figure,
which does not apply here anyway (Flet's default text size is 14px).
`tests/unit/test_simulation_view.py:351` and `:383` pin both usages, so this is
current behaviour rather than a stale path.

**Why it matters.** These two words are the interface's entire "everything is
fine" signal, and they are the ones a reader checks fastest and least
carefully. "Running" is also half of the pair that `docs/MODEL.md` treats as
safety-critical - distinguishing a running from a halted run is what stops a
reader trusting numbers that have stopped advancing - so the state most likely
to be misread is the one rendered least legibly. `PL-018` made the halted state
loud; the running state stayed quiet.

**Decision needed.** `ACCENT` cannot simply be darkened, because it has a
second, unrelated job: it is `ALVEOLAR_COLOR`, one of the six chart traces
(`:109`), where it is a graphical object held to 3:1 and owned by `PL-GVXP`.
One constant currently serves two roles with two different contrast bars. Three
routes:

1. **Add a text-safe token** (`ACCENT_TEXT` or similar) for the two status
   words, leaving `ACCENT` to the chart. Smallest change, and it makes the
   role split explicit - recommended, but it adds a constant, which
   `ROADMAP.md` item 24 (consolidate the scattered display constants) will want
   to know about.
2. **Darken `ACCENT` itself** to clear 4.5:1 and let the trace inherit it. One
   constant, but it pre-empts `PL-GVXP`'s palette work and changes the chart
   without that item's analysis.
3. **Stop using colour alone for the status word** and lean on the text itself,
   which already differs ("Running" / "Paused" / "Stopped — simulation error").
   Cheapest, but it gives up a cue rather than fixing it.

**Where.** `app/theme.py:9` (`ACCENT`); `app/simulation_view.py:681`, `:730`;
`tools/contrast_check.py`'s `KNOWN_SHORTFALLS` (the `ACCENT` entries, which
must go in the same change); `tests/unit/test_simulation_view.py:351`, `:383`.

**Done when.** Both status words meet 4.5:1 on the surface they are actually
drawn on, the chart trace's own requirement is unchanged or explicitly handed
to `PL-GVXP`, and the `KNOWN_SHORTFALLS` entries are deleted.
