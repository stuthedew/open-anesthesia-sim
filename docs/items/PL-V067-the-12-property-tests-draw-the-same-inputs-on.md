---
id: PL-V067
title: The 12 property tests draw the same inputs on every run, the weekly shuffled run included, because each sets derandomize=True on its own decorator: no scheduled run gives them new inputs
priority: P2
effort: S
status: ready
classes: defect
feature: unit-test-review
touches: tests/hypothesis_profiles.py, conftest.py, tests/conftest.py, tests/unit/test_hypothesis_profiles.py, .github/workflows/drift.yml, tests/unit/test_generated_runs.py, tests/unit/test_supported_range_edges.py, tests/unit/test_formatting.py, tests/unit/test_exponential_approach.py, tests/unit/test_required_checks_reference.py, tests/unit/test_makefile_reference.py, subprojects/docket/tests/test_frontmatter_reference.py, subprojects/docket/tests/test_shell.py, ROADMAP.md
added: 2026-11-11
payoff: the property tests reach new inputs every week, while every pull request's run stays repeatable
verify: grep -q 'def test_no_property_test_sets_a_setting_that_the_profiles_decide' tests/unit/test_hypothesis_profiles.py
---

**Problem.** The 12 property tests draw the same inputs on every run, the weekly shuffled run included, because each sets derandomize=True on its own decorator: no scheduled run gives them new inputs

**What happens.** Every `@given` test sets `@settings(derandomize=True, database=None, ...)` on its own decorator: 12 tests in 8 files, four of them simulator files (`tests/unit/test_supported_range_edges.py`, `test_generated_runs.py`, `test_formatting.py` and `test_exponential_approach.py`). Hypothesis's documentation says of `derandomize`: "every run will test the same set of test cases until you update Hypothesis, Python, or the test function", and gives as its example "running quick deterministic tests on every commit, and a longer non-deterministic nightly testing run" (https://hypothesis.readthedocs.io/en/latest/reference/api.html, `settings.derandomize`, read 2026-11-11).

**Measured 2026-11-11**, Hypothesis 6.168.3 and pytest-randomly 5.0.0: a five-example probe test with the same decorator drew the same five values under `-p no:randomly`, under `-p randomly --randomly-seed=20261111`, under `--randomly-seed=20261118` and under `--hypothesis-seed=7`. So `drift.yml`'s weekly `order` job shuffles the test order and gives these tests no new inputs. Their inputs change only when Hypothesis, Python or the test function changes.

**Recommendation.** Keep every commit's run as it is. Move the settings from the decorators to two registered profiles in `tests/conftest.py`: the default one as now, and an exploring one with `derandomize=False` and more examples. Run the exploring profile in `drift.yml`'s weekly `order` job, and print the seed so that a failure reproduces with `--hypothesis-seed`. With the decorators as they are, `--hypothesis-seed=7` changed nothing in the probe, so check that the seed takes effect once the decorators stop setting `derandomize=True`.

**Why it matters.** A property test is worth more than a list of cases only because it can reach an input nobody thought to list. Drawing the same inputs forever turns each of these 12 tests into a fixed list of cases that nobody chose. Four of them hold simulator values a learner sees: the supported-range guards, the generated runs, the display formatting and the exponential step.

**Done when.** Every ordinary run still draws the same inputs, and `drift.yml`'s weekly `order` job draws new inputs from a seed its command line shows, so a failure there reproduces. A test fails when a property test's decorator sets a setting that the profiles decide.

**Decided while building (2026-11-11).** The two profiles live in `tests/hypothesis_profiles.py`, not in `tests/conftest.py`. The root `conftest.py` loads them for every run of both test trees, and `tests/conftest.py` loads them for the mutation run, whose copy of the tree has no root `conftest.py` (mutmut 3.8.0's default `also_copy` list, `mutmut/configuration.py`). Both profiles start from Hypothesis's built-in `ci` profile, so a session's run and CI's take the same settings. The exploring profile keeps each test's `max_examples` instead of raising it, so the weekly job takes no longer than before: each week's new draw is the gain, and 52 weeks give 52 times the inputs. The weekly job uses the date as Hypothesis's seed, as it already does for pytest-randomly.

**Measured after the change (2026-11-11)**, with a five-example probe test carrying only `@settings(max_examples=5)`: two ordinary runs drew the same five values; two runs with `--hypothesis-profile=exploring --hypothesis-seed=1` drew the same five values, which differed from the ordinary run's; `--hypothesis-seed=2` drew others again. Under `-p randomly --randomly-seed=11` and `=12`, the seed-1 run drew the seed-1 values, so pytest-randomly does not disturb the seed.

**Generator check.** A one-off. The fact misread was which run gives a property test new inputs: the weekly shuffled run was assumed to, and the decorators kept it from doing so. No other open item shares that mechanism, and the new test fails on the next decorator that sets a profile's setting.
