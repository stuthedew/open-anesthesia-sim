---
id: PL-8YCC
title: docs/ARCHITECTURE.md § Tests says tests/unit/ tests the controller in isolation, but the controller's tests are in tests/integration/test_controller.py, and the section does not say that 78 of the 146 test files in tests/unit/ test repository tooling
priority: P3
effort: S
status: done
classes: docs
feature: unit-test-review
touches: docs/ARCHITECTURE.md
added: 2026-11-11
closed: 2026-11-11
pr: 2131
payoff: a contributor reading where tests go is sent to the right directory and told which standard each test file is held to
verify: grep -qF 'so its tests are in' docs/ARCHITECTURE.md
---

**Problem.** docs/ARCHITECTURE.md § Tests says tests/unit/ tests the controller in isolation, but the controller's tests are in tests/integration/test_controller.py, and the section does not say that 78 of the 146 test files in tests/unit/ test repository tooling

**What happens.** `docs/ARCHITECTURE.md` § "Tests (`tests/`)" describes `tests/unit/` as "tests of one module's behavior in isolation, such as a compartment, a validator, a parameter loader, the controller and the displayed-value formatters". No file in `tests/unit/` tests the controller: its tests are `tests/integration/test_controller.py` and `tests/integration/test_sevo_controller.py`. On 2026-11-11, 78 of the 146 test files in `tests/unit/` import no `anesthesia_sim` module and test `tools/`, the hooks or the workflows. The section does not mention them, so a contributor who opens the directory finds `test_gh_write_guard.py` beside `test_alveolar.py` with no explanation.

**Recommendation.** Correct the sentence. Separately, decide whether the tooling tests move to a directory of their own, such as `tests/tools/`. Before moving them, count what names `tests/unit/` paths: `tools/workflow_paths_check.py`, the CI split in `tests/conftest.py`, and the items' `verify:` commands.

**Why it matters.** `docs/ARCHITECTURE.md` is where a contributor learns which test tree a new test goes in. A sentence that names the controller as a unit-tested module sends that contributor to the wrong directory, and a directory that mixes simulator tests with tooling tests, unexplained, hides which standard each file is held to.

**Done when.** § "Tests (`tests/`)" no longer says that `tests/unit/` tests the controller, says where the controller's tests are, and says that about half of `tests/unit/` tests the repository's tooling and how a reader tells the two kinds apart.

**Decided while building (2026-11-11): the tooling tests stay in `tests/unit/`.** Moving 79 of the 147 files would change every path that names them: 46 open item briefs name a `tests/unit/` path, 27 items were in flight on other branches that day, and 145 files under `tests/unit/` changed on `main` in the month before, so the move would conflict with most open work. The split it would make visible is already decided by each file's imports, which `tools/workflow_paths_check.py` reads and the corrected sentence now explains. A move would buy a directory listing that shows the split, and nothing a check or a reader cannot already get.

**Generator check.** A one-off. The sentence went stale when the controller's tests were written as integration tests, and `PL-BLN0`, the open generator head for document sentences that restate the code, already covers that mechanism.
