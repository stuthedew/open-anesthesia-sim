---
id: PL-SXBQ
title: "Cut v0.4.17: the release where core/ said what it meant"
priority: P2
effort: S
status: done
classes: planning, docs
feature: release-process
milestone: v0.4.18
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases, docs/items/
added: 2026-09-13
closed: 2026-09-13
pr: 517
verify: python3 tools/doc_check.py check && grep -q '^version = "0.4.17"' pyproject.toml && test -f docs/releases/v0.4.17.md
---

**The cut.** Eleven finished items since 0.4.16, one of which is the v0.4.16
cut itself. A patch by the ordinary rule under `ROADMAP.md`'s "Versioning
decision": it crosses no capability boundary, and the simulator does nothing it
could not do before.

**That claim is measured here rather than asserted**, and it is stronger than
the last two releases could make it:

- `src/anesthesia_sim/data/` and `.github/` resolve to the same tree objects as
  at `v0.4.16`, so no stored parameter and no CI gate changed.
- Every reference test carrying a pinned published or canonical value is
  byte-identical to `v0.4.16` and still passes:
  `tests/reference/test_canonical_evaluation.py`,
  `tests/reference/test_coupled_dynamics.py`,
  `tests/reference/test_published_wash_in_and_elimination.py`,
  `tests/reference/test_circuit_wash_in.py`,
  `tests/reference/test_multi_agent.py`,
  `tests/reference/test_control_resolution.py`.
- Read line by line, every executable change under `core/` and `app/` is one of
  three things: a type annotation erased at runtime, a hand-written `* 100.0`
  or `/ 100.0` replaced by a named conversion defined as exactly that, or the
  deletion of a method nothing called.

So no equation, parameter, unit, numerical method, solver step or displayed
value moved.

**What is in it.** Four Gate 1 `needs-decision` entries about the core's own
vocabulary (`PL-74R0`, `PL-79YX`, `PL-WVSK`, `PL-8GV5`), the routing fix that
followed the fourth being answered by a session rather than by the project
owner (`PL-4T90`), a duplicate that had turned `main` red (`PL-1YDK`), and five
apparatus items that landed in #513 and #515. `ROADMAP.md`'s baseline section
carries the prose.

**Done when.** `pyproject.toml` and `uv.lock` read 0.4.17,
`docs/releases/v0.4.17.md` exists, `ROADMAP.md` carries the version-table row
with the baseline mark moved onto it and a baseline section naming v0.4.17, and
`make check` is green. The tag is pushed by the project owner after the merge,
per the handover below.

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.4.17 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item.

> Four Gate 1 `needs-decision` entries, all of them about the core's own vocabulary rather than its arithmetic, and **no number the model produces moves**: `src/anesthesia_sim/data/` and `.github/` are byte-identical to `v0.4.16`, and every reference test carrying a pinned published or canonical value - `test_canonical_evaluation.py`, `test_coupled_dynamics.py`, `test_published_wash_in_and_elimination.py`, `test_circuit_wash_in.py`, `test_multi_agent.py`, `test_control_resolution.py` - is byte-identical too and still passes. Every executable line that changed is a type annotation erased at runtime, or a hand-written `* 100.0` replaced by an identically-defined named conversion, or the deletion of a method with no caller. **Three of the four decisions were settled by a measurement that changed the answer the brief expected.** `PL-74R0` asked which of five public `advance` methods should survive the exact step that replaced the operator split: one 60 s step against six hundred 0.1 s steps put the circuit, tissue and venous closed forms within 1.1e-14 of themselves and `PatientCompartments.advance` **25% apart**, which is not a closed form at all but the first-order split `PL-GS5X` deleted, kept alive as a public method with no error bound and a docstring giving a reader nothing to suspect. It is gone; the three exact ones stay, documented, and the criterion deciding them was already written in `alveolar.py` - nothing outside the governing equations may move agent between two modelled compartments. `PL-79YX` asked whether six `== 0.0` guards deserved any words: they turned out to be **three different arguments**, two of them load-bearing rather than stylistic - `V/0.0` raises in Python, and the circuit's exhausted-agent integral is `inf * 0.0` and therefore `nan` at zero flow for every state - while the item's own 2026-09-02 walk had been run at a loaded fraction where the third argument is invisible, so deleting either `advance` guard had been leaving the whole suite green. `PL-WVSK` asked whether a concentration fraction and a percent should differ at the type level, against a brief naming two implicit conversions: there were **twelve**, across six modules, six of them on the path to a displayed clinical value, and `docs/MODEL.md` had been asserting that "the interface alone converts" since the agent files began carrying a MAC. `core/concentration.py` now owns the factor and both directions, with `Fraction` and `Percent` as `NewType`s whose limits are documented rather than implied - erased at runtime, useless against a wrong magnitude, and unable to reach inside the equations at all, since `Fraction(0.5) * 2.0` is a plain `float`. **The fourth was the project owner's and a session took it.** `PL-8GV5` asked whether `ROADMAP.md` should carry intent for a dose-dependent haemodynamic response; the session measured the human volunteer literature - cardiac index unchanged under desflurane alone, falling dose-dependently in the same volunteers with nitrous oxide, and falling then returning to baseline at 2.0 MAC under sevoflurane - and then closed the item on that measurement. Whether a feature enters the roadmap is direction, not fact. The owner's answer was different and better: not now, and kept as **planned item 35, an option a user turns on**, because an overlay can state the uncertainty those three studies describe where a default behaviour cannot. `PL-4T90` is the routing gap fixed in the same session - the `docket` skill now sorts a `needs-decision` item by what its answer rests on rather than by how hard it looks. Eleven items, one of which is the v0.4.16 cut itself, and one of which - `PL-1YDK` - was a duplicate of `PL-8PT6` that had turned `main` red by passing its own `verify:` command.
