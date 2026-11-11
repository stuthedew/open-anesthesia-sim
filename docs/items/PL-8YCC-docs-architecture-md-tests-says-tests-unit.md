---
id: PL-8YCC
title: docs/ARCHITECTURE.md § Tests says tests/unit/ tests the controller in isolation, but the controller's tests are in tests/integration/test_controller.py, and the section does not say that 78 of the 146 test files in tests/unit/ test repository tooling
status: untriaged
added: 2026-11-11
---

**Problem.** docs/ARCHITECTURE.md § Tests says tests/unit/ tests the controller in isolation, but the controller's tests are in tests/integration/test_controller.py, and the section does not say that 78 of the 146 test files in tests/unit/ test repository tooling

**What happens.** `docs/ARCHITECTURE.md` § "Tests (`tests/`)" describes `tests/unit/` as "tests of one module's behavior in isolation, such as a compartment, a validator, a parameter loader, the controller and the displayed-value formatters". No file in `tests/unit/` tests the controller: its tests are `tests/integration/test_controller.py` and `tests/integration/test_sevo_controller.py`. On 2026-11-11, 78 of the 146 test files in `tests/unit/` import no `anesthesia_sim` module and test `tools/`, the hooks or the workflows. The section does not mention them, so a contributor who opens the directory finds `test_gh_write_guard.py` beside `test_alveolar.py` with no explanation.

**Recommendation.** Correct the sentence. Separately, decide whether the tooling tests move to a directory of their own, such as `tests/tools/`. Before moving them, count what names `tests/unit/` paths: `tools/workflow_paths_check.py`, the CI split in `tests/conftest.py`, and the items' `verify:` commands.
