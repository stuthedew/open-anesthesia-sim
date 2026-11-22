---
id: PL-S6CP
title: The concentration chart's least height of 280 px was measured with the offscreen font and no advisory, so in an Area held at that height (Induction at 1366 by 768) an off-scale, capped-trace or hidden-trace advisory, or a desktop font taller than the offscreen one, pushes the bottom of the plot and its time axis below the Area's edge until the learner scrolls; decide whether the chart's need follows the View's own layout, so the Areas move when an advisory appears, or stays a fixed number, so the plot scrolls
priority: P2
effort: S
status: done
classes: ux, defect
feature: window-is-the-frame
milestone: v0.6.20
touches: src/anesthesia_sim/app/view_registry.py, src/anesthesia_sim/app/views.py, tests/integration/test_layout_safety.py
deferred-from: v0.7.0 - a new problem: #2134 (PL-CBYS, 2026-11-13) set the 280 px least height after the freeze; at 0947408 the chart's least height was 300 px and the page scrolled instead
added: 2026-11-14
closed: 2026-11-22
pr: 2226
payoff: A learner reading the concentration chart in a short Area never loses its time axis and its lowest traces without being shown it.
tests: tests/integration/simulation_view/test_simulation_view_page.py::test_an_advisory_above_the_concentration_plot_grows_its_area_and_keeps_the_plot_whole
---

**Problem.** The concentration chart's least height of 280 px was measured with the offscreen font and no advisory, so in an Area held at that height (Induction at 1366 by 768) an off-scale, capped-trace or hidden-trace advisory, or a desktop font taller than the offscreen one, pushes the bottom of the plot and its time axis below the Area's edge until the learner scrolls; decide whether the chart's need follows the View's own layout, so the Areas move when an advisory appears, or stays a fixed number, so the plot scrolls

**Found by** both blind review passes on `PL-CBYS`'s pull request `#2134`, on
2026-11-14. `_CHART_LEAST_HEIGHT_PX` in `app/view_registry.py` is 280 px: the
View's heading, the first two rows of its key box and the plot at its least
160 px, measured at 275 px with the offscreen font. The advisories sit outside
the key box, above the plot, so each one shown adds its height to what the
View needs. The View then scrolls inside its Area by that height, and the
bottom of the plot, with the time axis and the traces near zero, is below the
Area's edge. The constant is also a second copy of a fact the View's own layout
holds, and it is right only for the font it was measured with.

**Why it was not fixed on `#2134`.** Each fix is a choice between two
behaviours a learner sees. If the chart's need follows the View's own least
height, the plot always stays whole, but the Areas move each time an advisory
appears or clears, and the wash-in Area below gives up the room. If the need
stays a fixed number, the layout is stable, but the plot's bottom scrolls out
of view while an advisory is shown.

**A second case, from the adversarial review on 2026-11-14.** Taking a fork in
Induction at 1366 by 768 adds a second run, and the advisory that the chart
draws at most two compartments per run appears outside the key box (30 px).
The View's content becomes 311 px in the same 280 px Area, the plot sits at
y 137 to 297, and its bottom 17 px are scrolled out of view.

**Checked 2026-11-22**, at `d4e8200c`. `grep -n "_CHART_LEAST_HEIGHT_PX" src/anesthesia_sim/app/view_registry.py` still prints `_CHART_LEAST_HEIGHT_PX: Final = 280`, and the comment above it still says the figure was measured at 275 px with the offscreen font. At the freeze, `0947408`, the chart's least height was 300 px and the page scrolled instead, so this problem arrived with `#2134`.

**Why it matters.** The bottom of the concentration plot holds the time axis and the traces near zero, where the tissue curves start. While an advisory shows, a learner at the 1366 by 768 window sees a plot without that strip and with no sign of what is missing, other than a scroll bar inside the Area.

**Decision needed.** When an advisory or a second run's notice appears above the concentration plot, should the chart's Area grow so the plot stays whole, or keep its size so the plot scrolls? Either way the 280 px constant is a second copy of a height that the View's own layout already knows.

1. **The Area grows.** The chart's least height is read from the View's layout, so the plot always stays whole. The Areas move each time an advisory appears or clears, and the wash-in Area below gives up the room.
2. **The Area keeps its size.** The least height stays a fixed number, so the layout never moves. The bottom of the plot scrolls out of view while an advisory shows.
3. **The Area keeps room for the advisories all the time.** The least height is read from the View's layout with the advisory rows counted whether or not they show. The layout never moves and the plot never scrolls, but the wash-in Area is shorter by those rows even when no advisory shows.

**Recommendation:** option 3, if the shipped Workspaces still fit the 1366 by 768 window with the extra rows, and option 1 if they do not. A learner should not lose the plot's time axis without being told, and a layout that moves under the pointer is a hidden change of mode. Option 3 avoids both, and it removes the second copy of the height. The owner decides because each option changes what a learner sees of a required display.

**Done when.** The concentration chart's least height comes from the View's own layout rather than from a measured constant, and a test shows the chosen behaviour in Induction at 1366 by 768 with an advisory shown.

**Generator check.** A one-off. The misread fact is the chart View's least height, which its own layout holds and `#2134` copied into a constant measured once. `PL-16BG` and `PL-YJ21` name an Area's least size as it depends on its width and on Qt's pending layout requests, not on what the View shows, so neither head's fact covers it.

**Answered 2026-11-22 (project owner, 2026-11-22, ratified, over the Area growing or the plot scrolling).** The owner asked that each item needing him be settled by standard practice. The chart keeps room for its advisories all the time, option 3, and falls back to option 1 only if the shipped Workspaces do not fit the 1366 by 768 window with the extra rows. The standard practice is to reserve space in the first layout for content that appears later, so that nothing moves under the reader. web.dev's "Optimize Cumulative Layout Shift" (https://web.dev/articles/optimize-cls, read 2026-11-22) says that "layout shifts can be avoided by reserving the space for them in the initial layout", and calls unexpected shifts "visually jarring and frustrating", "throwing you off and requiring you to find your place again". The page is about web pages, but the hazard it names is the same in a desktop window: a moving layout is a hidden change of mode, and a learner should not lose the time axis without being shown it.

**Done when, as answered.** The concentration chart's least height is read from the View's own layout, with every advisory row counted whether or not it shows. A test in Induction at 1366 by 768 shows the plot whole and the Areas unmoved when an advisory and a second run's notice appear. If the shipped Workspaces do not fit with those rows, the test shows instead that the Area grows and the plot stays whole, and the brief records why.

**Documentation checked on 2026-11-22**, each passage that names a changed module, for a statement the change made untrue: `docs/ARCHITECTURE.md`, `docs/INTERFACE.md`, `docs/interface-provenance.md`, `ROADMAP.md` and `.claude/rules/ui-areas.md`. None needed a change.
