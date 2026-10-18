---
id: PL-KXTL
title: Ship the three default Workspaces - the central-graph default, induction, and big-picture maintenance - as validated versioned JSON beside the other shipped parameter files
priority: P2
effort: S
status: done
classes: feature
feature: interface-areas
touches: src/anesthesia_sim/data/, src/anesthesia_sim/layout/shipped.py, src/anesthesia_sim/layout/exceptions.py, src/anesthesia_sim/layout/__init__.py, src/anesthesia_sim/layout/store.py, tests/unit, docs/ARCHITECTURE.md, ROADMAP.md, tools/doc_check.py, tools/source_tier_counts.py
blocked-by: PL-WV9K, PL-SSQW
added: 2026-09-16
closed: 2026-10-18
pr: 1584
payoff: the three shipped Workspaces are validated JSON under data/workspaces/ that a first run loads through the reader's own reader, each carrying the provenance line the interface record asks for
verify: grep -q 'shipped:default' src/anesthesia_sim/data/workspaces/default.json
---

**Problem.** Ship the three default Workspaces - the central-graph default, induction, and big-picture maintenance - as validated versioned JSON beside the other shipped parameter files

**Why it matters.** Item 34 asks for task-oriented presets by example - an
induction Workspace with the concentration graph zoomed in, a big-picture
Workspace to switch to during maintenance - and a default with a central graph
of the compartments and the other Views around it. They are also what a
learner's "reset" restores to, and what Blender's refusal to delete the last
Workspace needs in order to have something to fall back on.

**Done when.** The three ship as validated versioned JSON beside the other
parameter files under `src/anesthesia_sim/data/`, load through the same path a
learner's own Workspaces do, round-trip under test, and carry the provenance
line `docs/interface-provenance.md` asks of anything modelled on Blender's own
named task Workspaces.

*Scope.* `ROADMAP.md` § "v0.6.0 - the layout is the reader's" -> "Required
scope" item 13.

**The accounting View is not in the shipped defaults** (project owner,
2026-09-16). Asked whether the agent-accounting panel should report liquid
millilitres, the owner's position was that "the info on the panel is not info
the user really needs or cares to see. At most, we could turn it into an
optional area widget a user could add back down the road." Stated tentatively
and recorded as stated, but it agrees with `docs/MODEL.md` § "Reachable rather
than simultaneously visible", which already puts the accounting in the one
required tier "a layout may leave them out", so nothing in that document needs
to change for it.

**Consequence for these three Workspaces:** none of the central-graph default,
induction or big-picture maintenance presets names the accounting View. It
is reached through the chooser (`PL-50PZ`) instead.

**It cannot be acted on before `PL-50PZ`.** The panel is structurally present
in today's single dashboard, so removing it from the default view before the
chooser exists would make it unreachable and violate the tier's second half —
"must not be removable from the application". The order is the chooser first,
then the defaults that omit it.

## Built 2026-10-18

The three files are `src/anesthesia_sim/data/workspaces/{default,induction,maintenance}.json`,
read by `layout/shipped.py`. Each is a Workspace set document holding one
Workspace, so it goes through `workspace_set_from_json`, the reader the
learner's `workspaces.json` goes through, and each round-trips byte for byte
under test. Two parts of the Done when landed in a different place than the
brief named, both decided here:

- **The provenance line is in `data/workspaces/__init__.py`, beside the
  files, rather than in each file.** The reader refuses any key the schema
  does not have (`PL-SSQW` Q5), and a provenance field in the schema would sit
  on every Workspace a learner saves, where it would say something false.
- **The Induction zoom is `PL-L59K`.** A zoom is the chart's own saved state,
  whose form the View contract decides (`PL-TH35` Q4), so it is added once
  that exists.

The arrangement of each Workspace is a learner-visible choice the ratified
decisions constrain but do not settle, so it was put to the project owner on
2026-10-18 with a recommendation, and the pull request waits for the answer.
The question is whether the Default leaves the wash-in chart out: on the
1366 px laptop the budget `PL-84QX` set leaves no height for it under the
chart. **Recommended: leave it out.** The Default shows the chart and the
parameter controls, Induction stacks the chart over wash-in beside the
controls, and Maintenance puts the chart across the top with wash-in and the
controls below.

**Answered 2026-10-18:** the Default leaves the wash-in chart out (project
owner, 2026-10-18, ratified, on the decision card, over a third column beside
the controls and over wash-in below the chart).

The View kind tags the files name - `concentration_chart`, `wash_in` and
`parameter_controls` - are not registered yet. `PL-R1WQ` Q4's test, which
asserts every shipped tag is registered, lands with the registry.

`tools/doc_check.py` and `tools/source_tier_counts.py` read every JSON file
under `data/` as a parameter file, and refused the three Workspace files for
having no `sources` and no provenance-table rows. Both now read the parameter
files through one function, `doc_check.parameter_data_files`, which leaves out
the subdirectories `NON_PARAMETER_DATA_DIRS` names: `workspaces`, which holds
layout fractions and ids and no value a clinician could read.
