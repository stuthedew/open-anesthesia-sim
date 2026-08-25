---
id: PL-JD2P
title: Cover the module-level agent-color guard in `simulation_view.py`
status: untriaged
added: 2026-08-25
---

**Problem.** `app/simulation_view.py` line 109 raises
`RuntimeError("AGENT_COLOR_SCHEMES must define exactly the built-in volatile
agents")` at import time, and never executes under the test suite.

**Why it matters.** It is the guard that stops an agent shipping without its
ISO 5360 identification color, or a color without its agent - the provenance
chain PL-002 established. Untested, it can be broken silently.

**Why it is not in the pilot.** It was pulled out of PL-LHHG deliberately.
Covering a module-level raise means re-executing the module body with the
constant patched (`importlib.reload` plus a monkeypatched dict), and a
per-module `--cov-fail-under=100` gate is impossible on `simulation_view.py`
while thirteen Flet-construction lines remain uncovered. Both make it a poor
fit for a delegated worker: the technique is fiddly and the proof command
cannot be clean. Do it in an ordinary session.

**Done when.** The guard is exercised, or the reason it is left uncovered is
recorded here.
