---
id: PL-GL5X
title: Load Factory Preferences needs shipped defaults to be a restorable artifact, but today's display defaults are Final constants in app/formatting.py with no factory state to return to
status: untriaged
feature: preferences-store
added: 2026-09-16
---

**Problem.** Load Factory Preferences needs shipped defaults to be a restorable artifact, but today's display defaults are Final constants in app/formatting.py with no factory state to return to

**What Blender's fourth menu entry needs.** "Load Factory Preferences"
restores a known factory state. Today this project's display defaults are
`Final` constants in `app/formatting.py` — `AGENT_VOLUME_DISPLAY_DECIMALS`,
`FLOW_DISPLAY_DECIMALS` and the rest — so there is no artifact to restore
*from*; a factory reset would have to reach into module state and re-derive
what the code already hardcodes.

**The pattern already exists in this repository.** `PL-KXTL` ships the three
default Workspaces "as validated versioned JSON beside the other shipped
parameter files" under `src/anesthesia_sim/data/`, loading "through the same
path a learner's own Workspaces do". Shipped default *preferences* want
exactly that treatment, and for the same reason: a default that loads by the
reader's own path is a default whose behaviour is tested by the reader's own
tests.

**The constraint that keeps it honest.** `CLAUDE.md` requires agent/model
parameters in validated, versioned data files and no executable equations in
data files, so a preference whose value is *derived* — display precision, per
`PL-0S0V` — stays a derivation in code with the data file carrying only what
the derivation is fed. The line is the same one `tools/doc_check.py` sits on:
the file states the inputs, the code states the rule.
