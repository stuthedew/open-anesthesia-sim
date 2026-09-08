---
id: PL-VLZT
title: Cut v0.4.10 - the release where the apparatus stopped being implicit
priority: P2
effort: S
status: done
classes: planning
feature: planning-cadence
touches: ROADMAP.md, pyproject.toml, uv.lock, docs/releases/v0.4.10.md, docs/items
added: 2026-09-08
closed: 2026-09-08
not-delegable: Proving a release cut means cutting the release; there is no command that can run beforehand and fail.
---

**Problem.** Cut v0.4.10 - the release where the apparatus stopped being implicit

**What it is for.** Twelve items finished since v0.4.9 and none of them moves a
stored value: `src/anesthesia_sim/data/` changes only in what its entries say
about their own numbers, and `core/` only in `circuit.py`'s docstrings. What
they have in common is the apparatus around the model - what a flow number
counts (`PL-CXYT`, `PL-71CF`), at what altitude and on which class of vaporizer
(`PL-5K5C`), through which breathing circuit (`PL-W21J`, `PL-73G7`), under
which identity the interface shows it (`PL-61WW`, `PL-97VB`), and out of which
book each parameter came (`PL-7HDS`, `PL-X19T`, `PL-J302`) - each of which was
already true and stated nowhere its reader would meet it. `PL-KTKP` closes
beside them.

**The one displayed change** is `PL-71CF`'s second label line under the
fresh-gas-flow control, which is the reason this is a release rather than a
docs pass: a user reading that control as a flowmeter mis-sizes the circuit
time constant by up to 22% at desflurane's dial maximum.

**Filed before the work under `CLAUDE.md`'s housekeeping rule**, which requires
repository work no item names to carry an id before it starts, because every
in-flight guard this project has matches a `PL-` id.

