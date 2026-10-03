---
id: PL-Y4NS
title: tests/unit/test_pr_title_check.py's two --discover tests read the real checkout's origin, because repo_slug comes from tools/open_pull_requests.py and the _git stub never reaches it, so both fail in any clone whose origin is not a GitHub URL
priority: P3
effort: S
status: done
classes: defect, test
feature: ci-cost
milestone: v0.5.21
touches: tests/unit/test_pr_title_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-09-28 triage pass
added: 2026-09-27
closed: 2026-10-01
pr: 1261
payoff: the PR-title tests pass in a clone whose origin is not GitHub, so timing runs in local clones stop reporting false failures
not-delegable: the fault shows only in a clone whose origin is not a GitHub URL, and every checkout the replay runs in has the GitHub origin, so no admitted command fails before the fix; the proof is both tests passing in a git clone --shared of the branch
---

**Problem.** tests/unit/test_pr_title_check.py's two --discover tests read the real checkout's origin, because repo_slug comes from tools/open_pull_requests.py and the _git stub never reaches it, so both fail in any clone whose origin is not a GitHub URL

**Observed 2026-09-27, by `PL-F08Y`.** Every timing run in a `git clone
--shared` of this checkout, whose `origin` is therefore a local path, failed
`test_a_stale_title_on_the_open_pull_request_fails_locally` (`main()` returned
0) and `test_a_discovered_title_that_leads_with_everything_passes` (it printed
nothing). Both pass in a checkout whose `origin` is the GitHub URL. The tests
replace `pr_title_check._git` with `_remote()`, which answers `remote get-url`
for them, but `main()`'s `--discover` branch calls `repo_slug()`, imported
from `tools/open_pull_requests.py`, which asks the real repository. With no
GitHub slug, `main()` skips silently and returns 0. The stub's own `remote
get-url` answer shows the tests meant the slug to come from it, so the fix is
most likely to stub `repo_slug` beside `_git`, or to route it through `_git`.
Any checkout whose `origin` is not a GitHub URL fails the same way: a local
clone, as here, or a mirror hosted elsewhere.

**Reproduced 2026-09-28** in a `git clone --shared` of this checkout: both
tests failed and 23 passed. The file's other two `--discover` tests already stub
`repo_slug` beside `_git`.

**Why it matters.** Any clone whose `origin` is not a GitHub URL - a local clone
for a timing run, a mirror - reports two false failures, which teaches a session
to read red as noise.

**Done when.** Both tests stub `repo_slug` as the file's other `--discover`
tests do, and pass in a clone whose `origin` is a local path.

**Generator check.** A one-off: two tests missing a stub the file's later tests
carry.

**Resolved 2026-10-01.** The helper `_remote(url, ...)` became
`_on_a_branch(monkeypatch, **refs)`, which stubs `repo_slug` beside `_git`; its
`remote get-url` arm went with it, because nothing in `tools/pr_title_check.py`
asks that since `PL-Q664`, and the dead arm is what made the stub look as if it
set the slug. A third test had the same gap and passed rather than failed:
`test_no_pull_request_to_read_is_a_silent_skip_that_never_reads_the_trees`
skipped on the missing slug before its stubbed lookup was called, so in such a
clone it asserted nothing about the path it names. It stubs `repo_slug` too.
In a `git clone --shared` with a local-path `origin`: 2 failed and 23 passed
before, 25 passed after.
