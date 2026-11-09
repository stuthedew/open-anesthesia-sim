---
id: PL-G1J9
title: docs/ARCHITECTURE.md § 'Layering' says app/ never performs a unit calculation, but § 'Data flow' and the package map say chart_frame.py, formatting.py and agent_cost.py convert units; one statement is wrong (copy editor structure read, 2026-11-05)
priority: P2
effort: S
status: ready
classes: defect, docs
feature: architecture-md-structure
touches: docs/ARCHITECTURE.md
added: 2026-11-05
payoff: a reviewer tracing a displayed value from the model to the screen is told which app/ modules convert units, and finds every step of the path
verify: ! grep -qF 'or unit calculation itself' docs/ARCHITECTURE.md
reenters: PL-4FBP
---

**Problem.** docs/ARCHITECTURE.md § 'Layering' says app/ never performs a unit calculation, but § 'Data flow' and the package map say chart_frame.py, formatting.py and agent_cost.py convert units; one statement is wrong (copy editor structure read, 2026-11-05)

**The structure read's query** (row numbers are docs/ARCHITECTURE.md at cfb15a4a, before the line edit):

- **Query, calculation in `app/`.** The file contradicts itself, and the statements stay as they are. Layering 29-32 says `app/` "never performs a physiological or unit calculation" and "only reads immutable snapshots". Against that:
  - Data flow 532-543 says `chart_frame.py` "converts each drawn value into the unit of its own axis".
  - Data flow 317-331 says `formatting.py` turns a fraction into a percent.
  - Package map 126 says `agent_cost.py` converts the delivered agent into millilitres of liquid.
  - Data flow 308-315 and Where new code belongs 1203-1236 say the views also read `drawn_window`.

**Checked 2026-11-09:** `grep -n 'or unit calculation itself' docs/ARCHITECTURE.md` still finds § "Layering": `app/` "never performs a physiological or unit calculation itself. It only reads immutable snapshots from `core/`". The code does not match that sentence, and the other sections are right. `app/formatting.py` turns a fraction into a percent and defines `mac_multiple`, which divides a fraction by the agent's MAC. `app/chart_frame.py` converts each drawn value into its axis unit. `app/agent_cost.py` takes the liquid volume from `core.liquid_agent.liquid_volume_ml` and multiplies it by the reader's price. The views also read `SimulationController.drawn_window`, not only snapshots. `.claude/rules/ui-calculations.md` already draws the line the code follows: no model quantity is computed in a callback, and a presentation transformation lives in a module that loads no toolkit and has its own tests.

**Why it matters.** A contributor who trusts § "Layering" will not look in `app/` for the code that turns a fraction into a percent or a MAC multiple. A reviewer checking the path from a model value to a displayed number needs to find every step of it.

**Done when.** § "Layering" states the line the code keeps. `app/` computes no model quantity, and each unit or display conversion it makes sits in a named module that loads no toolkit and has its own tests (`formatting.py`, `chart_frame.py`, `agent_cost.py`). It also says that the chart reads `drawn_window` as well as snapshots.

**Generator check.** Instance of `PL-4FBP`'s fact, "The link between a document sentence and the tree fact it restates": the sentence states a tree fact that the code has since moved past, and no check holds a `docs/ARCHITECTURE.md` sentence to the code.

**Checked 2026-11-09 against the tree at the freeze (`PL-GW0P`).** `git show 817a4d88:docs/ARCHITECTURE.md` already says that `app/` never performs a "unit calculation itself" (row 28), while that tree's `app/formatting.py` already defines `mac_multiple`. So the problem was present at the freeze, commit `817a4d88` (2026-10-24), and this finding belongs on v0.7.0's frozen list rather than deferred.
