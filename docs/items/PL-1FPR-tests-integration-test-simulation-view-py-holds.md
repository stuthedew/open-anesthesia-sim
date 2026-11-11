---
id: PL-1FPR
title: tests/integration/test_simulation_view.py holds 12,232 lines and 307 tests for a 2,193-line module, and tests/integration/test_controller.py holds 6,443 lines: split each by the behaviour it tests
status: untriaged
added: 2026-11-11
---

**Problem.** tests/integration/test_simulation_view.py holds 12,232 lines and 307 tests for a 2,193-line module, and tests/integration/test_controller.py holds 6,443 lines: split each by the behaviour it tests

**What happens.** Measured 2026-11-11 at `e084968ac`: `tests/integration/test_simulation_view.py` holds 12,232 lines and 307 test functions, for `src/anesthesia_sim/app/simulation_view.py` at 2,193 lines. `tests/integration/test_controller.py` holds 6,443 lines. `CLAUDE.md` § "What this project is" names "a file nobody wants to open" as one of the slow accumulations that could end the project. Open items already find that tests in the first file check hand-kept lists that miss cases (`PL-B8DL`, `PL-86VL`, `PL-0G2P`), and a file this long makes such a gap harder to see.

**Recommendation.** Split each file by the behaviour its tests check, moving tests without changing them, and keep shared fixtures in a `conftest.py` or a helper module. `PL-RF2S` is changing how the display is written and its tests, so split after it lands.
