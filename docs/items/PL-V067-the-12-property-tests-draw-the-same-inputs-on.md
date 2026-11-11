---
id: PL-V067
title: The 12 property tests draw the same inputs on every run, the weekly shuffled run included, because each sets derandomize=True on its own decorator: no scheduled run gives them new inputs
status: untriaged
added: 2026-11-11
---

**Problem.** The 12 property tests draw the same inputs on every run, the weekly shuffled run included, because each sets derandomize=True on its own decorator: no scheduled run gives them new inputs

**What happens.** Every `@given` test sets `@settings(derandomize=True, database=None, ...)` on its own decorator: 12 tests in 8 files, four of them simulator files (`tests/unit/test_supported_range_edges.py`, `test_generated_runs.py`, `test_formatting.py` and `test_exponential_approach.py`). Hypothesis's documentation says of `derandomize`: "every run will test the same set of test cases until you update Hypothesis, Python, or the test function", and gives as its example "running quick deterministic tests on every commit, and a longer non-deterministic nightly testing run" (https://hypothesis.readthedocs.io/en/latest/reference/api.html, `settings.derandomize`, read 2026-11-11).

**Measured 2026-11-11**, Hypothesis 6.168.3 and pytest-randomly 5.0.0: a five-example probe test with the same decorator drew the same five values under `-p no:randomly`, under `-p randomly --randomly-seed=20261111`, under `--randomly-seed=20261118` and under `--hypothesis-seed=7`. So `drift.yml`'s weekly `order` job shuffles the test order and gives these tests no new inputs. Their inputs change only when Hypothesis, Python or the test function changes.

**Recommendation.** Keep every commit's run as it is. Move the settings from the decorators to two registered profiles in `tests/conftest.py`: the default one as now, and an exploring one with `derandomize=False` and more examples. Run the exploring profile in `drift.yml`'s weekly `order` job, and print the seed so that a failure reproduces with `--hypothesis-seed`. With the decorators as they are, `--hypothesis-seed=7` changed nothing in the probe, so check that the seed takes effect once the decorators stop setting `derandomize=True`.
