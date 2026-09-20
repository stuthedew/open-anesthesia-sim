---
id: PL-GHMB
title: The marks dialog bounds the height control to the reference run's delivered ceiling, so while two runs are shown a height only the branch can reach cannot be marked
priority: P2
effort: S
status: dropped
classes: defect
feature: two-run-attribution
touches: src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/qt_widgets.py, tests/integration/test_simulation_view.py
added: 2026-09-20
closed: 2026-09-20
reason: refuted by measurement the day it was filed: the height control's ceiling is the agent's published maximum divided by the agent's MAC, both read once at construction, and two displayed runs are locked to one agent - so the trunk and a branch delivering 8.0% both reported 4.0 xMAC reachable
payoff: a learner comparing two managements can mark the height the two disagree about, which is the one the comparison is for
verify: grep -q 'def test_the_height_control_admits_a_height_only_the_branch_can_reach' tests/integration/test_simulation_view.py
---

**Problem.** The marks dialog bounds the height control to the reference run's delivered ceiling, so while two runs are shown a height only the branch can reach cannot be marked

**Refuted the same day it was filed, by measurement.** The ceiling is not a
per-run quantity at all. `BookmarkDialog.set_reachable_height` is handed
`mac_multiple(fraction_from_percent(max_delivered_concentration_percent),
agent_mac_percent)`, and both of those are the *agent's* published values,
read once in `SimulationController.__init__` from `agent_parameters` — not
the run's current delivered setting, which is what the title assumed. Two
displayed runs are locked to one agent three ways over
(`COMPARING_AGENT_LOCK_TEXT`, `BRANCH_AGENT_LOCK_TEXT`, and
`assemble_chart_frame` refusing a frame whose runs disagree), so the two
ceilings cannot differ.

Measured 2026-09-20 on a trunk paused at 60 s and a branch forked there with
its delivered concentration raised to 8.0%: both reported 4.0 xMAC reachable,
on agent `sevoflurane` with `max%` 8.0 each. Raising one run's delivered
concentration moves what it *will* reach and not what it *may be asked* to
reach, which is the quantity the control bounds.

So the reference-run read in `SimulationView._refresh_bookmarks` is sound at
that one site, and its docstring now says why rather than citing this item.

**Filed from the shape of the code rather than from a measurement** — "this
reads `snapshots[0]`, therefore it is the `PL-LHBY` defect again" — which is
the inference `.claude/skills/docket/modes/close-out.md` records a worked
instance of, a per-run holder widget said to cost the plots 18 px of spacing
and measured at 0 px. Dropped rather than left open: an item asserting a
defect that does not exist costs the session that starts it.
