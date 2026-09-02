---
id: PL-30P6
title: ACCENT is used as text and fails WCAG AA in both places it appears
priority: P2
effort: S
status: done
classes: defect, ux
feature: presentation-safety
milestone: v0.2.10
touches: src/anesthesia_sim/app/theme.py, src/anesthesia_sim/app/simulation_view.py, tools/contrast_check.py, tests/unit/test_simulation_view.py, tests/unit/test_contrast_check.py, docs/MODEL.md
added: 2026-09-02
closed: 2026-09-02
pr: 190
verify: uv run pytest tests/unit/test_contrast_check.py tests/unit/test_simulation_view.py && grep -q 'ACCENT_TEXT' src/anesthesia_sim/app/theme.py
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

**Resolved by route 1 (2026-09-02).** `ACCENT_TEXT = "#127D71"` is a uniform
darkening of `ACCENT`, so hue and saturation are unchanged (173 deg, 0.86) and
the two read as one colour family. It measures **5.00:1** on `PANEL` and
**4.65:1** on `BACKGROUND`. The two affirmative status words now use it;
`ACCENT` keeps only its graphical roles.

Two things found while doing it.

**The "Valid" word is large text, and the stricter bar was applied anyway.** It
renders at 20px bold (`simulation_view.py:208`), past WCAG's 14pt-bold
threshold, so SC 1.4.3's 3:1 large-text figure would have sufficed - and
`ACCENT` failed even that, at 2.93:1. Holding it to 4.5:1 keeps
`docs/MODEL.md`'s statement true that the large-text exception is not claimed
anywhere in this interface, and costs nothing since the new value clears it.

**`ACCENT` had a third role, not two.** Besides the alveolar trace it colours
the active track and thumb of all four parameter sliders
(`:320`, `:336`, `:346`, `:356`) - a user-interface component under SC 1.4.11,
also at 2.93:1 against 3:1. That is `PL-W8DQ`, captured rather than fixed here
because the right value depends on whether `PL-GVXP` keeps `ACCENT` as the
alveolar trace. So the constant was carrying a text role at 4.5:1, a trace role
at 3:1 and a control role at 3:1, and no single value satisfies all three -
which is the argument for the split, arriving after the split was chosen.

`tools/contrast_check.py` now lists `ACCENT` twice with the same measured value
and two different owners. That is deliberate: the trace and the slider track are
separate elements sharing one constant, and separate entries are what make the
sharing visible instead of hiding it behind a single row.
