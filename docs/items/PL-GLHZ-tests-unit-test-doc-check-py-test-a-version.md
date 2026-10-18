---
id: PL-GLHZ
title: tests/unit/test_doc_check.py::test_a_version_named_as_shipping_with_a_stale_version_file_is_excused failed once in CI (checks-part-2, run 39087297513, head cc7f135c, 2026-10-18 01:45Z) when its fixture's git commit --allow-empty exited 128, and passed on the next head and in one local run, so a fixture repository's git call fails intermittently in CI
priority: P3
effort: S
status: done
classes: infra, defect
touches: conftest.py, subprojects/docket/tests/test_git_isolation.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-18 triage pass
added: 2026-10-18
closed: 2026-10-18
pr: 1536
payoff: the next CI test that fails on a git or other subprocess call prints that program's own error, so it can be fixed instead of re-run as a flake
verify: grep -q 'def test_a_failed_subprocess_shows_its_output_in_the_report' subprojects/docket/tests/test_git_isolation.py
---

**Problem.** tests/unit/test_doc_check.py::test_a_version_named_as_shipping_with_a_stale_version_file_is_excused failed once in CI (checks-part-2, run 39087297513, head cc7f135c, 2026-10-18 01:45Z) when its fixture's git commit --allow-empty exited 128, and passed on the next head and in one local run, so a fixture repository's git call fails intermittently in CI

**Checked 2026-10-18.** The job log (job 117556440884) shows only
`CalledProcessError: ... returned non-zero exit status 128` for the fourth
`git commit` in the fixture repository, `the current baseline`. The fixture
passes `capture_output=True` and pytest does not print a `CalledProcessError`'s
captured streams, so git's own message, which names the cause, was thrown
away. The three earlier commits and two tags in the same repository had
succeeded. A scan of the 60 most recent failed `quality.yml` runs (2026-09-24
to 2026-10-18) found no other git failure in a test, so this is one occurrence,
not a pattern.

**Why it matters.** A red CI run costs a re-run and a session's attention.
The suite builds hundreds of real git repositories, and every fixture git call
discards its stderr the same way. So the next failure of this kind will be just
as undiagnosable, and the only available reading will be "a flake", which the
repository refuses as a root cause.

**Done when.** A test that fails because a subprocess exited non-zero shows
that subprocess's captured stderr and stdout in its failure report, for every
test in the suite, set once in the repository's root `conftest.py`, with a test
that pins it. The cause of this one failure stays unknown, and a recurrence is
filed with the message it then prints.

**Generator check.** One-off. The fact is "why a fixture's git call failed",
and no reader misread it: the message was never shown. It is not a member of
any head.
