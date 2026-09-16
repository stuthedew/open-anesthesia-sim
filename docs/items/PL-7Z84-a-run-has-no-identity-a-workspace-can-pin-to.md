---
id: PL-7Z84
title: A run has no identity a workspace can pin to - the dashboard addresses runs by their position in its own drawing order, and ROADMAP item 34 commits a workspace to pinning which run it shows
priority: P2
effort: M
status: blocked
classes: safety, anticipated
feature: interface-areas
blocked-by: PL-NMTF
touches: src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/dashboard_frame.py, docs/MODEL.md
added: 2026-09-16
---

**Problem.** A run has no identity a workspace can pin to - the dashboard addresses runs by their position in its own drawing order, and ROADMAP item 34 commits a workspace to pinning which run it shows

**Problem.** Nothing enumerates what a saved workspace holds beyond the layout tree, and the one member `ROADMAP.md` item 34 has already committed to cannot be written down today. A run is named by where it sits: `run_label(run_index)` in `src/anesthesia_sim/app/dashboard_frame.py:1179` is documented as "the one place a run is named", and `src/anesthesia_sim/app/simulation_view.py:225` calls it with the run's index in `self._runs`. There is no run id, no stable handle, nothing that survives a restart or a change in run order. So a workspace can record "the second run" and nothing else, and "the second run" names a different patient the moment a run is added, removed or reordered.

**Why it matters.** A workspace that restores a pin by position points at whatever run now occupies that slot, while the interface presents it as the run the workspace remembers. That is the correct number under the wrong patient, which `docs/MODEL.md` § "Minimum displayed outputs" treats as a display failure rather than a missing convenience, and it is the same class of silent substitution that `docs/interface-provenance.md` refuses Blender's answer for on the view-kind side. The break-out window inherits it directly: item 34 wants an area taken into its own top-level window and `PL-WLWY` requires that window to name its run, which is unanswerable while the run's name is a function of a position in a window it is no longer in. The pinning question is also what settles whether a run is part of the workspace's saved state or part of the session's, which decides what a workspace switch does to a run in progress — a question the layout code has to answer before it can switch a tab.

**Done when.** The workspace record's members are enumerated, distinguishing what it saves (layout tree, per-pane view state, pinned run) from what it does not; a run carries an identity stable across serialization and independent of its position, with `run_label` reduced to a display rendering of it; and the behaviour when a workspace's pinned run is absent on load is decided and tested, with a fallback to another run explicitly ruled out.

*Basis (lens `persistence`).* `ROADMAP.md` planned-milestone item 34: "And a workspace carries *settings*, not only a layout: Pin Scene makes activating a workspace switch back to the scene it remembers. The analogue here is a workspace pinning which **run** it shows, which is exactly what a broken-out window naming its run needs." `docs/interface-provenance.md` § "Adopted" records the same point as the reason the two-level split was taken at all: "Item 34 already wants a workspace to pin which **run** it shows... If a workspace were only a layout there would be nowhere to put that."

**Problem.** `ROADMAP.md` item 34 adopts Blender's Pin Scene as the precedent for a workspace carrying settings, and names the analogue: a workspace pinning which run it shows. There is nothing to pin to. In `src/anesthesia_sim/app/simulation_view.py:225` a run's name is assigned by the dashboard from its position in the tuple, and only when there is more than one:

```python
for index, run in enumerate(self._runs):
    run.set_run_name(run_label(index) if len(self._runs) > 1 else None)
```

So a run's identity today is *index in this dashboard's drawing order*, held by the widget that lays the runs out, and `None` whenever a run is shown alone. Neither property survives what item 34 introduces: a workspace that remembers a run across a layout change, a second workspace showing a different run, or a broken-out window holding one run on another monitor.

**Why it matters.** This is a presentation-correctness case under `CLAUDE.md`'s safety-critical standard rather than a modelling convenience - the correct number under the wrong patient context is a display failure, and a pin that resolves to the wrong run is exactly that, arriving silently. `docs/MODEL.md` already carries the compare-mode rule - "While two runs are shown, every readout names the run it describes" (~line 4886), with "The run is named in text, not carried by colour or by position" - but that rule is written against one dashboard showing two runs and is expressed in terms of the run *count*. The case that most needs a name is the one the count switches off: `PL-WLWY` records that "a broken-out window on a second monitor is the strongest form of position carrying meaning", and today that window's single run would be named `None`.

**Done when.** A run carries a stable identity that does not depend on drawing order or on how many runs are displayed; the rule for when a view names its run is restated in `docs/MODEL.md` in terms of that identity rather than of run count, so that a single run alone in an area or a window is covered; and the workspace model records the pinned run by that identity, with a defined and visible behaviour when the pinned run no longer exists rather than a fall back to whichever run is first.

*Basis (lens `layout-ops`).* ROADMAP.md item 34: "And a workspace carries *settings*, not only a layout: Pin Scene makes activating a workspace switch back to the scene it remembers. The analogue here is a workspace pinning which **run** it shows, which is exactly what a broken-out window naming its run needs."

## Area-model audit (PL-BNYF)

**Disposition: `missing-prereq`.** Filed 2026-09-16 by the area-model queue audit (`PL-BNYF`), which swept 49 open and untriaged items and seven gap lenses against `ROADMAP.md` item 34, `docs/interface-provenance.md` and `.claude/rules/ui-areas.md`. Each candidate was checked against the store before it was filed, so a gap an existing item already covers is not here.
