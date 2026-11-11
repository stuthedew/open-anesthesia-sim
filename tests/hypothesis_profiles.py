"""The two Hypothesis profiles that every property test runs under.

A property test is a test decorated with Hypothesis's `@given`, which draws
its inputs instead of listing them. The run's profile decides whether those
draws repeat:

- `repeatable` draws the same inputs on every run. Each test's inputs are
  seeded from the test function itself, so a failure reproduces with the same
  command, and a pull request's result does not depend on luck. Every run
  takes this profile unless it names another.
- `exploring` draws new inputs. `drift.yml`'s weekly `order` job runs it with
  `--hypothesis-profile=exploring --hypothesis-seed=<date>`, so each week
  tries inputs that no earlier run tried. A failure reproduces when the same
  command is run with the seed that the job's command line shows.

Hypothesis's documentation recommends this split: "running quick
deterministic tests on every commit, and a longer non-deterministic nightly
testing run" (`settings.derandomize`,
https://hypothesis.readthedocs.io/en/latest/reference/api.html). Until
`PL-V067`, each test set `derandomize=True` on its own decorator. A setting
on a decorator overrides the profile, so no run ever drew new inputs.

So a test's decorator sets only `max_examples`, the number of inputs it
draws, which is chosen for that test's cost. Both profiles keep that number,
so the weekly run takes no longer than an ordinary one.

Both profiles start from Hypothesis's built-in `ci` profile, which Hypothesis
loads by itself on a CI runner. It turns off the example database, a
directory that replays earlier failures on later runs, so a run's result never
depends on what ran before it on the same machine. It turns off the deadline
for each example, so a slow shared runner cannot fail a correct test. It also
prints a failing example's reproduction blob and does not stop a test whose
inputs are slow to generate. Starting from it gives a session's own run the
same settings as CI.

The root `conftest.py` and `tests/conftest.py` each call `register`. The
root one is loaded by every run of both test trees. `tests/conftest.py` is
there for the mutation run, whose copy of the tree holds `tests/` but not the
root `conftest.py`.
"""

from __future__ import annotations

from hypothesis import settings

#: The profile every run takes unless it names another.
REPEATABLE = "repeatable"

#: The profile that draws new inputs, for the weekly run.
EXPLORING = "exploring"


def register() -> None:
    """Register both profiles, and load `repeatable` unless `exploring` is already loaded.

    Hypothesis's pytest plugin loads a profile named by `--hypothesis-profile`
    after the first conftest files are imported. So this is called before
    that, and it never puts `repeatable` back over `exploring`.
    """
    ci = settings.get_profile("ci")
    settings.register_profile(REPEATABLE, ci, derandomize=True)
    settings.register_profile(EXPLORING, ci, derandomize=False)
    if settings.get_current_profile_name() != EXPLORING:
        settings.load_profile(REPEATABLE)
