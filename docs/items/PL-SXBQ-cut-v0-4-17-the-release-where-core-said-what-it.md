---
id: PL-SXBQ
title: "Cut v0.4.17: the release where core/ said what it meant"
priority: P2
effort: S
status: done
classes: planning, docs
feature: release-process
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
